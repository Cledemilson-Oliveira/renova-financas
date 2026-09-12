import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const reply = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });
const digits = (v: unknown) => String(v || "").replace(/\D/g, "");
const splitName = (v: unknown) => { const p = String(v || "").trim().split(/\s+/).filter(Boolean); return [p[0] || "Cliente", p.slice(1).join(" ") || "RENOVA"]; };

async function mp(path: string, token: string, init?: RequestInit) {
  const response = await fetch(`https://api.mercadopago.com${path}`, {
    ...init,
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...(init?.headers || {}) },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(String(data?.message || data?.error || `Mercado Pago HTTP ${response.status}`));
  return data;
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return reply({ error: "method_not_allowed" }, 405);

  const supabaseUrl = Deno.env.get("SUPABASE_URL") || "";
  const anonKey = Deno.env.get("SUPABASE_ANON_KEY") || "";
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
  const accessToken = Deno.env.get("MP_ACCESS_TOKEN") || "";
  const publicKey = Deno.env.get("MP_PUBLIC_KEY") || "";
  if (!supabaseUrl || !anonKey || !serviceKey) return reply({ error: "supabase_not_configured" }, 503);
  if (!accessToken) return reply({ error: "mercado_pago_not_configured", message: "MP_ACCESS_TOKEN ausente no backend." }, 503);

  const auth = req.headers.get("Authorization") || "";
  const userClient = createClient(supabaseUrl, anonKey, { global: { headers: { Authorization: auth } }, auth: { persistSession: false } });
  const { data: userData } = await userClient.auth.getUser();
  const user = userData?.user;
  if (!user?.id || !user.email) return reply({ error: "unauthorized" }, 401);

  const admin = createClient(supabaseUrl, serviceKey, { auth: { persistSession: false } });
  const body = await req.json().catch(() => ({}));
  const action = String(body?.action || "config").toLowerCase();
  const planCode = String(body?.plan_code || "renova_ia");
  const { data: plan } = await admin.from("ai_subscription_plans").select("code,name,price,currency,back_url,is_active").eq("code", planCode).eq("is_active", true).maybeSingle();
  if (!plan) return reply({ error: "plan_not_found" }, 404);

  const { data: existing } = await admin.from("ai_subscriptions").select("status,provider_subscription_id,current_period_end").eq("user_id", user.id).eq("plan_code", planCode).maybeSingle();
  if (existing?.status === "active") return reply({ status: "active", already_active: true, provider_subscription_id: existing.provider_subscription_id, current_period_end: existing.current_period_end });

  const price = Number(plan.price || 9.90);
  if (action === "config") return reply({ mode: "transparent", plan_code: planCode, plan_name: plan.name, price, currency: plan.currency || "BRL", public_key: publicKey || null, card_enabled: Boolean(publicKey), pix_enabled: true, boleto_enabled: true });

  const externalReference = `renova_ia:${user.id}:${crypto.randomUUID()}`;
  const mode = action === "card" ? "transparent_card_subscription" : action === "pix" ? "transparent_pix" : "transparent_boleto";
  const { data: checkout, error: checkoutError } = await admin.from("subscription_checkout_sessions").insert({
    user_id: user.id, plan_code: planCode, provider: "mercado_pago", external_reference: externalReference,
    payer_email: user.email, status: "created", metadata: { source: "renova_financas", mode },
  }).select("id").single();
  if (checkoutError || !checkout?.id) return reply({ error: "checkout_session_error", message: checkoutError?.message }, 500);

  const savePending = async (providerId: string, providerStatus: string, paymentMethod: string) => {
    const now = new Date().toISOString();
    const { error } = await admin.from("ai_subscriptions").upsert({
      user_id: user.id, plan_code: planCode, status: "pending", provider: "mercado_pago",
      provider_subscription_id: providerId || null, checkout_url: null, init_point: null,
      external_reference: externalReference, locked_price: price, provider_status: providerStatus,
      provider_status_detail: null, current_period_start: null, current_period_end: null, updated_at: now,
      metadata: { source: "renova_financas", mode, checkout_session_id: checkout.id, payment_method: paymentMethod, renewal_mode: action === "card" ? "automatic" : "manual" },
    }, { onConflict: "user_id,plan_code" });
    if (error) throw error;
  };

  try {
    if (action === "card") {
      if (!publicKey) return reply({ error: "public_key_not_configured", message: "MP_PUBLIC_KEY ausente no backend." }, 503);
      const cardToken = String(body?.card_token || body?.token || "").trim();
      if (!cardToken) return reply({ error: "card_token_required", message: "Token do cartão ausente." }, 400);
      const subscription = await mp("/preapproval", accessToken, { method: "POST", body: JSON.stringify({
        reason: String(plan.name || "RENOVA IA Personal"), external_reference: externalReference, payer_email: user.email,
        card_token_id: cardToken, auto_recurring: { frequency: 1, frequency_type: "months", transaction_amount: price, currency_id: String(plan.currency || "BRL") },
        back_url: String(plan.back_url || "https://minhas-financas-renova.streamlit.app/?assinatura=retorno"), status: "authorized",
      }) });
      const providerId = String(subscription?.id || "");
      const providerStatus = String(subscription?.status || "pending");
      if (!providerId) throw new Error("Mercado Pago não retornou o ID da assinatura.");
      await admin.from("subscription_checkout_sessions").update({ provider_subscription_id: providerId, status: providerStatus === "authorized" ? "authorized" : "pending", updated_at: new Date().toISOString(), metadata: { source: "renova_financas", mode, provider_status: providerStatus } }).eq("id", checkout.id);
      await savePending(providerId, providerStatus, String(body?.payment_method_id || "card"));
      return reply({ status: "pending_confirmation", provider_status: providerStatus, provider_subscription_id: providerId, message: "Assinatura criada. Aguardando confirmação automática do Mercado Pago." });
    }

    if (action === "pix") {
      const cpf = digits(body?.payer?.cpf || body?.cpf);
      if (cpf.length !== 11) return reply({ error: "invalid_cpf", message: "Informe um CPF válido." }, 400);
      const [firstName, lastName] = splitName(body?.payer?.name || user.user_metadata?.full_name);
      const payment = await mp("/v1/payments", accessToken, { method: "POST", headers: { "X-Idempotency-Key": crypto.randomUUID() }, body: JSON.stringify({
        transaction_amount: price, description: String(plan.name || "RENOVA IA Personal"), payment_method_id: "pix", external_reference: externalReference,
        notification_url: `${supabaseUrl}/functions/v1/mercado-pago-transparent-webhook`, payer: { email: user.email, first_name: firstName, last_name: lastName, identification: { type: "CPF", number: cpf } },
      }) });
      const paymentId = String(payment?.id || ""); const providerStatus = String(payment?.status || "pending"); const tx = payment?.point_of_interaction?.transaction_data || {};
      if (!paymentId) throw new Error("Mercado Pago não retornou o ID do Pix.");
      await admin.from("subscription_checkout_sessions").update({ provider_subscription_id: paymentId, status: providerStatus === "approved" ? "authorized" : "pending", updated_at: new Date().toISOString(), metadata: { source: "renova_financas", mode, payment_id: paymentId, provider_status: providerStatus } }).eq("id", checkout.id);
      await savePending(paymentId, providerStatus, "pix");
      return reply({ status: providerStatus, payment_id: paymentId, qr_code: String(tx?.qr_code || ""), qr_code_base64: String(tx?.qr_code_base64 || ""), ticket_url: String(tx?.ticket_url || ""), renewal_mode: "manual" });
    }

    if (action === "boleto") {
      const cpf = digits(body?.payer?.cpf || body?.cpf); const payer = body?.payer || {}; const address = payer?.address || {};
      if (cpf.length !== 11) return reply({ error: "invalid_cpf", message: "Informe um CPF válido." }, 400);
      const cleanAddress = { zip_code: digits(address?.zip_code), street_name: String(address?.street_name || "").trim(), street_number: String(address?.street_number || "").trim(), neighborhood: String(address?.neighborhood || "").trim(), city: String(address?.city || "").trim(), federal_unit: String(address?.state || address?.federal_unit || "").trim().toUpperCase() };
      if (!cleanAddress.zip_code || !cleanAddress.street_name || !cleanAddress.street_number || !cleanAddress.neighborhood || !cleanAddress.city || cleanAddress.federal_unit.length !== 2) return reply({ error: "invalid_address", message: "Preencha o endereço completo para gerar o boleto." }, 400);
      const [firstName, lastName] = splitName(payer?.name || user.user_metadata?.full_name); const expiration = new Date(); expiration.setUTCDate(expiration.getUTCDate() + 3);
      const payment = await mp("/v1/payments", accessToken, { method: "POST", headers: { "X-Idempotency-Key": crypto.randomUUID() }, body: JSON.stringify({
        transaction_amount: price, description: String(plan.name || "RENOVA IA Personal"), payment_method_id: "bolbradesco", date_of_expiration: expiration.toISOString(), external_reference: externalReference,
        notification_url: `${supabaseUrl}/functions/v1/mercado-pago-transparent-webhook`, payer: { email: user.email, first_name: firstName, last_name: lastName, identification: { type: "CPF", number: cpf }, address: cleanAddress },
      }) });
      const paymentId = String(payment?.id || ""); const providerStatus = String(payment?.status || "pending");
      if (!paymentId) throw new Error("Mercado Pago não retornou o ID do boleto.");
      await admin.from("subscription_checkout_sessions").update({ provider_subscription_id: paymentId, status: providerStatus === "approved" ? "authorized" : "pending", updated_at: new Date().toISOString(), metadata: { source: "renova_financas", mode, payment_id: paymentId, provider_status: providerStatus } }).eq("id", checkout.id);
      await savePending(paymentId, providerStatus, "bolbradesco");
      return reply({ status: providerStatus, payment_id: paymentId, ticket_url: String(payment?.transaction_details?.external_resource_url || payment?.point_of_interaction?.transaction_data?.ticket_url || ""), barcode: String(payment?.barcode?.content || payment?.point_of_interaction?.transaction_data?.barcode_content || ""), expiration: expiration.toISOString(), renewal_mode: "manual" });
    }

    return reply({ error: "unsupported_action" }, 400);
  } catch (error) {
    await admin.from("subscription_checkout_sessions").update({ status: "failed", updated_at: new Date().toISOString(), metadata: { source: "renova_financas", mode, error: error instanceof Error ? error.message : String(error) } }).eq("id", checkout.id);
    return reply({ error: "mercado_pago_error", message: error instanceof Error ? error.message : String(error) }, 502);
  }
});
