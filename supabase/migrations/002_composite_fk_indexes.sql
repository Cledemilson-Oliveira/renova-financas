-- Índices de cobertura para FKs compostas multiusuário.
create index if not exists idx_transactions_account_user
  on public.transactions(account_id, user_id);
create index if not exists idx_transactions_destination_user
  on public.transactions(destination_account_id, user_id)
  where destination_account_id is not null;
create index if not exists idx_transactions_category_user
  on public.transactions(category_id, user_id)
  where category_id is not null;

create index if not exists idx_cards_account_user
  on public.cards(account_id, user_id)
  where account_id is not null;

create index if not exists idx_card_expenses_card_user
  on public.card_expenses(card_id, user_id);
create index if not exists idx_card_expenses_category_user
  on public.card_expenses(category_id, user_id)
  where category_id is not null;

create index if not exists idx_budgets_category_user
  on public.budgets(category_id, user_id);

create index if not exists idx_recurring_account_user
  on public.recurring_transactions(account_id, user_id);
create index if not exists idx_recurring_category_user
  on public.recurring_transactions(category_id, user_id)
  where category_id is not null;
