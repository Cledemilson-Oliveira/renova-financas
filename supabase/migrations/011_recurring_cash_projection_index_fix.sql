-- Remove índice duplicado de recorrências e cobre a FK composta de transactions.
drop index if exists public.idx_recurring_user_active_next;

create index if not exists idx_transactions_recurring_owner
  on public.transactions(recurring_id, user_id)
  where recurring_id is not null;
