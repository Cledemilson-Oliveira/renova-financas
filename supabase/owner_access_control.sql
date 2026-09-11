-- RENOVA Finanças — controle de acesso V2
-- Dono fixado por e-mail no primeiro cadastro correspondente.
-- Autorizações são armazenadas no banco, não em user_metadata.

create schema if not exists private;

create table if not exists private.owner_config (
  email text primary key,
  created_at timestamptz not null default now()
);

revoke all on table private.owner_config from public, anon, authenticated;

insert into private.owner_config (email)
values (lower('consultorcledemilsonoliveira@gmail.com'))
on conflict (email) do nothing;

create table if not exists public.user_access (
  user_id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  role text not null default 'usuario' check (role in ('dono', 'admin', 'usuario')),
  status text not null default 'ativo' check (status in ('ativo', 'suspenso')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index if not exists user_access_email_lower_uq
  on public.user_access (lower(email));
create index if not exists idx_user_access_role_status
  on public.user_access (role, status);

alter table public.user_access enable row level security;

grant select, update on public.user_access to authenticated;
revoke insert, delete on public.user_access from anon, authenticated;

create or replace function private.is_owner()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select coalesce(
    exists (
      select 1
      from public.user_access ua
      where ua.user_id = (select auth.uid())
        and ua.role = 'dono'
        and ua.status = 'ativo'
    ),
    false
  );
$$;

create or replace function private.has_active_access()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select coalesce(
    exists (
      select 1
      from public.user_access ua
      where ua.user_id = (select auth.uid())
        and ua.status = 'ativo'
    ),
    false
  );
$$;

revoke all on function private.is_owner() from public, anon;
revoke all on function private.has_active_access() from public, anon;
grant usage on schema private to authenticated;
grant execute on function private.is_owner() to authenticated;
grant execute on function private.has_active_access() to authenticated;

create policy user_access_select_own_or_owner
on public.user_access
for select
to authenticated
using (
  (select auth.uid()) = user_id
  or (select private.is_owner())
);

create policy user_access_update_by_owner
on public.user_access
for update
to authenticated
using (
  (select private.is_owner())
  and role <> 'dono'
  and user_id <> (select auth.uid())
)
with check (
  (select private.is_owner())
  and role <> 'dono'
  and user_id <> (select auth.uid())
);

create or replace function private.sync_auth_user_access()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  desired_role text := 'usuario';
begin
  if new.email is null then
    return new;
  end if;

  if tg_op = 'INSERT' and exists (
    select 1
    from private.owner_config oc
    where oc.email = lower(new.email)
  ) then
    desired_role := 'dono';
  end if;

  insert into public.user_access (user_id, email, role, status)
  values (new.id, lower(new.email), desired_role, 'ativo')
  on conflict (user_id) do update
    set email = excluded.email,
        updated_at = now();

  return new;
end;
$$;

revoke all on function private.sync_auth_user_access() from public, anon, authenticated;

drop trigger if exists renova_sync_auth_user_access on auth.users;
create trigger renova_sync_auth_user_access
after insert or update of email on auth.users
for each row execute function private.sync_auth_user_access();

-- Backfill de usuários que eventualmente já existam.
insert into public.user_access (user_id, email, role, status)
select
  u.id,
  lower(u.email),
  case
    when exists (
      select 1 from private.owner_config oc where oc.email = lower(u.email)
    ) then 'dono'
    else 'usuario'
  end,
  'ativo'
from auth.users u
where u.email is not null
on conflict (user_id) do update
  set email = excluded.email,
      updated_at = now();

-- Garante que o e-mail do dono sempre receba o papel de dono caso já exista.
update public.user_access ua
set role = 'dono',
    status = 'ativo',
    updated_at = now()
where ua.user_id in (
  select u.id
  from auth.users u
  join private.owner_config oc on oc.email = lower(u.email)
);

-- Bloqueio de dados financeiros quando o acesso estiver suspenso.
create policy accounts_require_active_access
on public.accounts as restrictive for all to authenticated
using ((select private.has_active_access()))
with check ((select private.has_active_access()));

create policy categories_require_active_access
on public.categories as restrictive for all to authenticated
using ((select private.has_active_access()))
with check ((select private.has_active_access()));

create policy transactions_require_active_access
on public.transactions as restrictive for all to authenticated
using ((select private.has_active_access()))
with check ((select private.has_active_access()));

create policy cards_require_active_access
on public.cards as restrictive for all to authenticated
using ((select private.has_active_access()))
with check ((select private.has_active_access()));

create policy card_expenses_require_active_access
on public.card_expenses as restrictive for all to authenticated
using ((select private.has_active_access()))
with check ((select private.has_active_access()));

create policy budgets_require_active_access
on public.budgets as restrictive for all to authenticated
using ((select private.has_active_access()))
with check ((select private.has_active_access()));

create policy goals_require_active_access
on public.financial_goals as restrictive for all to authenticated
using ((select private.has_active_access()))
with check ((select private.has_active_access()));

create policy recurring_require_active_access
on public.recurring_transactions as restrictive for all to authenticated
using ((select private.has_active_access()))
with check ((select private.has_active_access()));

create policy alerts_require_active_access
on public.financial_alerts as restrictive for all to authenticated
using ((select private.has_active_access()))
with check ((select private.has_active_access()));

drop trigger if exists user_access_set_updated_at on public.user_access;
create trigger user_access_set_updated_at
before update on public.user_access
for each row execute function public.set_updated_at();
