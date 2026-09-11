# RENOVA Finanças

Aplicativo separado de gestão financeira com identidade visual RENOVA.

## Stack

- Streamlit
- Supabase (Auth + Postgres + RLS)
- GitHub
- Plotly

## V1 já estruturada

- Dashboard financeiro
- Receitas e despesas
- Contas
- Cartões
- Orçamentos por categoria
- Análises e gráficos
- Relatórios com exportação CSV
- RENOVA IA Financeira com alertas iniciais
- Tema responsivo RENOVA
- Cliente Supabase preparado para chave publicável
- Schema SQL com RLS por usuário

## Identidade visual

- Fundo principal: `#0B0B0C`
- Superfície: `#111111`
- Destaque RENOVA: `#FFD75A`
- Dourado secundário: `#D9A520`
- Texto principal: `#F5F5F5`
- Texto secundário: `#CFCFCF`

## Rodar localmente

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Sem Supabase configurado, a aplicação abre em modo demonstração.

## Configurar Supabase

No Streamlit Cloud, adicione em **App settings > Secrets**:

```toml
SUPABASE_URL = "https://SEU-PROJETO.supabase.co"
SUPABASE_PUBLISHABLE_KEY = "sb_publishable_..."
```

Nunca coloque chave `service_role` ou `sb_secret_...` no app Streamlit.

O schema inicial está em `supabase/schema.sql`.

## Próximas etapas

1. Criar o projeto Supabase exclusivo `renova-financas`.
2. Aplicar e validar o schema/RLS.
3. Ligar Auth na interface.
4. Substituir dados demonstrativos por persistência real.
5. Publicar no Streamlit Cloud.
6. Evoluir relatórios PDF/XLSX e RENOVA IA Financeira.
