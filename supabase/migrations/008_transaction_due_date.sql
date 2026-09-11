-- RENOVA Finanças — vencimento de lançamentos
-- Permite diferenciar a data do lançamento da data real de vencimento
-- para análises de contas pendentes, próximas do vencimento e atrasadas.

alter table public.transactions
  add column if not exists due_date date;

create index if not exists transactions_user_status_due_date_idx
  on public.transactions (user_id, status, due_date)
  where due_date is not null;
