# Publicação — RENOVA Finanças no Streamlit Community Cloud

## Aplicação

- Repositório: `Cledemilson-Oliveira/renova-financas`
- Branch: `main`
- Arquivo principal: `app.py`
- Python: `3.12`
- Sugestão de subdomínio: `renova-financas`

## Secrets

No Streamlit Community Cloud, abra **Advanced settings > Secrets** e cole:

```toml
SUPABASE_URL = "https://ysxttnnkuyhzvkjheqfy.supabase.co"
SUPABASE_PUBLISHABLE_KEY = "sb_publishable_ExcRQAHpToigI3WDwv3tew_ONpV9Xls"
```

A chave acima é uma chave publicável do Supabase. Nunca adicionar `sb_secret_...` ou `service_role` ao código ou ao Streamlit Secrets usado pelo frontend.

## Passo a passo

1. Acesse `share.streamlit.io` e conecte sua conta GitHub.
2. Se o repositório privado não aparecer, autorize o Streamlit a acessar repositórios privados.
3. Clique em **Create app**.
4. Selecione **Yup, I have an app**.
5. Informe o repositório `Cledemilson-Oliveira/renova-financas`.
6. Branch: `main`.
7. Main file path: `app.py`.
8. Abra **Advanced settings**.
9. Python version: `3.12`.
10. Cole os Secrets acima.
11. Salve e clique em **Deploy**.

## Teste após publicar

1. Abra o app publicado.
2. Crie um usuário com e-mail e senha.
3. Faça login.
4. Crie uma conta financeira.
5. Registre uma receita e uma despesa.
6. Confira se Dashboard, Contas e Lançamentos refletem os dados.
7. No Supabase, confirme que os registros foram gravados para o mesmo `user_id`.

## Observação sobre privacidade

O repositório está privado. O Streamlit Community Cloud pode exigir permissão adicional para acessar repositórios privados. Caso a conta já tenha atingido o limite de aplicativos privados do plano, será necessário ajustar a visibilidade do app ou o plano antes de concluir a publicação.
