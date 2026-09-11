import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const jsonHeaders = { "Content-Type": "application/json" };

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: jsonHeaders });
}

function parseSignature(value: string) {
  const result: Record<string, string> = {};
  for (const part of value.split(",")) {
    const [key, ...rest] = part.trim().split("=");
    if (key && rest.length) result[key] = rest.join("=");
  }
  return result;
}

function constantTimeEqual(a: string, b: string) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i += 1) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

async function hmacHex(secret: string, message: string) {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(message));
  return Array.from(new Uint8Array(signature)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function validateWebhook(req: Request, dataId: string, secret: string) {
  const rawSignature = req.headers.get("x-signature") || "";
  const requestId = req.headers.get("x-request-id") || "";
  const parsed = parseSignature(rawSignature);
  const ts = parsed.ts || "";
  const v1 = parsed.v1 || "";
  if (!ts || !v1 || !requestId || !dataId) return false;
  const manifest = `id:${dataId};request-id:${requestId};ts:${ts};`;
  const expected = await hmacHex(secret, manifest);
  return constantTimeEqual(expected.toLowerCase(), v1.toLowerCase());
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

function checkoutStatus(providerStatus: string | null | undefined) {
  switch ((providerStatus || "").toLowerCase()) {
    case "authorized": return "authorized";
    case "cancelled": return "cancelled";
    case "pending": return "pending";
    case "paused": return "pending";
    default: return "pending";
  }
}

async function mpGet(path: string, accessToken: string) {
  const response = await fetch(`https://api.mercadopago.com${path}`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(String(payload?.message || payload?.error || `Mercado Pago HTTP ${response.status}`));
  }
  return payload;
}

function userIdFromExternalReference(value: string) {
  const match = /^renova_ia:([0-9a-fA-F-]{36}):/.exec(value || "");
  return match ? match[1] : "";
}

async function resolveUserId(admin: any, externalReference: string, providerSubscriptionId: string, payerEmail = "") {
  let userId = userIdFromExternalReference(externalReference);

  if (!userId && externalReference) {
    const { data: byRef } = await admin
      .from("subscription_checkout_sessions")
      .select("user_id")
      .eq("external_reference", externalReference)
      .maybeSingle();
    userId = String(byRef?.user_id || "");
  }

  if (!userId && providerSubscriptionId) {
    const { data: bySubscription } = await admin
      .from("ai_subscriptions")
      .select("user_id")
      .eq("provider", "mercado_pago")
      .eq("provider_subscription_id", providerSubscriptionId)
      .maybeSingle();
    userId = String(bySubscription?.user_id || "");
  }

  if (!userId && providerSubscriptionId) {
    const { data: byCheckout } = await admin
      .from("subscription_checkout_sessions")
      .select("user_id")
      .eq("provider", "mercado_pago")
      .eq("provider_subscription_id", providerSubscriptionId)
      .maybeSingle();
    userId = String(byCheckout?.user_id || "");
  }

  if (!userId && payerEmail) {
    const { data: accessRow } = await admin
      .from("user_access")
      .select("user_id")
      .ilike("email", payerEmail)
      .eq("status", "ativo")
      .limit(1)
      .maybeSingle();
    userId = String(accessRow?.user_id || "");
  }

  return userId;
}

async function syncSubscription(admin: any, subscription: any, eventKey: string, paymentInfo: any = null) {
  const providerSubscriptionId = String(subscription?.id || "");
  const providerStatus = String(subscription?.status || "pending");
  const externalReference = String(subscription?.external_reference || "");
  const payerEmail = String(subscription?.payer_email || subscription?.payer?.email || "");
  const checkoutUrl = String(subscription?.init_point || "");
  const nextPaymentAt = subscription?.next_payment_date || null;
  const statusDetail = subscription?.status_detail ? String(subscription.status_detail) : null;
  const mappedStatus = internalStatus(providerStatus);
  const now = new Date().toISOString();

  if (!providerSubscriptionId) throw new Error("Assinatura Mercado Pago sem identificador.");

  const userId = await resolveUserId(admin, externalReference, providerSubscriptionId, payerEmail);
  if (!userId) throw new Error("Não foi possível vincular a assinatura a um usuário RENOVA.");

  const { data: plan } = await admin
    .from("ai_subscription_plans")
    .select("price")
    .eq("code", "renova_ia")
    .maybeSingle();

  if (externalReference) {
    await admin
      .from("subscription_checkout_sessions")
      .update({
        provider_subscription_id: providerSubscriptionId,
        payer_email: payerEmail || null,
        init_point: checkoutUrl || null,
        status: checkoutStatus(providerStatus),
        updated_at: now,
        metadata: {
          provider_status: providerStatus,
          last_webhook_event: eventKey,
          last_payment: paymentInfo || null,
        },
      })
      .eq("external_reference", externalReference);
  }

  const approvedPayment = paymentInfo && String(paymentInfo.status || "").toLowerCase() === "approved";
  const subscriptionPayload: Record<string, unknown> = {
    user_id: userId,
    plan_code: "renova_ia",
    status: mappedStatus,
    provider: "mercado_pago",
    provider_subscription_id: providerSubscriptionId,
    checkout_url: checkoutUrl || null,
    init_point: checkoutUrl || null,
    external_reference: externalReference || null,
    locked_price: Number(plan?.price || 9.90),
    provider_status: providerStatus,
    provider_status_detail: statusDetail,
    next_payment_at: nextPaymentAt,
    started_at: mappedStatus === "active" ? now : null,
    cancelled_at: mappedStatus === "cancelled" ? now : null,
    last_payment_at: approvedPayment ? String(paymentInfo.date || now) : undefined,
    updated_at: now,
    metadata: {
      source: "mercado_pago_webhook",
      last_event_key: eventKey,
      last_payment: paymentInfo || null,
    },
  };

  Object.keys(subscriptionPayload).forEach((key) => {
    if (subscriptionPayload[key] === undefined) delete subscriptionPayload[key];
  });

  const { error: upsertError } = await admin
    .from("ai_subscriptions")
    .upsert(subscriptionPayload, { onConflict: "user_id,plan_code" });
  if (upsertError) throw upsertError;

  return { userId, mappedStatus };
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok");
  if (req.method !== "POST") return jsonResponse({ error: "method_not_allowed" }, 405);

  const supabaseUrl = Deno.env.get("SUPABASE_URL") || "";
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
  const accessToken = Deno.env.get("MP_ACCESS_TOKEN") || "";
  const webhookSecret = Deno.env.get("MP_WEBHOOK_SECRET") || "";
  if (!supabaseUrl || !serviceKey || !accessToken || !webhookSecret) {
    return jsonResponse({ error: "backend_not_configured" }, 503);
  }

  const url = new URL(req.url);
  const payload = await req.json().catch(() => ({}));
  const dataId = String(
    url.searchParams.get("data.id") ||
    url.searchParams.get("data_id") ||
    payload?.data?.id ||
    ""
  );
  const requestId = req.headers.get("x-request-id") || "";
  const eventType = String(payload?.type || url.searchParams.get("type") || "");
  const action = String(payload?.action || "");
  const notificationId = String(payload?.id || "");
  const eventKey = `mp:${notificationId || requestId || `${eventType}:${dataId}:${action}`}`;

  const admin = createClient(supabaseUrl, serviceKey, { auth: { persistSession: false } });
  const signatureValid = await validateWebhook(req, dataId, webhookSecret).catch(() => false);

  const { data: existingEvent } = await admin
    .from("mercado_pago_webhook_events")
    .select("id,processing_status")
    .eq("event_key", eventKey)
    .maybeSingle();
  if (existingEvent?.id) return jsonResponse({ ok: true, duplicate: true });

  const { data: eventRow, error: insertError } = await admin
    .from("mercado_pago_webhook_events")
    .insert({
      event_key: eventKey,
      request_id: requestId || null,
      event_type: eventType || null,
      action: action || null,
      resource_id: dataId || null,
      live_mode: typeof payload?.live_mode === "boolean" ? payload.live_mode : null,
      signature_valid: signatureValid,
      processing_status: "received",
      payload,
    })
    .select("id")
    .single();

  if (insertError || !eventRow?.id) return jsonResponse({ error: "event_log_error" }, 500);

  if (!signatureValid) {
    await admin
      .from("mercado_pago_webhook_events")
      .update({ processing_status: "failed", error_message: "invalid_signature", processed_at: new Date().toISOString() })
      .eq("id", eventRow.id);
    return jsonResponse({ error: "invalid_signature" }, 401);
  }

  try {
    if (!dataId) throw new Error("Notificação sem data.id.");

    let result: any = null;

    if (eventType === "subscription_preapproval") {
      const subscription = await mpGet(`/preapproval/${encodeURIComponent(dataId)}`, accessToken);
      result = await syncSubscription(admin, subscription, eventKey);
    } else if (eventType === "subscription_authorized_payment") {
      const invoice = await mpGet(`/authorized_payments/${encodeURIComponent(dataId)}`, accessToken);
      const preapprovalId = String(invoice?.preapproval_id || "");
      if (!preapprovalId) throw new Error("Fatura recorrente sem preapproval_id.");
      const subscription = await mpGet(`/preapproval/${encodeURIComponent(preapprovalId)}`, accessToken);
      const paymentInfo = {
        invoice_id: String(invoice?.id || dataId),
        payment_id: invoice?.payment?.id ? String(invoice.payment.id) : null,
        status: String(invoice?.payment?.status || invoice?.summarized || invoice?.status || ""),
        status_detail: invoice?.payment?.status_detail ? String(invoice.payment.status_detail) : null,
        date: invoice?.debit_date || invoice?.last_modified || new Date().toISOString(),
        amount: invoice?.transaction_amount ?? null,
      };
      result = await syncSubscription(admin, subscription, eventKey, paymentInfo);
    } else if (eventType === "payment") {
      const payment = await mpGet(`/v1/payments/${encodeURIComponent(dataId)}`, accessToken);
      const externalReference = String(payment?.external_reference || "");
      const userId = userIdFromExternalReference(externalReference);
      if (userId && String(payment?.status || "").toLowerCase() === "approved") {
        await admin
          .from("ai_subscriptions")
          .update({
            last_payment_at: payment?.date_approved || payment?.date_last_updated || new Date().toISOString(),
            provider_status_detail: payment?.status_detail ? String(payment.status_detail) : null,
            updated_at: new Date().toISOString(),
          })
          .eq("user_id", userId)
          .eq("plan_code", "renova_ia");
        result = { userId, payment_status: "approved" };
      } else {
        result = { ignored_payment: true, status: String(payment?.status || "") };
      }
    } else {
      await admin
        .from("mercado_pago_webhook_events")
        .update({ processing_status: "ignored", processed_at: new Date().toISOString() })
        .eq("id", eventRow.id);
      return jsonResponse({ ok: true, ignored: true, type: eventType });
    }

    await admin
      .from("mercado_pago_webhook_events")
      .update({ processing_status: "processed", processed_at: new Date().toISOString() })
      .eq("id", eventRow.id);

    return jsonResponse({ ok: true, type: eventType, result });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    await admin
      .from("mercado_pago_webhook_events")
      .update({ processing_status: "failed", error_message: message, processed_at: new Date().toISOString() })
      .eq("id", eventRow.id);
    return jsonResponse({ error: "processing_error", message }, 500);
  }
});
