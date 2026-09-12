import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const reply = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
const parseSig = (v: string) => Object.fromEntries(v.split(",").map(x => x.trim().split("=")).filter(x => x.length === 2));
async function hmac(secret: string, value: string) { const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]); const s = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(value)); return Array.from(new Uint8Array(s)).map(b => b.toString(16).padStart(2, "0")).join(""); }
async function valid(req: Request, id: string, secret: string) { const sig = parseSig(req.headers.get("x-signature") || ""); const requestId = req.headers.get("x-request-id") || ""; if (!sig.ts || !sig.v1 || !requestId || !id) return false; return (await hmac(secret, `id:${id};request-id:${requestId};ts:${sig.ts};`)).toLowerCase() === String(sig.v1).toLowerCase(); }
const userIdFromRef = (v: string) => (/^renova_ia:([0-9a-fA-F-]{36}):/.exec(v || "") || [])[1] || "";
const addMonth = (v: string) => { const d = new Date(v); d.setUTCMonth(d.getUTCMonth() + 1); return d.toISOString(); };

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") return reply({ error: "method_not_allowed" }, 405);
  const supabaseUrl = Deno.env.get("SUPABASE_URL") || ""; const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || ""; const accessToken = Deno.env.get("MP_ACCESS_TOKEN") || ""; const secret = Deno.env.get("MP_WEBHOOK_SECRET") || "";
  if (!supabaseUrl || !serviceKey || !accessToken || !secret) return reply({ error: "backend_not_configured" }, 503);
  const url = new URL(req.url); const payload = await req.json().catch(() => ({})); const dataId = String(url.searchParams.get("data.id") || url.searchParams.get("data_id") || payload?.data?.id || "");
  if (!dataId) return reply({ error: "missing_data_id" }, 400);
  if (!(await valid(req, dataId, secret).catch(() => false))) return reply({ error: "invalid_signature" }, 401);
  const eventType = String(payload?.type || url.searchParams.get("type") || ""); if (eventType && eventType !== "payment") return reply({ ok: true, ignored: true, type: eventType });

  const response = await fetch(`https://api.mercadopago.com/v1/payments/${encodeURIComponent(dataId)}`, { headers: { Authorization: `Bearer ${accessToken}` } });
  const payment = await response.json().catch(() => ({})); if (!response.ok) return reply({ error: "payment_lookup_failed" }, 502);
  const externalReference = String(payment?.external_reference || ""); const userId = userIdFromRef(externalReference); if (!userId) return reply({ ok: true, ignored: true, reason: "foreign_payment" });

  const admin = createClient(supabaseUrl, serviceKey, { auth: { persistSession: false } });
  const { data: checkout } = await admin.from("subscription_checkout_sessions").select("id,plan_code,metadata").eq("external_reference", externalReference).maybeSingle();
  if (!checkout?.id) return reply({ ok: true, ignored: true, reason: "checkout_not_found" });

  const status = String(payment?.status || "pending").toLowerCase(); const approvedAt = String(payment?.date_approved || payment?.date_last_updated || new Date().toISOString());
  const subscriptionStatus = status === "approved" ? "active" : ["rejected","cancelled","refunded","charged_back"].includes(status) ? "cancelled" : "pending";
  const checkoutStatus = status === "approved" ? "authorized" : status === "cancelled" ? "cancelled" : ["rejected","refunded","charged_back"].includes(status) ? "failed" : "pending";
  const { data: plan } = await admin.from("ai_subscription_plans").select("price").eq("code", checkout.plan_code || "renova_ia").maybeSingle(); const now = new Date().toISOString();

  await admin.from("subscription_checkout_sessions").update({ provider_subscription_id: String(payment.id), status: checkoutStatus, updated_at: now, metadata: { ...(checkout.metadata || {}), provider_status: status, provider_status_detail: payment?.status_detail || null, payment_id: String(payment.id) } }).eq("id", checkout.id);
  const { error } = await admin.from("ai_subscriptions").upsert({
    user_id: userId, plan_code: checkout.plan_code || "renova_ia", status: subscriptionStatus, provider: "mercado_pago", provider_subscription_id: String(payment.id), checkout_url: null, init_point: null,
    external_reference: externalReference, locked_price: Number(plan?.price || payment?.transaction_amount || 9.90), provider_status: status, provider_status_detail: payment?.status_detail || null,
    current_period_start: subscriptionStatus === "active" ? approvedAt : null, current_period_end: subscriptionStatus === "active" ? addMonth(approvedAt) : null,
    started_at: subscriptionStatus === "active" ? approvedAt : null, cancelled_at: subscriptionStatus === "cancelled" ? now : null, last_payment_at: subscriptionStatus === "active" ? approvedAt : null, updated_at: now,
    metadata: { source: "mercado_pago_transparent_webhook", mode: checkout?.metadata?.mode || "transparent_payment", renewal_mode: "manual", payment_method: String(payment?.payment_method_id || ""), payment_id: String(payment.id) },
  }, { onConflict: "user_id,plan_code" });
  if (error) return reply({ error: "subscription_update_failed", message: error.message }, 500);
  return reply({ ok: true, payment_status: status, subscription_status: subscriptionStatus });
});
