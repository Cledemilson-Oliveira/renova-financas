-- RENOVA Finanças
-- Contato do usuário + oferta RENOVA IA Personal + trava de preço por assinatura.

alter table public.profiles
  add column if not exists phone text;

alter table public.ai_subscription_plans
  add column if not exists reference_price numeric(12,2),
  add column if not exists promise text,
  add column if not exists price_lock_policy text;

alter table public.ai_subscriptions
  add column if not exists locked_price numeric(12,2);

update public.ai_subscription_plans
set name = 'RENOVA IA Personal',
    price = 9.90,
    reference_price = 29.90,
    promise = 'Sua IA financeira que aprende seu jeito de cuidar do dinheiro.',
    price_lock_policy = 'Quem assinar pelo preço de lançamento mantém R$ 9,90/mês enquanto a assinatura permanecer ativa.',
    updated_at = now()
where code = 'renova_ia';

create or replace function private.sync_auth_profile_contact()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  profile_name text;
  profile_phone text;
begin
  profile_name := nullif(trim(coalesce(new.raw_user_meta_data ->> 'full_name', '')), '');
  profile_phone := nullif(trim(coalesce(new.raw_user_meta_data ->> 'phone', '')), '');

  if profile_name is null and new.email is not null then
    profile_name := split_part(new.email, '@', 1);
  end if;

  insert into public.profiles (id, full_name, phone)
  values (new.id, profile_name, profile_phone)
  on conflict (id) do update
    set full_name = coalesce(excluded.full_name, public.profiles.full_name),
        phone = coalesce(excluded.phone, public.profiles.phone),
        updated_at = now();

  return new;
end;
$$;

drop trigger if exists renova_sync_auth_profile_contact on auth.users;
create trigger renova_sync_auth_profile_contact
after insert or update of raw_user_meta_data, email on auth.users
for each row execute function private.sync_auth_profile_contact();

create or replace function private.lock_ai_subscription_price()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  current_plan_price numeric(12,2);
begin
  if new.status = 'active'
     and (tg_op = 'INSERT' or old.status is distinct from 'active' or new.locked_price is null) then
    select price into current_plan_price
    from public.ai_subscription_plans
    where code = new.plan_code;

    new.locked_price := coalesce(current_plan_price, new.locked_price);
  end if;
  return new;
end;
$$;

drop trigger if exists renova_lock_ai_subscription_price on public.ai_subscriptions;
create trigger renova_lock_ai_subscription_price
before insert or update of status, plan_code on public.ai_subscriptions
for each row execute function private.lock_ai_subscription_price();
