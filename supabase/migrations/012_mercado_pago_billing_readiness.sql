-- RENOVA Finanças • preparação do billing Mercado Pago
-- Objetivo: dar rastreabilidade ao checkout/assinatura e deixar o webhook idempotente.

alter table public.ai_subscription_plans
  add column if not exists provider_plan_id text,
  add column if not exists back_url text;

alter table public.ai_subscriptions
  add column if not exists external_reference text,
  add column if not exists init_point text,
  add column if not exists next_payment_at timestamptz,
  add column if not exists provider_status text,
  add column if not exists provider_status_detail text;

create index if not exists ai_subscriptions_plan_code_idx
  on public.ai_subscriptions(plan_code);

create unique index if not exists ai_subscriptions_provider_subscription_uidx
  on public.ai_subscriptions(provider, provider_subscription_id)
  where provider_subscription_id is not null;

create unique index if not exists ai_subscriptions_external_reference_uidx
  on public.ai_subscriptions(external_reference)
  where external_reference is not null;

create table if not exists public.subscription_checkout_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  plan_code text not null references public.ai_subscription_plans(code),
  provider text not null default 'mercado_pago',
  external_reference text not null unique,
  provider_plan_id text,
  provider_subscription_id text,
  payer_email text,
  init_point text,
  status text not null default 'created'
    check (status in ('created','redirected','pending','authorized','cancelled','expired','failed')),
  expires_at timestamptz,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists subscription_checkout_sessions_user_created_idx
  on public.subscription_checkout_sessions(user_id, created_at desc);

create unique index if not exists subscription_checkout_sessions_provider_subscription_uidx
  on public.subscription_checkout_sessions(provider, provider_subscription_id)
  where provider_subscription_id is not null;

alter table public.subscription_checkout_sessions enable row level security;

drop policy if exists "checkout_sessions_select_own_or_owner"
  on public.subscription_checkout_sessions;
create policy "checkout_sessions_select_own_or_owner"
on public.subscription_checkout_sessions
for select
to authenticated
using ((select auth.uid()) = user_id or (select private.is_owner()));

-- Criação/alteração de checkout deve ocorrer no backend (Edge Function/service role),
-- nunca diretamente pelo cliente Streamlit.
grant select on public.subscription_checkout_sessions to authenticated;

create table if not exists public.mercado_pago_webhook_events (
  id uuid primary key default gen_random_uuid(),
  event_key text not null unique,
  request_id text,
  event_type text,
  action text,
  resource_id text,
  live_mode boolean,
  signature_valid boolean not null default false,
  processing_status text not null default 'received'
    check (processing_status in ('received','processed','ignored','failed')),
  payload jsonb not null default '{}'::jsonb,
  error_message text,
  received_at timestamptz not null default now(),
  processed_at timestamptz
);

create index if not exists mercado_pago_webhook_events_resource_idx
  on public.mercado_pago_webhook_events(resource_id, received_at desc);

create index if not exists mercado_pago_webhook_events_status_idx
  on public.mercado_pago_webhook_events(processing_status, received_at desc);

alter table public.mercado_pago_webhook_events enable row level security;

drop policy if exists "mp_webhook_events_owner_read"
  on public.mercado_pago_webhook_events;
create policy "mp_webhook_events_owner_read"
on public.mercado_pago_webhook_events
for select
to authenticated
using ((select private.is_owner()));

grant select on public.mercado_pago_webhook_events to authenticated;

update public.ai_subscription_plans
set back_url = coalesce(back_url, 'https://minhas-financas-renova.streamlit.app/?assinatura=retorno'),
    updated_at = now()
where code = 'renova_ia';
