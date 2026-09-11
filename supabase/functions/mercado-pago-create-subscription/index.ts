import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

function internalStatus(providerStatus: string | null | undefined) {
  switch ((providerStatus || "").toLowerCase()) {
    case "authorized": return "active";
    case "pending": return "pending";
    case "paused": return "past_due";
    case "cancelled": return "cancelled";
    default: return "pending";
  }
}

async function mercadoPago(path: string, accessToken: string, init?: RequestInit) {
  const response = await fetch(`https://api.mercadopago.com${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload?.message || payload?.error || `Mercado Pago HTTP ${response.status}`;
    throw new Error(String(message));
  }
  return payload;
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return jsonResponse({ error: "method_not_allowed" }, 405);

  const supabaseUrl = Deno.env.get("SUPABASE_URL") || "";
  const anonKey = Deno.env.get("SUPABASE_ANON_KEY") || "";
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
  const mpAccessToken = Deno.env.get("MP_ACCESS_TOKEN") || "";
  if (!supabaseUrl || !anonKey || !serviceKey) {
    return jsonResponse({ error: "supabase_not_configured" }, 503);
  }
  if (!mpAccessToken) {
    return jsonResponse({ error: "mercado_pago_not_configured", message: "MP_ACCESS_TOKEN ausente no backend." }, 503);
  }

  const authorization = req.headers.get("Authorization") || "";
  const userClient = createClient(supabaseUrl, anonKey, {
    global: { headers: { Authorization: authorization } },
    auth: { persistSession: false },
  });
  const { data: userData, error: userError } = await userClient.auth.getUser();
  const user = userData?.user;
  if (userError || !user?.id || !user.email) {
    return jsonResponse({ error: "unauthorized" }, 401);
  }

  const admin = createClient(supabaseUrl, serviceKey, { auth: { persistSession: false } });
  const body = await req.json().catch(() => ({}));
  const planCode = String(body?.plan_code || "renova_ia");

  const { data: plan, error: planError } = await admin
    .from("ai_subscription_plans")
    .select("code,name,price,currency,billing_cycle,provider,back_url,is_active")
    .eq("code", planCode)
    .eq("is_active", true)
    .maybeSingle();
  if (planError || !plan) return jsonResponse({ error: "plan_not_found" }, 404);

  const { data: existing } = await admin
    .from("ai_subscriptions")
    .select("id,status,provider_subscription_id,init_point,checkout_url,provider_status,current_period_end")
    .eq("user_id", user.id)
    .eq("plan_code", planCode)
    .maybeSingle();

  if (existing?.status === "active") {
    return jsonResponse({ status: "active", already_active: true, provider_subscription_id: existing.provider_subscription_id });
  }

  if (existing?.status === "pending" && (existing.init_point || existing.checkout_url)) {
    return jsonResponse({
      status: "pending",
      reused: true,
      checkout_url: existing.init_point || existing.checkout_url,
      provider_subscription_id: existing.provider_subscription_id,
    });
  }

  const externalReference = `renova_ia:${user.id}:${crypto.randomUUID()}`;
  const { data: checkoutRow, error: checkoutError } = await admin
    .from("subscription_checkout_sessions")
    .insert({
      user_id: user.id,
      plan_code: planCode,
      provider: "mercado_pago",
      external_reference: externalReference,
      payer_email: user.email,
      status: "created",
      metadata: { source: "renova_financas", mode: "pending_preapproval" },
    })
    .select("id")
    .single();
  if (checkoutError || !checkoutRow?.id) {
    return jsonResponse({ error: "checkout_session_error", message: checkoutError?.message }, 500);
  }

  try {
    const price = Number(plan.price);
    const mp = await mercadoPago("/preapproval", mpAccessToken, {
      method: "POST",
      body: JSON.stringify({
        reason: String(plan.name || "RENOVA IA Personal"),
        external_reference: externalReference,
        payer_email: user.email,
        auto_recurring: {
          frequency: 1,
          frequency_type: "months",
          transaction_amount: price,
          currency_id: String(plan.currency || "BRL"),
        },
        back_url: String(plan.back_url || "https://minhas-financas-renova.streamlit.app/?assinatura=retorno"),
        status: "pending",
      }),
    });

    const providerStatus = String(mp?.status || "pending");
    const checkoutUrl = String(mp?.init_point || "");
    const providerSubscriptionId = String(mp?.id || "");
    if (!providerSubscriptionId || !checkoutUrl) {
      throw new Error("Mercado Pago não retornou id/init_point da assinatura.");
    }

    await admin
      .from("subscription_checkout_sessions")
      .update({
        provider_subscription_id: providerSubscriptionId,
        init_point: checkoutUrl,
        status: providerStatus === "authorized" ? "authorized" : "pending",
        updated_at: new Date().toISOString(),
        metadata: { source: "renova_financas", mode: "pending_preapproval", mercado_pago: { status: providerStatus } },
      })
      .eq("id", checkoutRow.id);

    const now = new Date().toISOString();
    const subscriptionPayload = {
      user_id: user.id,
      plan_code: planCode,
      status: internalStatus(providerStatus),
      provider: "mercado_pago",
      provider_subscription_id: providerSubscriptionId,
      checkout_url: checkoutUrl,
      init_point: checkoutUrl,
      external_reference: externalReference,
      locked_price: price,
      provider_status: providerStatus,
      provider_status_detail: null,
      started_at: providerStatus === "authorized" ? now : null,
      updated_at: now,
      metadata: { source: "renova_financas", checkout_session_id: checkoutRow.id },
    };

    const { error: upsertError } = await admin
      .from("ai_subscriptions")
      .upsert(subscriptionPayload, { onConflict: "user_id,plan_code" });
    if (upsertError) throw upsertError;

    return jsonResponse({
      status: internalStatus(providerStatus),
      checkout_url: checkoutUrl,
      provider_subscription_id: providerSubscriptionId,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    await admin
      .from("subscription_checkout_sessions")
      .update({ status: "failed", updated_at: new Date().toISOString(), metadata: { error: message } })
      .eq("id", checkoutRow.id);
    return jsonResponse({ error: "mercado_pago_error", message }, 502);
  }
});
