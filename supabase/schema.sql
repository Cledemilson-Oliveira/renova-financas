-- RENOVA Finanças - schema V1
-- Projeto Supabase exclusivo do RENOVA Finanças.
-- Segurança: todas as tabelas públicas usam RLS por usuário e FKs compostas
-- para impedir referências cruzadas entre usuários.

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.accounts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  account_type text not null default 'conta',
  currency char(3) not null default 'BRL',
  initial_balance numeric(14,2) not null default 0,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (id, user_id)
);

create table public.categories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  kind text not null default 'despesa' check (kind in ('receita','despesa','ambos')),
  icon text,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (id, user_id),
  unique (user_id, name, kind)
);

create table public.transactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  account_id uuid not null,
  destination_account_id uuid,
  category_id uuid,
  kind text not null check (kind in ('receita','despesa','transferencia')),
  description text not null,
  amount numeric(14,2) not null check (amount > 0),
  occurred_on date not null default current_date,
  status text not null default 'pago' check (status in ('previsto','pago','atrasado','cancelado')),
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint transactions_account_owner_fk
    foreign key (account_id, user_id) references public.accounts(id, user_id) on delete restrict,
  constraint transactions_destination_owner_fk
    foreign key (destination_account_id, user_id) references public.accounts(id, user_id) on delete restrict,
  constraint transactions_category_owner_fk
    foreign key (category_id, user_id) references public.categories(id, user_id) on delete set null (category_id),
  constraint transactions_transfer_shape_ck check (
    (kind = 'transferencia' and destination_account_id is not null and destination_account_id <> account_id)
    or
    (kind <> 'transferencia' and destination_account_id is null)
  )
);

create table public.cards (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  account_id uuid,
  name text not null,
  credit_limit numeric(14,2) not null default 0 check (credit_limit >= 0),
  closing_day smallint check (closing_day between 1 and 31),
  due_day smallint check (due_day between 1 and 31),
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (id, user_id),
  constraint cards_account_owner_fk
    foreign key (account_id, user_id) references public.accounts(id, user_id) on delete set null (account_id)
);

create table public.card_expenses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  card_id uuid not null,
  category_id uuid,
  description text not null,
  amount numeric(14,2) not null check (amount > 0),
  purchase_date date not null default current_date,
  installments integer not null default 1 check (installments between 1 and 120),
  current_installment integer not null default 1 check (current_installment >= 1),
  status text not null default 'aberta' check (status in ('aberta','paga','cancelada')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint card_expenses_installment_ck check (current_installment <= installments),
  constraint card_expenses_card_owner_fk
    foreign key (card_id, user_id) references public.cards(id, user_id) on delete cascade,
  constraint card_expenses_category_owner_fk
    foreign key (category_id, user_id) references public.categories(id, user_id) on delete set null (category_id)
);

create table public.budgets (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  category_id uuid not null,
  month date not null,
  planned_amount numeric(14,2) not null check (planned_amount >= 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint budgets_month_first_day_ck check (month = date_trunc('month', month)::date),
  constraint budgets_category_owner_fk
    foreign key (category_id, user_id) references public.categories(id, user_id) on delete cascade,
  unique (user_id, category_id, month)
);

create table public.financial_goals (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  target_amount numeric(14,2) not null check (target_amount > 0),
  current_amount numeric(14,2) not null default 0 check (current_amount >= 0),
  target_date date,
  status text not null default 'ativa' check (status in ('ativa','concluida','pausada')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.recurring_transactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  account_id uuid not null,
  category_id uuid,
  kind text not null check (kind in ('receita','despesa')),
  description text not null,
  amount numeric(14,2) not null check (amount > 0),
  frequency text not null check (frequency in ('semanal','quinzenal','mensal','anual')),
  next_due_date date not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint recurring_account_owner_fk
    foreign key (account_id, user_id) references public.accounts(id, user_id) on delete cascade,
  constraint recurring_category_owner_fk
    foreign key (category_id, user_id) references public.categories(id, user_id) on delete set null (category_id)
);

create table public.financial_alerts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  severity text not null check (severity in ('info','atencao','urgente')),
  title text not null,
  message text not null,
  source text,
  is_read boolean not null default false,
  created_at timestamptz not null default now()
);

create index idx_accounts_user on public.accounts(user_id);
create index idx_categories_user on public.categories(user_id);
create index idx_transactions_user_date on public.transactions(user_id, occurred_on desc);
create index idx_transactions_account on public.transactions(account_id);
create index idx_transactions_destination_account on public.transactions(destination_account_id) where destination_account_id is not null;
create index idx_transactions_category on public.transactions(category_id) where category_id is not null;
create index idx_cards_user on public.cards(user_id);
create index idx_cards_account on public.cards(account_id) where account_id is not null;
create index idx_card_expenses_user_date on public.card_expenses(user_id, purchase_date desc);
create index idx_card_expenses_card on public.card_expenses(card_id);
create index idx_card_expenses_category on public.card_expenses(category_id) where category_id is not null;
create index idx_budgets_user_month on public.budgets(user_id, month);
create index idx_budgets_category on public.budgets(category_id);
create index idx_goals_user on public.financial_goals(user_id);
create index idx_recurring_user_due on public.recurring_transactions(user_id, next_due_date) where is_active;
create index idx_alerts_user_unread on public.financial_alerts(user_id, created_at desc) where not is_read;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
security invoker
set search_path = public
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger profiles_set_updated_at before update on public.profiles
for each row execute function public.set_updated_at();
create trigger accounts_set_updated_at before update on public.accounts
for each row execute function public.set_updated_at();
create trigger categories_set_updated_at before update on public.categories
for each row execute function public.set_updated_at();
create trigger transactions_set_updated_at before update on public.transactions
for each row execute function public.set_updated_at();
create trigger cards_set_updated_at before update on public.cards
for each row execute function public.set_updated_at();
create trigger card_expenses_set_updated_at before update on public.card_expenses
for each row execute function public.set_updated_at();
create trigger budgets_set_updated_at before update on public.budgets
for each row execute function public.set_updated_at();
create trigger goals_set_updated_at before update on public.financial_goals
for each row execute function public.set_updated_at();
create trigger recurring_set_updated_at before update on public.recurring_transactions
for each row execute function public.set_updated_at();

alter table public.profiles enable row level security;
alter table public.accounts enable row level security;
alter table public.categories enable row level security;
alter table public.transactions enable row level security;
alter table public.cards enable row level security;
alter table public.card_expenses enable row level security;
alter table public.budgets enable row level security;
alter table public.financial_goals enable row level security;
alter table public.recurring_transactions enable row level security;
alter table public.financial_alerts enable row level security;

grant select, insert, update, delete on public.profiles to authenticated;
grant select, insert, update, delete on public.accounts to authenticated;
grant select, insert, update, delete on public.categories to authenticated;
grant select, insert, update, delete on public.transactions to authenticated;
grant select, insert, update, delete on public.cards to authenticated;
grant select, insert, update, delete on public.card_expenses to authenticated;
grant select, insert, update, delete on public.budgets to authenticated;
grant select, insert, update, delete on public.financial_goals to authenticated;
grant select, insert, update, delete on public.recurring_transactions to authenticated;
grant select, insert, update, delete on public.financial_alerts to authenticated;

create policy profiles_select_own on public.profiles for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = id);
create policy profiles_insert_own on public.profiles for insert to authenticated
with check ((select auth.uid()) is not null and (select auth.uid()) = id);
create policy profiles_update_own on public.profiles for update to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = id)
with check ((select auth.uid()) is not null and (select auth.uid()) = id);
create policy profiles_delete_own on public.profiles for delete to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = id);

create policy accounts_select_own on public.accounts for select to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy accounts_insert_own on public.accounts for insert to authenticated with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy accounts_update_own on public.accounts for update to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id) with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy accounts_delete_own on public.accounts for delete to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create policy categories_select_own on public.categories for select to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy categories_insert_own on public.categories for insert to authenticated with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy categories_update_own on public.categories for update to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id) with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy categories_delete_own on public.categories for delete to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create policy transactions_select_own on public.transactions for select to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy transactions_insert_own on public.transactions for insert to authenticated with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy transactions_update_own on public.transactions for update to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id) with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy transactions_delete_own on public.transactions for delete to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create policy cards_select_own on public.cards for select to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy cards_insert_own on public.cards for insert to authenticated with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy cards_update_own on public.cards for update to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id) with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy cards_delete_own on public.cards for delete to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create policy card_expenses_select_own on public.card_expenses for select to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy card_expenses_insert_own on public.card_expenses for insert to authenticated with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy card_expenses_update_own on public.card_expenses for update to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id) with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy card_expenses_delete_own on public.card_expenses for delete to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create policy budgets_select_own on public.budgets for select to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy budgets_insert_own on public.budgets for insert to authenticated with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy budgets_update_own on public.budgets for update to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id) with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy budgets_delete_own on public.budgets for delete to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create policy goals_select_own on public.financial_goals for select to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy goals_insert_own on public.financial_goals for insert to authenticated with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy goals_update_own on public.financial_goals for update to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id) with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy goals_delete_own on public.financial_goals for delete to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create policy recurring_select_own on public.recurring_transactions for select to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy recurring_insert_own on public.recurring_transactions for insert to authenticated with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy recurring_update_own on public.recurring_transactions for update to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id) with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy recurring_delete_own on public.recurring_transactions for delete to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create policy alerts_select_own on public.financial_alerts for select to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy alerts_insert_own on public.financial_alerts for insert to authenticated with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy alerts_update_own on public.financial_alerts for update to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id) with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy alerts_delete_own on public.financial_alerts for delete to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
