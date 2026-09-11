# RENOVA Finanças — assinaturas Mercado Pago

Data da revisão: 11/09/2026

## Estado atual

- O plano interno `renova_ia` existe no Supabase por **R$ 9,90/mês** com provedor `mercado_pago`.
- O checkout interno aponta para `Checkout_Assinatura`, dentro do próprio RENOVA Finanças.
- A tabela `ai_subscriptions` controla acesso, status e dados do provedor.
- `subscription_checkout_sessions` correlaciona usuário RENOVA e assinatura Mercado Pago por `external_reference` única.
- `mercado_pago_webhook_events` registra notificações com chave idempotente para evitar processamento duplicado.
- A Edge Function autenticada `mercado-pago-create-subscription` está implantada.
- A Edge Function pública `mercado-pago-webhook` está implantada com validação HMAC própria.
- O código-fonte das duas Edge Functions está versionado em `supabase/functions/`.
- O app já possui a página autenticada `pages/Checkout_Assinatura.py`.
- O token privado do Mercado Pago nunca deve ir para o navegador, GitHub ou Streamlit público.

## Fluxo definido

1. **Usuário escolhe RENOVA IA Personalizada**
   - O CTA navega internamente para `Checkout_Assinatura`.
   - O usuário precisa estar autenticado.

2. **Criação da assinatura**
   - A página chama `mercado-pago-create-subscription` com o JWT Supabase do usuário.
   - A função valida usuário e plano `renova_ia`.
   - Cria uma `external_reference` no formato `renova_ia:<user_id>:<uuid>`.
   - Cria a assinatura diretamente em `POST /preapproval`, sem plano Mercado Pago associado.
   - A assinatura nasce como `pending`, permitindo que o Mercado Pago apresente o checkout para o assinante configurar o meio de pagamento.
   - O `id` e o `init_point` retornados são salvos no Supabase.

3. **Webhook**
   - Endpoint: `https://ysxttnnkuyhzvkjheqfy.supabase.co/functions/v1/mercado-pago-webhook`.
   - A função valida `x-signature`, `x-request-id` e `data.id` com HMAC-SHA256.
   - Cada evento é registrado antes do processamento.
   - Eventos duplicados são ignorados com segurança.
   - `subscription_preapproval` consulta `/preapproval/{id}` e sincroniza o estado da assinatura.
   - `subscription_authorized_payment` consulta `/authorized_payments/{id}` e atualiza também a última cobrança.
   - `payment` consulta `/v1/payments/{id}` e registra pagamentos aprovados quando há vínculo RENOVA identificável.

4. **Liberação de acesso**
   - Mercado Pago `authorized` -> RENOVA `active`: libera IA Personalizada.
   - `pending` -> mantém acesso Premium bloqueado.
   - `paused` -> RENOVA `past_due`.
   - `cancelled` -> RENOVA `cancelled`.

## Banco

A preparação de billing adicionou:

- `provider_plan_id` e `back_url` no cadastro do plano;
- `external_reference`, `init_point`, próxima cobrança e status do provedor em `ai_subscriptions`;
- índice de `plan_code`;
- `subscription_checkout_sessions`;
- `mercado_pago_webhook_events`.

O campo `provider_plan_id` permanece opcional porque o fluxo atual usa **assinatura sem plano Mercado Pago associado**, mantendo uma referência única por usuário RENOVA.

## Únicos passos externos restantes para produção

1. No projeto Supabase `renova-financas`, cadastrar como segredos das Edge Functions:
   - `MP_ACCESS_TOKEN` = Access Token de produção do Mercado Pago.
   - `MP_WEBHOOK_SECRET` = chave secreta gerada ao configurar o webhook no Mercado Pago.
2. No Mercado Pago, cadastrar o webhook acima e habilitar pelo menos os tópicos:
   - `subscription_preapproval`;
   - `subscription_authorized_payment`;
   - `payment`.
3. Executar um teste real controlado do ciclo:
   - iniciar checkout;
   - concluir meio de pagamento;
   - confirmar webhook válido;
   - verificar `ai_subscriptions.status = active`;
   - confirmar liberação da RENOVA IA Personalizada;
   - validar cancelamento e nova cobrança.

## Auditoria adicional

- Supabase Security Advisor: proteção contra senhas vazadas está desativada; habilitar antes da abertura comercial é recomendado.
- Existem políticas RLS permissivas duplicadas por causa do acesso global da conta dono. Não bloqueiam o checkout, mas devem ser consolidadas em uma etapa posterior de otimização.
- Índices marcados como `unused` não devem ser removidos agora: o projeto ainda é novo e não acumulou carga suficiente para esse indicador ser conclusivo.

## Referências oficiais Mercado Pago

- Assinaturas: https://www.mercadopago.com.br/developers/pt/reference/online-payments/subscriptions/overview
- Criar assinatura: https://www.mercadopago.com.br/developers/pt/reference/online-payments/subscriptions/create-preapproval/post
- Obter fatura recorrente: https://www.mercadopago.com.br/developers/pt/reference/online-payments/subscriptions/get-authorized-payment/get
- Webhooks: https://www.mercadopago.com.br/developers/pt/docs/subscriptions/additional-content/your-integrations/notifications
