# RENOVA Finanças — preparação para assinaturas Mercado Pago

Data da revisão: 11/09/2026

## Estado encontrado

- O plano `renova_ia` já existe no Supabase com preço de **R$ 9,90/mês** e provedor `mercado_pago`.
- A tabela `ai_subscriptions` já controla acesso por status e período.
- O app já bloqueia a RENOVA IA Personal para quem não possui assinatura ativa.
- O campo `checkout_url` do plano ainda está vazio.
- Ainda não existem Edge Functions no projeto `renova-financas`.
- Ainda não existe assinatura registrada em `ai_subscriptions`.
- O token privado do Mercado Pago não deve ir para Streamlit/secrets públicos nem para o navegador. A criação e atualização da assinatura devem ocorrer no backend.

## Arquitetura definida

1. **Plano**
   - Criar um plano mensal no Mercado Pago via `POST /preapproval_plan`.
   - Persistir o ID recebido em `ai_subscription_plans.provider_plan_id`.

2. **Início do checkout**
   - O Streamlit chama uma Edge Function autenticada.
   - A função valida o usuário e o plano `renova_ia`.
   - Cria uma linha em `subscription_checkout_sessions` com uma `external_reference` única.
   - Cria a assinatura no Mercado Pago via `POST /preapproval`.
   - Salva `provider_subscription_id` e `init_point`.
   - Devolve somente o `init_point` ao app para redirecionamento.

3. **Webhook**
   - Uma Edge Function pública recebe notificações do Mercado Pago.
   - A origem deve ser validada pelo header `x-signature`/request id conforme documentação do Mercado Pago.
   - O evento é gravado em `mercado_pago_webhook_events` usando chave idempotente.
   - A função consulta o recurso no Mercado Pago antes de liberar acesso.
   - Atualiza `ai_subscriptions` com status, período, próxima cobrança e IDs do provedor.

4. **Liberação de acesso**
   - `authorized/active` -> acesso RENOVA IA Personal liberado.
   - `pending` -> acesso ainda não liberado.
   - `past_due/paused` -> acesso suspenso conforme regra de negócio.
   - `cancelled/expired` -> acesso removido ao fim do período aplicável.

## Banco preparado pela migration 012

A migration `012_mercado_pago_billing_readiness.sql` adiciona:

- `provider_plan_id` e `back_url` no cadastro do plano;
- rastreamento de `external_reference`, `init_point`, próxima cobrança e status do provedor na assinatura;
- índice de `plan_code`, corrigindo a ausência apontada pelo Advisor do Supabase;
- `subscription_checkout_sessions` para correlacionar usuário, plano e assinatura sem expor IDs sensíveis;
- `mercado_pago_webhook_events` para auditoria e idempotência dos webhooks.

## Pontos antes de produção

- Configurar o Access Token **somente** como segredo do backend/Edge Function.
- Configurar a chave secreta do webhook **somente** no backend.
- Criar o plano de assinatura de produção e registrar `provider_plan_id`.
- Criar/deploy da função `mercado-pago-create-subscription` com JWT obrigatório.
- Criar/deploy da função `mercado-pago-webhook` com validação própria de assinatura e sem JWT do usuário.
- Testar: checkout pendente, pagamento autorizado, recusa, cancelamento e reprocessamento do mesmo webhook.
- Confirmar que nenhuma chamada do cliente consegue gravar diretamente `ai_subscriptions` ou eventos de webhook.

## Auditoria adicional

- Supabase Security Advisor: proteção contra senhas vazadas está desativada; habilitar antes da abertura comercial é recomendado.
- Performance Advisor: existem políticas RLS permissivas duplicadas por causa do acesso global da conta dono. Não bloqueiam o lançamento, mas devem ser consolidadas em uma etapa de otimização.
- Índices ainda marcados como “unused” não devem ser removidos agora: o projeto é novo e ainda não acumulou carga suficiente para esse indicador ser conclusivo.

## Referências oficiais Mercado Pago

- Assinaturas: https://www.mercadopago.com.br/developers/pt/reference/online-payments/subscriptions/overview
- Criar plano: https://www.mercadopago.com.br/developers/pt/reference/online-payments/subscriptions/create-preapproval-plan/post
- Criar assinatura: https://www.mercadopago.com.br/developers/pt/reference/online-payments/subscriptions/create-preapproval/post
- Notificações de assinaturas: https://www.mercadopago.com.br/developers/pt/docs/subscriptions/additional-content/your-integrations/notifications
