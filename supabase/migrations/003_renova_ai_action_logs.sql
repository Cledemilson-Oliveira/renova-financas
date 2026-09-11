-- RENOVA IA: audit trail for chat-driven financial actions
create table if not exists public.ai_action_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  command_text text not null,
  action_type text not null,
  action_payload jsonb not null default '{}'::jsonb,
  status text not null default 'executed'
    check (status in ('executed','pending_confirmation','confirmed','cancelled','failed','analysis')),
  result_message text,
  created_at timestamptz not null default now()
);

create index if not exists ai_action_logs_user_created_idx
  on public.ai_action_logs(user_id, created_at desc);

alter table public.ai_action_logs enable row level security;

drop policy if exists "ai_action_logs_select_own" on public.ai_action_logs;
create policy "ai_action_logs_select_own"
on public.ai_action_logs
for select
to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "ai_action_logs_insert_own" on public.ai_action_logs;
create policy "ai_action_logs_insert_own"
on public.ai_action_logs
for insert
to authenticated
with check ((select auth.uid()) = user_id);

grant select, insert on public.ai_action_logs to authenticated;
