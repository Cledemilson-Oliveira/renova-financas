-- RENOVA IA subscription model (R$ 9,90/month via Mercado Pago)
create table if not exists public.ai_subscription_plans (
  code text primary key,
  name text not null,
  price numeric(10,2) not null,
  currency text not null default 'BRL',
  billing_cycle text not null default 'monthly',
  provider text not null default 'mercado_pago',
  checkout_url text,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

insert into public.ai_subscription_plans(code,name,price,currency,billing_cycle,provider,is_active)
values ('renova_ia','RENOVA IA',9.90,'BRL','monthly','mercado_pago',true)
on conflict (code) do update
set name=excluded.name, price=excluded.price, currency=excluded.currency,
    billing_cycle=excluded.billing_cycle, provider=excluded.provider, is_active=true,
    updated_at=now();

create table if not exists public.ai_subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  plan_code text not null references public.ai_subscription_plans(code),
  status text not null default 'inactive'
    check (status in ('inactive','pending','active','past_due','cancelled','expired')),
  provider text not null default 'mercado_pago',
  provider_subscription_id text,
  provider_customer_id text,
  checkout_url text,
  current_period_start timestamptz,
  current_period_end timestamptz,
  started_at timestamptz,
  cancelled_at timestamptz,
  last_payment_at timestamptz,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(user_id, plan_code)
);

create index if not exists ai_subscriptions_user_status_idx
  on public.ai_subscriptions(user_id,status);

alter table public.ai_subscription_plans enable row level security;
alter table public.ai_subscriptions enable row level security;

drop policy if exists "ai_plans_public_read" on public.ai_subscription_plans;
create policy "ai_plans_public_read"
on public.ai_subscription_plans for select
to anon, authenticated
using (is_active = true);

drop policy if exists "ai_subscriptions_select_own_or_owner" on public.ai_subscriptions;
create policy "ai_subscriptions_select_own_or_owner"
on public.ai_subscriptions for select
to authenticated
using ((select auth.uid()) = user_id or (select private.is_owner()));

drop policy if exists "ai_subscriptions_owner_global" on public.ai_subscriptions;
create policy "ai_subscriptions_owner_global"
on public.ai_subscriptions for all
to authenticated
using ((select private.is_owner()))
with check ((select private.is_owner()));

grant select on public.ai_subscription_plans to anon, authenticated;
grant select on public.ai_subscriptions to authenticated;
