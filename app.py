from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from src.access import is_owner, list_user_access
from src.data import (
    CATEGORIES,
    brl,
    demo_accounts,
    demo_budgets,
    demo_cards,
    demo_transactions,
    financial_summary,
)
from src.repository import (
    bootstrap_user,
    create_account,
    create_card,
    create_transaction,
    fetch_financial_data,
    get_ai_plan,
    has_active_ai_subscription,
    upsert_budget,
)
from src.supabase_client import (
    current_user,
    is_authenticated,
    is_configured,
    sign_in,
    sign_out,
    sign_up,
)
from src.theme import apply_renova_theme, auto_collapse_sidebar, brand_block, floating_ai_button
from src.ai_finance import confirm_pending_action, process_message


st.set_page_config(
    page_title="RENOVA Finanças",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_renova_theme()
REAL_MODE = is_configured()
APP_BUILD = "2026.09.11.2"


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="renova-hero">
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, hint: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="label">{label}</div>
          <div class="value">{value}</div>
          <div class="hint">{hint}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_auth() -> None:
    st.markdown(
        """
        <section class="sales-hero">
          <div class="sales-badge">✦ RENOVA FINANÇAS • GESTÃO + INTELIGÊNCIA ARTIFICIAL</div>
          <h1>Organize seu dinheiro hoje.<br><strong>Decida melhor amanhã.</strong></h1>
          <p class="sales-lead">
            Tenha contas, receitas, despesas, cartões, metas e orçamentos em um só lugar.
            Comece gratuitamente e, quando quiser acelerar sua gestão, ative a RENOVA IA.
          </p>
          <div class="sales-cta-row">
            <a href="#criar-conta" class="sales-cta primary">Criar minha conta grátis</a>
            <a href="#acessar" class="sales-cta secondary">Já tenho uma conta</a>
          </div>
          <div class="sales-proof">✓ Sem custo para começar &nbsp; • &nbsp; ✓ Recursos essenciais gratuitos &nbsp; • &nbsp; ✓ Seus dados separados por usuário</div>
        </section>

        <section class="sales-section">
          <div class="sales-eyebrow">CONTROLE FINANCEIRO SEM COMPLICAÇÃO</div>
          <h2>Você não precisa de mais uma planilha.<br><strong>Precisa enxergar o que está acontecendo.</strong></h2>
          <div class="sales-grid">
            <article class="sales-card"><span>💰</span><h3>Receitas e despesas</h3><p>Registre e acompanhe cada movimentação em uma visão organizada.</p></article>
            <article class="sales-card"><span>🏦</span><h3>Contas e cartões</h3><p>Centralize saldos, limites, faturas e vencimentos.</p></article>
            <article class="sales-card"><span>🎯</span><h3>Metas e orçamentos</h3><p>Defina limites e acompanhe seu progresso financeiro.</p></article>
            <article class="sales-card"><span>📊</span><h3>Análises visuais</h3><p>Transforme lançamentos em informações úteis para decidir melhor.</p></article>
          </div>
        </section>

        <section class="ai-sales">
          <div>
            <div class="sales-eyebrow">ASSISTENTE FINANCEIRO IA</div>
            <h2>Em vez de procurar funções,<br><strong>simplesmente peça.</strong></h2>
            <p>
              Diga “gastei R$ 85 no mercado”, “crie uma meta de R$ 5.000”,
              “marque a energia como paga” ou “analise minhas finanças”.
              A RENOVA IA entende o pedido e executa as ações disponíveis para sua conta.
            </p>
            <div class="ai-chip">🧠 Aprende suas preferências de uso</div>
          </div>
          <div class="ai-demo">
            <div class="bubble user">Gastei R$ 85 no mercado hoje.</div>
            <div class="bubble bot">🤖 Despesa registrada e categorizada. Seu painel já foi atualizado.</div>
            <div class="bubble user">Quando eu disser pensão, use a categoria Família.</div>
            <div class="bubble bot">🧠 Aprendi. Vou usar essa preferência nos próximos lançamentos.</div>
          </div>
        </section>

        <section class="pricing-section">
          <div class="sales-eyebrow">ESCOLHA COMO COMEÇAR</div>
          <h2>Comece grátis. <strong>Ative a IA quando quiser.</strong></h2>
          <div class="pricing-grid">
            <article class="price-card">
              <div class="plan">GRÁTIS</div>
              <div class="price">R$ 0</div>
              <p>Para organizar sua vida financeira e começar agora.</p>
              <ul>
                <li>✓ Dashboard financeiro</li><li>✓ Receitas e despesas</li>
                <li>✓ Contas e cartões</li><li>✓ Orçamentos e análises</li>
              </ul>
              <a href="#criar-conta" class="sales-cta secondary full">Criar conta gratuita</a>
            </article>
            <article class="price-card featured">
              <div class="popular">MAIS INTELIGENTE</div>
              <div class="plan">RENOVA IA</div>
              <div class="price">R$ 9,90 <small>/mês</small></div>
              <p>Para administrar suas finanças conversando com a IA.</p>
              <ul>
                <li>✓ Tudo do plano gratuito</li><li>✓ Assistente Financeiro IA</li>
                <li>✓ Modo Execução</li><li>✓ Memória de preferências</li>
                <li>✓ Análises e comandos pelo chat</li>
              </ul>
              <div class="sales-cta primary full static">Crie sua conta e ative por R$ 9,90/mês</div>
            </article>
          </div>
          <p class="pricing-note">A assinatura da IA é opcional. O usuário pode continuar utilizando os recursos gratuitos sem ativá-la.</p>
        </section>

        <div id="acessar" class="auth-anchor"></div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Acesse sua conta")
    login_tab, signup_tab = st.tabs(["Entrar", "Criar conta grátis"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("E-mail", key="login_email")
            password = st.text_input("Senha", type="password", key="login_password")
            submitted = st.form_submit_button("Entrar no RENOVA Finanças", use_container_width=True)
            if submitted:
                try:
                    sign_in(email, password)
                    st.success("Login realizado.")
                    st.rerun()
                except Exception:
                    st.error("Não foi possível entrar. Verifique e-mail e senha.")

    with signup_tab:
        st.markdown('<div id="criar-conta"></div>', unsafe_allow_html=True)
        st.caption("Crie sua conta gratuita. A assinatura RENOVA IA é opcional.")
        with st.form("signup_form"):
            full_name = st.text_input("Nome")
            email = st.text_input("E-mail", key="signup_email")
            password = st.text_input("Senha", type="password", key="signup_password")
            confirm = st.text_input("Confirmar senha", type="password")
            submitted = st.form_submit_button("Criar minha conta grátis", use_container_width=True)
            if submitted:
                if len(password) < 8:
                    st.error("Use uma senha com pelo menos 8 caracteres.")
                elif password != confirm:
                    st.error("As senhas não conferem.")
                else:
                    try:
                        response = sign_up(email, password, full_name)
                        if response.session is None:
                            st.success("Conta criada. Confirme o e-mail para liberar o acesso.")
                        else:
                            st.success("Conta criada e autenticada.")
                            st.rerun()
                    except Exception:
                        st.error("Não foi possível criar a conta. Confira os dados e tente novamente.")

    st.markdown(
        """
        <section class="sales-final">
          <div class="sales-eyebrow">COMECE AGORA</div>
          <h2>Mais clareza sobre seu dinheiro começa com <strong>um primeiro registro.</strong></h2>
          <p>Crie sua conta gratuita e organize suas finanças no seu ritmo.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def active_user_id() -> str:
    user = current_user()
    if not user:
        return ""
    return str(st.session_state.get("active_financial_user_id") or user.id)


def load_data() -> None:
    if REAL_MODE:
        user = current_user()
        if not user:
            return
        session_user_id = str(user.id)
        target_user_id = active_user_id()
        if st.session_state.get("bootstrap_user_id") != session_user_id:
            bootstrap_user(user)
            st.session_state.bootstrap_user_id = session_user_id
        bundle = fetch_financial_data(target_user_id)
        for key, value in bundle.items():
            st.session_state[key] = value
    else:
        if "transactions" not in st.session_state:
            st.session_state.transactions = demo_transactions()
        if "accounts" not in st.session_state:
            st.session_state.accounts = demo_accounts()
        if "cards" not in st.session_state:
            st.session_state.cards = demo_cards()
        if "budgets" not in st.session_state:
            st.session_state.budgets = demo_budgets()
        if "categories" not in st.session_state:
            st.session_state.categories = pd.DataFrame(
                [{"id": name, "name": name, "kind": "ambos", "is_active": True} for name in CATEGORIES]
            )


if REAL_MODE and not is_authenticated():
    render_auth()
    st.stop()

if REAL_MODE:
    session_user = current_user()
    session_user_id = str(session_user.id) if session_user else ""
    st.session_state.active_financial_user_id = session_user_id

    try:
        if session_user_id and is_owner(session_user_id):
            owner_users = list_user_access()
            active_users = [row for row in owner_users if row.get("status") == "ativo"]
            owner_options = {
                f"{row.get('email', row.get('user_id'))} • {row.get('role', 'usuario')}": str(row.get("user_id"))
                for row in active_users
            }
            if owner_options:
                with st.sidebar:
                    st.caption("MODO DONO • ACESSO GLOBAL")
                    selected_owner_user = st.selectbox(
                        "Gerenciar dados de",
                        list(owner_options.keys()),
                        key="owner_global_target",
                    )
                st.session_state.active_financial_user_id = owner_options[selected_owner_user]
    except Exception:
        st.session_state.active_financial_user_id = session_user_id

try:
    load_data()
except Exception:
    st.error("Não foi possível carregar seus dados financeiros agora.")
    st.stop()


AI_FAB_CLICKED = floating_ai_button()


def account_options() -> dict[str, str]:
    accounts = st.session_state.accounts
    if "id" in accounts.columns:
        return {str(row["conta"]): str(row["id"]) for _, row in accounts.iterrows()}
    return {str(row["conta"]): str(row["conta"]) for _, row in accounts.iterrows()}


def category_options(kind: str | None = None) -> dict[str, str]:
    categories = st.session_state.categories
    if categories.empty:
        return {}
    filtered = categories.copy()
    if kind in {"receita", "despesa"} and "kind" in filtered.columns:
        filtered = filtered[filtered["kind"].isin([kind, "ambos"])]
    return {str(row["name"]): str(row["id"]) for _, row in filtered.iterrows()}


def render_dashboard() -> None:
    hero(
        "Sua vida financeira, <strong>em um só lugar</strong>",
        "Visão rápida, inteligente e organizada para você decidir melhor.",
    )
    tx = st.session_state.transactions.copy()
    accounts = st.session_state.accounts.copy()
    summary = financial_summary(tx, accounts)

    cols = st.columns(4)
    with cols[0]:
        metric_card("Saldo total", brl(summary["saldo"]), "Somatório das contas")
    with cols[1]:
        metric_card("Receitas", brl(summary["receitas"]), "Período atual")
    with cols[2]:
        metric_card("Despesas", brl(summary["despesas"]), "Período atual")
    with cols[3]:
        metric_card("Resultado", brl(summary["resultado"]), f"Economia: {summary['taxa_economia']:.1f}%")

    st.write("")
    left, right = st.columns([1.45, 1])
    with left:
        st.subheader("Evolução financeira")
        if tx.empty:
            st.info("Adicione seu primeiro lançamento para visualizar a evolução.")
        else:
            chart_df = tx[tx["tipo"].isin(["Receita", "Despesa"])].copy().sort_values("data")
            if chart_df.empty:
                st.info("Ainda não há receitas ou despesas para o gráfico.")
            else:
                chart_df["receita"] = chart_df["valor"].where(chart_df["tipo"] == "Receita", 0)
                chart_df["despesa"] = chart_df["valor"].where(chart_df["tipo"] == "Despesa", 0)
                daily = chart_df.groupby("data", as_index=False)[["receita", "despesa"]].sum()
                fig = px.line(daily, x="data", y=["receita", "despesa"], markers=True)
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend_title_text="",
                    margin=dict(l=10, r=10, t=20, b=10),
                    height=360,
                )
                st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Despesas por categoria")
        expenses = tx[tx["tipo"] == "Despesa"].groupby("categoria", as_index=False)["valor"].sum() if not tx.empty else pd.DataFrame()
        if expenses.empty:
            st.info("Sem despesas categorizadas no período.")
        else:
            fig = px.pie(expenses, names="categoria", values="valor", hole=.62)
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=True,
                margin=dict(l=0, r=0, t=20, b=0),
                height=360,
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Últimos lançamentos")
    if tx.empty:
        st.info("Nenhum lançamento cadastrado.")
    else:
        latest = tx.sort_values("data", ascending=False).head(7).copy()
        latest["valor"] = latest["valor"].map(brl)
        visible = [col for col in ["data", "tipo", "categoria", "descricao", "valor", "conta", "status"] if col in latest.columns]
        st.dataframe(latest[visible], use_container_width=True, hide_index=True)


def render_transactions() -> None:
    hero(
        "Receitas e <strong>despesas</strong>",
        "Registre, categorize e acompanhe cada movimentação financeira.",
    )
    accounts_map = account_options()
    tx = st.session_state.transactions.copy()

    with st.expander("➕ Novo lançamento", expanded=False):
        if not accounts_map:
            st.warning("Cadastre uma conta antes de criar lançamentos.")
        else:
            with st.form("new_transaction", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    dt = st.date_input("Data", value=date.today())
                    kind_label = st.selectbox("Tipo", ["Receita", "Despesa"])
                kind_db = "receita" if kind_label == "Receita" else "despesa"
                categories_map = category_options(kind_db)
                with c2:
                    category_label = st.selectbox("Categoria", list(categories_map.keys())) if categories_map else None
                    account_label = st.selectbox("Conta", list(accounts_map.keys()))
                with c3:
                    description = st.text_input("Descrição")
                    value = st.number_input("Valor", min_value=0.0, step=10.0, format="%.2f")
                submitted = st.form_submit_button("Salvar lançamento", use_container_width=True)
                if submitted:
                    if not description.strip() or value <= 0:
                        st.error("Informe uma descrição e um valor maior que zero.")
                    elif REAL_MODE:
                        try:
                            create_transaction(
                                active_user_id(),
                                accounts_map[account_label],
                                categories_map.get(category_label) if category_label else None,
                                kind_db,
                                description,
                                value,
                                dt,
                            )
                            st.success("Lançamento salvo.")
                            st.rerun()
                        except Exception:
                            st.error("Não foi possível salvar o lançamento.")
                    else:
                        new_row = pd.DataFrame(
                            [[dt, kind_label, category_label or "Outros", description.strip(), value, account_label]],
                            columns=st.session_state.transactions.columns,
                        )
                        st.session_state.transactions = pd.concat([st.session_state.transactions, new_row], ignore_index=True)
                        st.rerun()

    if tx.empty:
        st.info("Nenhum lançamento cadastrado.")
        return
    f1, f2 = st.columns(2)
    with f1:
        type_filter = st.multiselect("Filtrar por tipo", ["Receita", "Despesa"], default=["Receita", "Despesa"])
    with f2:
        category_filter = st.multiselect("Filtrar por categoria", sorted(tx["categoria"].dropna().unique().tolist()))
    filtered = tx[tx["tipo"].isin(type_filter)]
    if category_filter:
        filtered = filtered[filtered["categoria"].isin(category_filter)]
    display = filtered.copy()
    display["valor"] = display["valor"].map(brl)
    visible = [col for col in ["data", "tipo", "categoria", "descricao", "valor", "conta", "status"] if col in display.columns]
    st.dataframe(display[visible], use_container_width=True, hide_index=True)


def render_accounts() -> None:
    hero(
        "Gerencie suas <strong>contas</strong>",
        "Veja saldos e concentre sua estrutura financeira em uma única tela.",
    )
    accounts = st.session_state.accounts.copy()
    with st.expander("➕ Nova conta"):
        with st.form("new_account", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                name = st.text_input("Nome da conta")
            with c2:
                account_type = st.selectbox("Tipo", ["conta", "carteira", "poupanca", "investimento"])
            with c3:
                initial_balance = st.number_input("Saldo inicial", step=10.0, format="%.2f")
            submitted = st.form_submit_button("Criar conta", use_container_width=True)
            if submitted and name.strip():
                if REAL_MODE:
                    try:
                        create_account(active_user_id(), name, account_type, initial_balance)
                        st.rerun()
                    except Exception:
                        st.error("Não foi possível criar a conta.")
                else:
                    st.info("Cadastro persistente de contas fica ativo quando o Supabase estiver configurado.")

    total = float(accounts["saldo"].sum()) if not accounts.empty else 0.0
    st.metric("Saldo consolidado", brl(total))
    if accounts.empty:
        st.info("Nenhuma conta cadastrada.")
    else:
        view = accounts.copy()
        view["saldo"] = view["saldo"].map(brl)
        visible = [col for col in ["conta", "tipo", "saldo", "ativo"] if col in view.columns]
        st.dataframe(view[visible], use_container_width=True, hide_index=True)


def render_cards() -> None:
    hero(
        "Controle todos os seus <strong>cartões</strong>",
        "Limite, fatura, fechamento e vencimento com leitura simples.",
    )
    cards = st.session_state.cards.copy()
    accounts_map = account_options()
    with st.expander("➕ Novo cartão"):
        with st.form("new_card", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                name = st.text_input("Nome do cartão")
                limit_value = st.number_input("Limite", min_value=0.0, step=100.0, format="%.2f")
            with c2:
                closing_day = st.number_input("Fechamento", min_value=1, max_value=31, value=10)
                due_day = st.number_input("Vencimento", min_value=1, max_value=31, value=17)
            with c3:
                linked = st.selectbox("Conta vinculada", ["Sem vínculo", *accounts_map.keys()])
            submitted = st.form_submit_button("Criar cartão", use_container_width=True)
            if submitted and name.strip():
                if REAL_MODE:
                    try:
                        create_card(
                            active_user_id(),
                            name,
                            limit_value,
                            int(closing_day),
                            int(due_day),
                            None if linked == "Sem vínculo" else accounts_map[linked],
                        )
                        st.rerun()
                    except Exception:
                        st.error("Não foi possível criar o cartão.")
                else:
                    st.info("Cadastro persistente de cartões fica ativo quando o Supabase estiver configurado.")

    if cards.empty:
        st.info("Nenhum cartão cadastrado.")
        return
    cols = st.columns(min(3, max(1, len(cards))))
    for idx, row in cards.iterrows():
        with cols[idx % len(cols)]:
            utilization = min(100.0, row["fatura"] / row["limite"] * 100 if row["limite"] else 0)
            st.markdown(
                f"""
                <div class="metric-card">
                  <div class="label">{row['cartao']}</div>
                  <div class="value">{brl(row['fatura'])}</div>
                  <div class="hint">Limite {brl(row['limite'])} • vence dia {int(row['vencimento'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(utilization / 100, text=f"{utilization:.0f}% do limite utilizado")


def render_budgets() -> None:
    hero(
        "Orçamentos por <strong>categoria</strong>",
        "Defina limites e descubra antes quando uma categoria está saindo do controle.",
    )
    budgets = st.session_state.budgets.copy()
    expense_categories = category_options("despesa")
    with st.expander("➕ Definir orçamento"):
        if not expense_categories:
            st.warning("Não há categorias de despesa disponíveis.")
        else:
            with st.form("budget_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    category_label = st.selectbox("Categoria", list(expense_categories.keys()))
                with c2:
                    planned = st.number_input("Orçamento mensal", min_value=0.0, step=50.0, format="%.2f")
                submitted = st.form_submit_button("Salvar orçamento", use_container_width=True)
                if submitted and planned > 0:
                    if REAL_MODE:
                        try:
                            upsert_budget(
                                active_user_id(),
                                expense_categories[category_label],
                                date.today().replace(day=1),
                                planned,
                            )
                            st.rerun()
                        except Exception:
                            st.error("Não foi possível salvar o orçamento.")
                    else:
                        st.info("Orçamentos persistentes ficam ativos quando o Supabase estiver configurado.")

    if budgets.empty:
        st.info("Nenhum orçamento definido para este mês.")
        return
    budgets["uso_%"] = budgets.apply(
        lambda row: (float(row["realizado"]) / float(row["orcamento"]) * 100) if float(row["orcamento"]) else 0,
        axis=1,
    )
    for _, row in budgets.iterrows():
        c1, c2 = st.columns([2.5, 1])
        with c1:
            st.write(f"**{row['categoria']}**")
            st.progress(min(float(row["uso_%"]), 100.0) / 100, text=f"{row['uso_%']:.0f}% utilizado")
        with c2:
            st.write(f"{brl(row['realizado'])} / {brl(row['orcamento'])}")


def render_analysis() -> None:
    hero(
        "Gráficos avançados para <strong>análise</strong>",
        "Entenda padrões, categorias e pontos de atenção sem depender de planilhas externas.",
    )
    tx = st.session_state.transactions.copy()
    if tx.empty:
        st.info("Cadastre lançamentos para liberar as análises.")
        return
    expenses = tx[tx["tipo"] == "Despesa"].groupby("categoria", as_index=False)["valor"].sum().sort_values("valor", ascending=False)
    incomes = tx[tx["tipo"] == "Receita"].groupby("categoria", as_index=False)["valor"].sum().sort_values("valor", ascending=False)
    c1, c2 = st.columns(2)
    with c1:
        if expenses.empty:
            st.info("Sem despesas para analisar.")
        else:
            fig = px.bar(expenses, x="valor", y="categoria", orientation="h", title="Ranking de despesas")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=390)
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        if incomes.empty:
            st.info("Sem receitas para analisar.")
        else:
            fig = px.bar(incomes, x="categoria", y="valor", title="Origem das receitas")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=390)
            st.plotly_chart(fig, use_container_width=True)


def render_reports() -> None:
    hero(
        "Relatórios e <strong>exportação</strong>",
        "Prepare seus dados para análise, prestação de contas e tomada de decisão.",
    )
    tx = st.session_state.transactions.copy().sort_values("data", ascending=False)
    if tx.empty:
        st.info("Nenhum lançamento disponível para exportar.")
        return
    report = tx.copy()
    report["valor"] = report["valor"].map(brl)
    visible = [col for col in ["data", "tipo", "categoria", "descricao", "valor", "conta", "status"] if col in report.columns]
    st.dataframe(report[visible], use_container_width=True, hide_index=True)
    csv = tx[visible].to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Baixar CSV",
        data=csv,
        file_name="renova-financas-lancamentos.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.caption("PDF e XLSX entram na próxima etapa do módulo de relatórios.")


def session_user_id() -> str:
    user = current_user()
    return str(user.id) if user and getattr(user, "id", None) else ""


def has_renova_ai_access() -> bool:
    uid = session_user_id()
    if not uid:
        return False
    try:
        if is_owner(uid):
            return True
        return has_active_ai_subscription(uid)
    except Exception:
        return False


def _ensure_ai_messages() -> None:
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = [
            {
                "role": "assistant",
                "content": (
                    "Olá! Eu sou a **RENOVA IA Financeira**. Posso analisar seus números e executar "
                    "ações de gestão financeira pelo chat."
                ),
            }
        ]


def _refresh_active_financial_data(user_id: str) -> None:
    refreshed = fetch_financial_data(user_id)
    for key, value in refreshed.items():
        st.session_state[key] = value


def _execute_ai_prompt(prompt: str) -> None:
    _ensure_ai_messages()
    st.session_state.ai_messages.append({"role": "user", "content": prompt})
    normalized = prompt.strip().upper()
    pending = st.session_state.get("ai_pending_action")
    user_id = active_user_id()

    try:
        if pending and normalized == "CONFIRMAR":
            result = confirm_pending_action(
                user_id,
                str(st.session_state.get("ai_pending_command") or ""),
                pending,
            )
            st.session_state.pop("ai_pending_action", None)
            st.session_state.pop("ai_pending_command", None)
        elif pending and normalized == "CANCELAR":
            st.session_state.pop("ai_pending_action", None)
            st.session_state.pop("ai_pending_command", None)
            st.session_state.ai_messages.append(
                {"role": "assistant", "content": "✅ A ação sensível foi cancelada e nenhuma alteração foi feita."}
            )
            return
        elif pending:
            st.session_state.ai_messages.append(
                {
                    "role": "assistant",
                    "content": "Há uma ação sensível pendente. Digite **CONFIRMAR** ou **CANCELAR** antes de enviar outro comando.",
                }
            )
            return
        else:
            bundle = {
                "transactions": st.session_state.transactions,
                "accounts": st.session_state.accounts,
                "cards": st.session_state.cards,
                "budgets": st.session_state.budgets,
                "categories": st.session_state.categories,
                "goals": st.session_state.goals,
            }
            result = process_message(user_id, prompt, bundle)
            if result.pending_confirmation:
                st.session_state.ai_pending_action = result.pending_confirmation
                st.session_state.ai_pending_command = prompt

        st.session_state.ai_messages.append({"role": "assistant", "content": result.text})
        if result.executed:
            _refresh_active_financial_data(user_id)
    except Exception as exc:
        st.session_state.ai_messages.append(
            {
                "role": "assistant",
                "content": "Não consegui executar esse comando agora. Nenhuma ação parcial foi considerada concluída.",
            }
        )
        st.session_state.ai_last_error = str(exc)


def render_ai_chat(input_key: str) -> None:
    _ensure_ai_messages()

    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.get("ai_pending_action"):
        st.warning("Existe uma ação sensível aguardando confirmação. Digite **CONFIRMAR** ou **CANCELAR**.")

    prompt = st.chat_input("Digite seu comando financeiro...", key=input_key)
    if prompt:
        _execute_ai_prompt(prompt)
        st.rerun()


def render_ai_subscription_sales() -> None:
    plan = get_ai_plan() if REAL_MODE else None
    price = float(plan.get("price", 9.90)) if plan else 9.90
    checkout_url = str(plan.get("checkout_url") or "") if plan else ""

    hero(
        "Ative o <strong>RENOVA IA</strong>",
        "Transforme o RENOVA Finanças em um assistente que entende seus pedidos e executa sua gestão pelo chat.",
    )

    st.markdown(
        f"""
        <section class="ai-subscribe-gate">
          <div class="sales-eyebrow">PLANO RENOVA IA</div>
          <h2>Seu assistente financeiro por <strong>R$ {price:,.2f}/mês</strong></h2>
          <p>
            O plano gratuito continua disponível para sua gestão manual.
            A assinatura RENOVA IA libera o chat, Modo Execução, memória de preferências
            e análises por conversa.
          </p>
          <div class="gate-benefits">
            <span>✓ Chat financeiro IA</span>
            <span>✓ Lançamentos por conversa</span>
            <span>✓ Metas e orçamentos por comando</span>
            <span>✓ Memória das suas preferências</span>
            <span>✓ Modo Execução</span>
          </div>
        </section>
        """.replace("9,90", f"{price:.2f}".replace(".", ",")),
        unsafe_allow_html=True,
    )

    if checkout_url:
        st.link_button(
            "Assinar RENOVA IA por R$ 9,90/mês com Mercado Pago",
            checkout_url,
            use_container_width=True,
        )
        st.caption("Após a confirmação do Mercado Pago, o acesso à IA será liberado automaticamente.")
    else:
        st.info(
            "A integração de checkout do Mercado Pago está sendo conectada. "
            "O plano já está cadastrado e o controle de acesso já está ativo."
        )


@st.dialog("🤖 Assistente Financeiro IA", width="large")
def open_ai_dialog() -> None:
    if not has_renova_ai_access():
        st.warning("O chat com a RENOVA IA é exclusivo do plano RENOVA IA.")
        plan = get_ai_plan() if REAL_MODE else None
        price = float(plan.get("price", 9.90)) if plan else 9.90
        st.markdown(
            f"Ative o plano por **R$ {price:.2f}/mês** para usar o Assistente Financeiro IA."
        )
        if st.button("Ver plano RENOVA IA", use_container_width=True):
            st.session_state.nav_page = "Assinar RENOVA IA"
            st.rerun()
        return

    st.caption("Converse sem sair desta tela. A IA pode executar as ações permitidas para sua conta.")
    render_ai_chat("ai_modal_input")


def render_ai() -> None:
    if not has_renova_ai_access():
        render_ai_subscription_sales()
        return

    hero(
        "RENOVA IA <strong>Financeira</strong>",
        "Converse com sua gestão financeira. A IA analisa e executa ações quando você pedir.",
    )
    st.caption("🧠 A IA aprende preferências suas e reaplica nos próximos comandos compatíveis.")
    render_ai_chat("ai_page_input")


NAV_PAGES = ["Dashboard", "Lançamentos", "Contas", "Cartões", "Orçamentos", "Análises", "Relatórios", "RENOVA IA", "Assinar RENOVA IA"]

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Dashboard"

with st.sidebar:
    brand_block()
    st.caption("GESTÃO FINANCEIRA")
    previous_page = st.session_state.get("_last_nav_page", st.session_state.nav_page)
    page = st.radio(
        "Navegação",
        NAV_PAGES,
        key="nav_page",
        label_visibility="collapsed",
    )
    if page != previous_page:
        st.session_state._last_nav_page = page
        auto_collapse_sidebar()
    else:
        st.session_state._last_nav_page = page
    st.divider()
    if REAL_MODE:
        st.success("Supabase conectado")
        user = current_user()
        if user:
            st.caption(str(getattr(user, "email", "Usuário autenticado")))
            st.caption(f"Build {APP_BUILD}")
        if st.button("Sair", use_container_width=True):
            sign_out()
            st.rerun()
    else:
        st.warning("Modo demonstração")
        st.caption("Configure SUPABASE_URL e SUPABASE_PUBLISHABLE_KEY no Streamlit Secrets.")

pages = {
    "Dashboard": render_dashboard,
    "Lançamentos": render_transactions,
    "Contas": render_accounts,
    "Cartões": render_cards,
    "Orçamentos": render_budgets,
    "Análises": render_analysis,
    "Relatórios": render_reports,
    "RENOVA IA": render_ai,
    "Assinar RENOVA IA": render_ai_subscription_sales,
}
pages[page]()

if AI_FAB_CLICKED:
    if has_renova_ai_access():
        open_ai_dialog()
    else:
        st.session_state.nav_page = "Assinar RENOVA IA"
        st.rerun()
