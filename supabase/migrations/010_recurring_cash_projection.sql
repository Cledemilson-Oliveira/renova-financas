-- RENOVA Finanças
-- Contas/receitas fixas mensais, parcelamentos e metadados para projeção de caixa.

alter table public.recurring_transactions
  add column if not exists schedule_type text not null default 'mensal_fixa',
  add column if not exists start_date date,
  add column if not exists due_day smallint,
  add column if not exists total_amount numeric(14,2),
  add column if not exists total_installments integer,
  add column if not exists generated_installments integer not null default 0,
  add column if not exists end_date date,
  add column if not exists notes text;

update public.recurring_transactions
set start_date = coalesce(start_date, next_due_date),
    due_day = coalesce(due_day, extract(day from next_due_date)::smallint)
where start_date is null or due_day is null;

do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conname = 'recurring_schedule_type_ck'
      and conrelid = 'public.recurring_transactions'::regclass
  ) then
    alter table public.recurring_transactions
      add constraint recurring_schedule_type_ck
      check (schedule_type in ('mensal_fixa','parcelada'));
  end if;

  if not exists (
    select 1 from pg_constraint
    where conname = 'recurring_due_day_ck'
      and conrelid = 'public.recurring_transactions'::regclass
  ) then
    alter table public.recurring_transactions
      add constraint recurring_due_day_ck
      check (due_day is null or due_day between 1 and 31);
  end if;

  if not exists (
    select 1 from pg_constraint
    where conname = 'recurring_installments_ck'
      and conrelid = 'public.recurring_transactions'::regclass
  ) then
    alter table public.recurring_transactions
      add constraint recurring_installments_ck
      check (
        (schedule_type = 'mensal_fixa' and total_installments is null)
        or
        (schedule_type = 'parcelada' and total_installments between 1 and 360)
      );
  end if;

  if not exists (
    select 1 from pg_constraint
    where conname = 'recurring_generated_installments_ck'
      and conrelid = 'public.recurring_transactions'::regclass
  ) then
    alter table public.recurring_transactions
      add constraint recurring_generated_installments_ck
      check (
        generated_installments >= 0
        and (total_installments is null or generated_installments <= total_installments)
      );
  end if;

  if not exists (
    select 1 from pg_constraint
    where conname = 'recurring_total_amount_ck'
      and conrelid = 'public.recurring_transactions'::regclass
  ) then
    alter table public.recurring_transactions
      add constraint recurring_total_amount_ck
      check (total_amount is null or total_amount > 0);
  end if;

  if not exists (
    select 1 from pg_constraint
    where conname = 'recurring_id_user_unique'
      and conrelid = 'public.recurring_transactions'::regclass
  ) then
    alter table public.recurring_transactions
      add constraint recurring_id_user_unique unique (id, user_id);
  end if;
end $$;

alter table public.transactions
  add column if not exists recurring_id uuid,
  add column if not exists installment_number integer,
  add column if not exists installment_total integer;

do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conname = 'transactions_recurring_owner_fk'
      and conrelid = 'public.transactions'::regclass
  ) then
    alter table public.transactions
      add constraint transactions_recurring_owner_fk
      foreign key (recurring_id, user_id)
      references public.recurring_transactions(id, user_id)
      on delete set null (recurring_id);
  end if;

  if not exists (
    select 1 from pg_constraint
    where conname = 'transactions_installment_shape_ck'
      and conrelid = 'public.transactions'::regclass
  ) then
    alter table public.transactions
      add constraint transactions_installment_shape_ck
      check (
        (installment_number is null and installment_total is null)
        or
        (
          installment_number is not null
          and installment_total is not null
          and installment_number between 1 and installment_total
          and installment_total between 1 and 360
        )
      );
  end if;
end $$;

create index if not exists idx_recurring_user_active_next
  on public.recurring_transactions(user_id, next_due_date)
  where is_active;

create index if not exists idx_transactions_recurring
  on public.transactions(recurring_id)
  where recurring_id is not null;

create unique index if not exists uq_transactions_recurring_due
  on public.transactions(user_id, recurring_id, due_date)
  where recurring_id is not null and due_date is not null;
