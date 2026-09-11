-- Owner global access for RENOVA Finanças.
-- Normal users remain restricted by their existing own-row RLS policies.
do $$
declare
  t text;
begin
  foreach t in array array[
    'profiles','accounts','categories','transactions','cards','card_expenses',
    'budgets','financial_goals','recurring_transactions','financial_alerts',
    'ai_action_logs','ai_user_preferences'
  ]
  loop
    execute format('drop policy if exists %I on public.%I', t || '_owner_global_access', t);
    execute format(
      'create policy %I on public.%I for all to authenticated using ((select private.is_owner())) with check ((select private.is_owner()))',
      t || '_owner_global_access', t
    );
  end loop;
end $$;
