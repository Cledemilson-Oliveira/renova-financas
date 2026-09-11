-- RENOVA Finanças • Treinamento personalizado da IA
-- Cada usuário mantém sua própria base de conhecimento. O conteúdo não altera
-- pesos do modelo: ele funciona como memória operacional e regras personalizadas.

create table if not exists public.ai_training_items (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null check (char_length(trim(title)) between 1 and 120),
  area text not null default 'geral'
    check (area in ('geral','pessoal','negocio','financeiro','rotina','vendas','clientes','preferencias','regras')),
  kind text not null default 'conhecimento'
    check (kind in ('conhecimento','regra','preferencia','vocabulario','objetivo')),
  content text not null check (char_length(trim(content)) between 1 and 10000),
  application_mode text not null default 'quando_relevante'
    check (application_mode in ('sempre','quando_relevante','somente_consulta')),
  keywords text[] not null default '{}'::text[],
  structured_rule jsonb not null default '{}'::jsonb,
  priority smallint not null default 50 check (priority between 0 and 100),
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists ai_training_items_user_active_priority_idx
  on public.ai_training_items(user_id, is_active, priority desc, updated_at desc);

create index if not exists ai_training_items_keywords_gin_idx
  on public.ai_training_items using gin(keywords);

alter table public.ai_training_items enable row level security;

drop policy if exists "ai_training_select_own" on public.ai_training_items;
create policy "ai_training_select_own"
on public.ai_training_items for select
to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "ai_training_insert_own" on public.ai_training_items;
create policy "ai_training_insert_own"
on public.ai_training_items for insert
to authenticated
with check ((select auth.uid()) = user_id);

drop policy if exists "ai_training_update_own" on public.ai_training_items;
create policy "ai_training_update_own"
on public.ai_training_items for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

drop policy if exists "ai_training_delete_own" on public.ai_training_items;
create policy "ai_training_delete_own"
on public.ai_training_items for delete
to authenticated
using ((select auth.uid()) = user_id);

grant select, insert, update, delete on public.ai_training_items to authenticated;
