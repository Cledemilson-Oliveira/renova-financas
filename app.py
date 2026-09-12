from __future__ import annotations

from datetime import date
from html import escape

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
    create_category,
    create_transaction,
    delete_transaction,
    fetch_financial_data,
    get_ai_plan,
    has_active_ai_subscription,
    update_transaction,
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
from src.urgencies import analyze_financial_urgencies, urgency_summary


st.set_page_config(
    page_title="RENOVA Finanças",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_renova_theme()
REAL_MODE = is_configured()
APP_BUILD = "2026.09.12.2"


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
    # A tela pública deve funcionar como landing page; nenhuma navegação interna
    # do Streamlit fica exposta antes da autenticação.
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapseButton"]{display:none!important}
        [data-testid="stMainBlockContainer"]{max-width:1480px!important;margin:0 auto!important}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <section class="sales-hero">
          <div class="sales-badge">✦ RENOVA FINANÇAS • GESTÃO + INTELIGÊNCIA ARTIFICIAL</div>
          <h1>Organize seu dinheiro hoje.<br><strong>Decida melhor amanhã.</strong></h1>
          <p class="sales-lead">
            Tenha contas, receitas, despesas, cartões, metas e orçamentos em um só lugar.
            A IA Padrão já vem incluída gratuitamente; personalize a memória e o treinamento quando quiser.
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
            <div class="ai-chip">🤖 IA Padrão gratuita • 🧠 Treinamento personalizado no Premium</div>
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
          <h2>Comece grátis com IA. <strong>Personalize quando quiser.</strong></h2>
          <div class="pricing-grid">
            <article class="price-card">
              <div class="plan">GRÁTIS</div>
              <div class="price">R$ 0</div>
              <p>Para organizar sua vida financeira e começar agora.</p>
              <ul>
                <li>✓ Dashboard financeiro</li><li>✓ Receitas e despesas</li>
                <li>✓ Contas e cartões</li><li>✓ Orçamentos e análises</li>
                <li>✓ IA Padrão para lançamentos e consultas</li>
              </ul>
              <a href="#criar-conta" class="sales-cta secondary full">Criar conta gratuita</a>
            </article>
            <article class="price-card featured">
              <div class="popular">MAIS INTELIGENTE</div>
              <div class="plan">RENOVA IA</div>
              <div class="price">R$ 9,90 <small>/mês</small></div>
              <p>Para transformar a IA padrão em um assistente treinado para o seu jeito de trabalhar.</p>
              <ul>
                <li>✓ Tudo do plano gratuito</li><li>✓ Treinamento personalizado</li>
                <li>✓ Memória de preferências e regras</li><li>✓ PDFs e YouTube como conhecimento privado</li>
                <li>✓ Vocabulário, conta padrão e contexto próprio</li>
              </ul>
              <div class="sales-cta primary full static">Personalize sua IA por R$ 9,90/mês</div>
            </article>
          </div>
          <p class="pricing-note">A IA Padrão faz parte da conta gratuita. A assinatura é opcional e libera treinamento e memória personalizados.</p>
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
    if "is_active" in filtered.columns:
        filtered = filtered[filtered["is_active"] == True]
    if kind in {"receita", "despesa"} and "kind" in filtered.columns:
        filtered = filtered[filtered["kind"].isin([kind, "ambos"])]
    return {str(row["name"]): str(row["id"]) for _, row in filtered.iterrows()}


def _refresh_categories() -> None:
    if not REAL_MODE:
        return
    refreshed = fetch_financial_data(active_user_id())
    st.session_state.categories = refreshed["categories"]


def _create_or_get_category(kind: str, name: str) -> tuple[str, str]:
    clean = " ".join((name or "").split()).strip()
    if not clean:
        raise ValueError("Informe o nome da categoria.")

    existing = category_options(kind)
    for label, category_id in existing.items():
        if label.casefold() == clean.casefold():
            return category_id, label

    if REAL_MODE:
        create_category(
            active_user_id(),
            clean,
            kind,
            "💰" if kind == "receita" else "💸",
        )
        _refresh_categories()
        for label, category_id in category_options(kind).items():
            if label.casefold() == clean.casefold():
                return category_id, label
        raise RuntimeError("A categoria foi criada, mas não pôde ser recarregada.")

    new_row = pd.DataFrame(
        [{"id": clean, "name": clean, "kind": kind, "icon": "📌", "is_active": True}]
    )
    st.session_state.categories = pd.concat([st.session_state.categories, new_row], ignore_index=True)
    return clean, clean


def render_urgency_center() -> None:
    alerts = analyze_financial_urgencies(
        transactions=st.session_state.get("transactions"),
        accounts=st.session_state.get("accounts"),
        budgets=st.session_state.get("budgets"),
        cards=st.session_state.get("cards"),
    )
    summary = urgency_summary(alerts)

    st.markdown("### 🧭 Central Inteligente de Urgências")
    st.caption(
        "Análise automática dos seus dados para destacar o que merece atenção primeiro. "
        "Os alertas são recalculados sempre que os dados financeiros mudam."
    )

    if not alerts:
        st.success("✅ Nenhuma urgência financeira relevante detectada neste momento.")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Urgências", summary["total"])
    with c2:
        st.metric("Críticas", summary["critica"])
    with c3:
        st.metric("Altas", summary["alta"])
    with c4:
        st.metric("Médias", summary["media"])

    for alert in alerts[:6]:
        severity = str(alert.get("severity") or "info")
        title = f"{alert.get('icon', '🔎')} {alert.get('severity_label', 'INFO')} • {alert.get('title', 'Alerta financeiro')}"
        message = str(alert.get("message") or "")
        action = str(alert.get("action") or "")

        if severity == "critica":
            st.error(f"**{title}**\n\n{message}\n\n**Ação recomendada:** {action}")
        elif severity == "alta":
            st.warning(f"**{title}**\n\n{message}\n\n**Ação recomendada:** {action}")
        else:
            st.info(f"**{title}**\n\n{message}\n\n**Ação recomendada:** {action}")

    if len(alerts) > 6:
        st.caption(f"Mais {len(alerts) - 6} alerta(s) de menor prioridade foram agrupados para manter o painel objetivo.")

    action_cols = st.columns(2)
    with action_cols[0]:
        if st.button("📋 Revisar lançamentos", key="urgencies_open_transactions", use_container_width=True):
            st.session_state.nav_page = "Lançamentos"
            st.rerun()
    with action_cols[1]:
        if st.button("🤖 Analisar com RENOVA IA", key="urgencies_open_ai", use_container_width=True):
            st.session_state.nav_page = "RENOVA IA"
            st.rerun()


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
    render_urgency_center()
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
            fig.update_traces(
                domain={"x": [0.10, 0.90], "y": [0.18, 0.98]},
                textposition="inside",
                textinfo="percent",
                hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>",
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11),
                ),
                margin=dict(l=16, r=16, t=8, b=62),
                height=380,
                uniformtext_minsize=10,
                uniformtext_mode="hide",
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Últimos lançamentos")
    if tx.empty:
        st.info("Nenhum lançamento cadastrado.")
    else:
        latest = tx.sort_values("data", ascending=False).head(7).copy()
        latest["valor"] = latest["valor"].map(brl)
        visible = [col for col in ["data", "vencimento", "tipo", "categoria", "descricao", "valor", "conta", "status"] if col in latest.columns]
        st.dataframe(latest[visible], use_container_width=True, hide_index=True)


def _render_quick_transaction_dialog(kind_db: str) -> None:
    is_income = kind_db == "receita"
    kind_label = "Receita" if is_income else "Despesa"
    accounts_map = account_options()
    if not accounts_map:
        st.warning("Cadastre uma conta antes de criar lançamentos.")
        return

    categories_map = category_options(kind_db)
    options = list(categories_map.keys())
    if "Outros" not in options:
        options.append("Outros")
    options.append("➕ Nova categoria...")

    st.caption(
        "Categorias exibidas aqui são filtradas automaticamente para "
        + ("receitas." if is_income else "despesas.")
    )
    c1, c2 = st.columns(2)
    with c1:
        dt = st.date_input("Data do lançamento", value=date.today(), key=f"quick_{kind_db}_date")
        account_label = st.selectbox("Conta", list(accounts_map.keys()), key=f"quick_{kind_db}_account")
    with c2:
        category_label = st.selectbox("Categoria", options, key=f"quick_{kind_db}_category")
        value = st.number_input(
            "Valor",
            min_value=0.0,
            step=10.0,
            format="%.2f",
            key=f"quick_{kind_db}_amount",
        )

    due_date = None
    status_db = "pago"
    if not is_income:
        situation = st.radio(
            "Situação da despesa",
            ["✅ Pago", "🕒 Pendente"],
            horizontal=True,
            key=f"quick_{kind_db}_status",
        )
        if situation == "🕒 Pendente":
            status_db = "previsto"
            due_date = st.date_input(
                "Data de vencimento",
                value=date.today(),
                key=f"quick_{kind_db}_due_date",
                help="Esta data é usada pela Central de Urgências para identificar contas próximas do vencimento ou atrasadas.",
            )

    needs_custom = category_label in {"Outros", "➕ Nova categoria..."}
    custom_category = ""
    if needs_custom:
        custom_category = st.text_input(
            "Especifique a categoria",
            placeholder="Ex.: Ferramentas, Comissão, Manutenção...",
            key=f"quick_{kind_db}_custom_category",
        )

    description = st.text_input(
        "Descrição",
        placeholder="Descreva o lançamento",
        key=f"quick_{kind_db}_description",
    )

    if st.button(
        f"{'💰' if is_income else '💸'} SALVAR {kind_label.upper()}",
        key=f"quick_{kind_db}_save",
        use_container_width=True,
    ):
        if value <= 0:
            st.error("Informe um valor maior que zero.")
            return
        if not description.strip():
            st.error("Informe a descrição do lançamento.")
            return
        if needs_custom and not custom_category.strip():
            st.error("Especifique a nova categoria antes de salvar.")
            return

        try:
            if needs_custom:
                category_id, category_name = _create_or_get_category(kind_db, custom_category)
            else:
                category_id = categories_map.get(category_label)
                category_name = category_label

            if REAL_MODE:
                create_transaction(
                    active_user_id(),
                    accounts_map[account_label],
                    category_id,
                    kind_db,
                    description,
                    value,
                    dt,
                    due_date=due_date,
                    status=status_db,
                )
                st.success(f"{kind_label} salva em {category_name}.")
                st.rerun()
            else:
                new_row = {
                    "data": dt,
                    "tipo": kind_label,
                    "categoria": category_name,
                    "descricao": description.strip(),
                    "valor": value,
                    "conta": account_label,
                }
                st.session_state.transactions = pd.concat(
                    [st.session_state.transactions, pd.DataFrame([new_row])],
                    ignore_index=True,
                )
                st.rerun()
        except Exception as exc:
            st.error(f"Não foi possível salvar o lançamento: {exc}")


@st.dialog("💸 Lançar despesa", width="large")
def open_expense_dialog() -> None:
    _render_quick_transaction_dialog("despesa")


@st.dialog("💰 Lançar receita", width="large")
def open_income_dialog() -> None:
    _render_quick_transaction_dialog("receita")


@st.dialog("✏️ Editar lançamento", width="large")
def open_edit_transaction_dialog(transaction_id: str) -> None:
    tx = st.session_state.transactions
    matches = tx[tx["id"].astype(str) == str(transaction_id)] if "id" in tx.columns else pd.DataFrame()
    if matches.empty:
        st.error("Lançamento não encontrado.")
        return

    row = matches.iloc[0]
    kind_db = "receita" if str(row["tipo"]) == "Receita" else "despesa"
    accounts_map = account_options()
    categories_map = category_options(kind_db)

    current_account = str(row.get("conta") or "")
    account_labels = list(accounts_map.keys())
    account_index = account_labels.index(current_account) if current_account in account_labels else 0

    current_category = str(row.get("categoria") or "")
    category_labels = list(categories_map.keys())
    category_index = category_labels.index(current_category) if current_category in category_labels else 0

    current_status = str(row.get("status_db") or row.get("status") or "pago")
    status_labels = {
        "pago": "✅ Pago",
        "previsto": "🕒 Pendente",
        "atrasado": "🚨 Atrasado",
    }
    reverse_status = {label: key for key, label in status_labels.items()}
    current_status_label = status_labels.get(current_status, "🕒 Pendente")

    c1, c2 = st.columns(2)
    with c1:
        edit_date = st.date_input("Data do lançamento", value=row["data"], key=f"edit_date_{transaction_id}")
        edit_account = st.selectbox("Conta", account_labels, index=account_index, key=f"edit_account_{transaction_id}")
        edit_status_label = st.selectbox(
            "Situação",
            list(reverse_status.keys()),
            index=list(reverse_status.keys()).index(current_status_label),
            key=f"edit_status_{transaction_id}",
        )
    with c2:
        edit_value = st.number_input(
            "Valor",
            min_value=0.01,
            value=float(row["valor"]),
            step=10.0,
            format="%.2f",
            key=f"edit_value_{transaction_id}",
        )
        edit_category = st.selectbox(
            "Categoria",
            category_labels,
            index=category_index,
            key=f"edit_category_{transaction_id}",
        )
        has_due = st.checkbox(
            "Possui data de vencimento",
            value=pd.notna(row.get("vencimento")),
            key=f"edit_has_due_{transaction_id}",
        )

    edit_due_date = None
    if has_due:
        current_due = row.get("vencimento")
        if pd.isna(current_due) or current_due is None:
            current_due = date.today()
        edit_due_date = st.date_input(
            "Data de vencimento",
            value=current_due,
            key=f"edit_due_{transaction_id}",
        )

    edit_description = st.text_input(
        "Descrição",
        value=str(row.get("descricao") or ""),
        key=f"edit_description_{transaction_id}",
    )

    if st.button("💾 Salvar alterações", key=f"save_edit_{transaction_id}", use_container_width=True):
        if not edit_description.strip():
            st.error("Informe a descrição do lançamento.")
            return
        try:
            update_transaction(
                active_user_id(),
                str(transaction_id),
                account_id=accounts_map[edit_account],
                category_id=categories_map[edit_category],
                description=edit_description,
                amount=edit_value,
                occurred_on=edit_date,
                due_date=edit_due_date if has_due else None,
                status=reverse_status[edit_status_label],
            )
            _refresh_active_financial_data(active_user_id())
            st.success("Lançamento atualizado.")
            st.rerun()
        except Exception as exc:
            st.error(f"Não foi possível atualizar: {exc}")


@st.dialog("🗑️ Excluir lançamento")
def open_delete_transaction_dialog(transaction_id: str) -> None:
    tx = st.session_state.transactions
    matches = tx[tx["id"].astype(str) == str(transaction_id)] if "id" in tx.columns else pd.DataFrame()
    if matches.empty:
        st.error("Lançamento não encontrado.")
        return
    row = matches.iloc[0]
    st.warning(
        f"Você está prestes a excluir **{row['descricao']} — {brl(float(row['valor']))}**. "
        "Essa ação remove o lançamento dos seus registros."
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancelar", key=f"cancel_delete_{transaction_id}", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("🗑️ Confirmar exclusão", key=f"confirm_delete_{transaction_id}", type="primary", use_container_width=True):
            try:
                delete_transaction(active_user_id(), str(transaction_id))
                _refresh_active_financial_data(active_user_id())
                st.success("Lançamento excluído.")
                st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível excluir: {exc}")


@st.dialog("🗑️ Excluir lançamentos selecionados", width="large")
def open_bulk_delete_transactions_dialog(transaction_ids: list[str]) -> None:
    tx = st.session_state.transactions
    ids = {str(item) for item in transaction_ids}
    selected = tx[tx["id"].astype(str).isin(ids)] if "id" in tx.columns else pd.DataFrame()
    if selected.empty:
        st.info("Nenhum lançamento selecionado.")
        return

    st.warning(
        f"Você está prestes a excluir **{len(selected)} lançamento(s)**. "
        "Essa ação remove definitivamente os registros selecionados."
    )
    preview = selected[[col for col in ["data", "descricao", "valor"] if col in selected.columns]].copy()
    if "valor" in preview.columns:
        preview["valor"] = preview["valor"].map(brl)
    st.dataframe(preview, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancelar", key="cancel_bulk_delete_transactions", use_container_width=True):
            st.rerun()
    with c2:
        if st.button(
            f"🗑️ Excluir {len(selected)} lançamento(s)",
            key="confirm_bulk_delete_transactions",
            type="primary",
            use_container_width=True,
        ):
            failed = []
            for transaction_id in selected["id"].astype(str).tolist():
                try:
                    delete_transaction(active_user_id(), transaction_id)
                except Exception as exc:
                    failed.append((transaction_id, str(exc)))
            _refresh_active_financial_data(active_user_id())
            st.session_state.pop("transactions_editor", None)
            st.session_state.tx_select_all = False
            if failed:
                st.session_state.tx_bulk_message = (
                    "warning",
                    f"{len(selected) - len(failed)} lançamento(s) excluído(s), mas {len(failed)} não puderam ser removidos.",
                )
            else:
                st.session_state.tx_bulk_message = (
                    "success",
                    f"{len(selected)} lançamento(s) excluído(s) com sucesso.",
                )
            st.rerun()


def render_transactions() -> None:
    hero(
        "Receitas e <strong>despesas</strong>",
        "Registre, corrija e acompanhe cada movimentação sem perder o controle dos vencimentos.",
    )

    st.markdown(
        """
        <style>
        .st-key-launch_actions{
          position:fixed!important;
          right:24px!important;
          bottom:94px!important;
          z-index:9998!important;
          width:min(430px,calc(100vw - 48px))!important;
          padding:10px!important;
          border:1px solid rgba(255,215,90,.34)!important;
          border-radius:18px!important;
          background:linear-gradient(145deg,rgba(4,17,28,.96),rgba(2,8,14,.97))!important;
          box-shadow:0 20px 44px rgba(0,0,0,.45),0 0 24px rgba(0,174,239,.12)!important;
          backdrop-filter:blur(16px)!important;
        }
        .st-key-launch_actions [data-testid="stHorizontalBlock"]{gap:8px!important}
        .st-key-transactions_premium_table{
          margin-top:10px!important;
          padding:12px 12px 6px!important;
          border:1px solid rgba(64,185,255,.22)!important;
          border-radius:20px!important;
          background:linear-gradient(145deg,rgba(4,22,36,.98),rgba(2,10,18,.99))!important;
          box-shadow:0 18px 44px rgba(0,0,0,.28),0 0 28px rgba(0,174,239,.08)!important;
          overflow:hidden!important;
        }
        .st-key-transactions_premium_table [data-testid="stDataFrame"]{
          border-radius:14px!important;
          overflow:hidden!important;
        }
        .st-key-transactions_bulk_actions{
          margin-top:10px!important;
          padding:10px 12px!important;
          border-radius:16px!important;
          border:1px solid rgba(255,215,90,.24)!important;
          background:linear-gradient(135deg,rgba(6,27,43,.92),rgba(4,15,25,.96))!important;
        }
        .transactions-summary{
          display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 2px;
        }
        .transactions-summary span{
          display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:999px;
          border:1px solid rgba(0,174,239,.18);background:rgba(0,174,239,.06);
          color:#BFEFFF;font-size:.72rem;font-weight:800;
        }
        .transactions-summary span.income{color:#9CF2C2;border-color:rgba(62,214,132,.22);background:rgba(62,214,132,.07)}
        .transactions-summary span.expense{color:#FFC2C2;border-color:rgba(255,104,104,.22);background:rgba(255,104,104,.07)}
        @media(max-width:768px){
          .st-key-launch_actions{left:14px!important;right:14px!important;bottom:136px!important;width:auto!important}
          .st-key-transactions_premium_table{padding:8px 6px 4px!important;border-radius:16px!important}
          .st-key-transactions_bulk_actions{padding:8px!important}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="launch_actions"):
        c1, c2 = st.columns(2)
        with c1:
            expense_clicked = st.button("💸 Lançar despesa", key="fab_expense", use_container_width=True)
        with c2:
            income_clicked = st.button("💰 Lançar receita", key="fab_income", use_container_width=True)

    if expense_clicked:
        open_expense_dialog()
    if income_clicked:
        open_income_dialog()

    bulk_message = st.session_state.pop("tx_bulk_message", None)
    if bulk_message:
        message_type, message_text = bulk_message
        if message_type == "success":
            st.success(message_text)
        else:
            st.warning(message_text)

    st.caption("Despesas pendentes podem receber uma data de vencimento; a Central de Urgências usa essa data para avisar quando estão próximas ou atrasadas.")

    tx = st.session_state.transactions.copy()
    if tx.empty:
        st.info("Nenhum lançamento cadastrado. Use um dos botões flutuantes para começar.")
        return

    search_col, type_col, category_col, status_col = st.columns([1.45, 1, 1.1, 1])
    with search_col:
        search_text = st.text_input(
            "Buscar lançamento",
            placeholder="Descrição, categoria ou conta...",
            key="transactions_search",
        )
    with type_col:
        type_filter = st.multiselect(
            "Tipo",
            ["Receita", "Despesa"],
            default=["Receita", "Despesa"],
            key="transactions_type_filter",
        )
    with category_col:
        category_filter = st.multiselect(
            "Categoria",
            sorted(tx["categoria"].dropna().unique().tolist()),
            key="transactions_category_filter",
        )
    with status_col:
        status_options = sorted(tx["status"].dropna().astype(str).unique().tolist()) if "status" in tx.columns else []
        status_filter = st.multiselect("Status", status_options, key="transactions_status_filter")

    filtered = tx[tx["tipo"].isin(type_filter)].copy()
    if category_filter:
        filtered = filtered[filtered["categoria"].isin(category_filter)]
    if status_filter and "status" in filtered.columns:
        filtered = filtered[filtered["status"].astype(str).isin(status_filter)]
    if search_text.strip():
        needle = search_text.strip().casefold()
        searchable_columns = [col for col in ["descricao", "categoria", "conta", "tipo", "status"] if col in filtered.columns]
        mask = pd.Series(False, index=filtered.index)
        for col in searchable_columns:
            mask = mask | filtered[col].fillna("").astype(str).str.casefold().str.contains(needle, regex=False)
        filtered = filtered[mask]

    if filtered.empty:
        st.info("Nenhum lançamento encontrado com os filtros atuais.")
        return

    income_total = float(filtered.loc[filtered["tipo"] == "Receita", "valor"].sum())
    expense_total = float(filtered.loc[filtered["tipo"] == "Despesa", "valor"].sum())
    st.markdown(
        f"""
        <div class="transactions-summary">
          <span>📋 {len(filtered)} lançamento(s)</span>
          <span class="income">↗ Receitas {brl(income_total)}</span>
          <span class="expense">↘ Despesas {brl(expense_total)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    can_manage = REAL_MODE and "id" in filtered.columns
    display = filtered.copy()
    if "id" in display.columns:
        display["_tx_id"] = display["id"].astype(str)
    display.insert(0, "selecionar", bool(st.session_state.get("tx_select_all", False)))
    display["valor"] = display["valor"].map(brl)
    if "status" in display.columns:
        status_labels = {"pago": "✅ Pago", "atrasado": "🚨 Atrasado", "previsto": "🕒 Previsto"}
        display["status"] = display["status"].astype(str).map(lambda value: status_labels.get(value.casefold(), value.title()))

    visible = ["selecionar", *[col for col in ["data", "vencimento", "tipo", "categoria", "descricao", "valor", "conta", "status"] if col in display.columns]]
    if "_tx_id" in display.columns:
        visible.append("_tx_id")

    select_all_col, helper_col = st.columns([1, 2.4])
    with select_all_col:
        select_all = st.checkbox("Selecionar todos os filtrados", key="tx_select_all")
    with helper_col:
        st.caption("Marque as caixas da primeira coluna para editar um registro ou excluir vários de uma vez.")

    if select_all:
        display["selecionar"] = True

    with st.container(key="transactions_premium_table"):
        edited = st.data_editor(
            display[visible],
            key="transactions_editor",
            use_container_width=True,
            hide_index=True,
            disabled=[col for col in visible if col not in {"selecionar"}],
            column_config={
                "selecionar": st.column_config.CheckboxColumn("✓", help="Marque para selecionar", default=False, width="small"),
                "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY", width="small"),
                "vencimento": st.column_config.DateColumn("Vencimento", format="DD/MM/YYYY", width="small"),
                "tipo": st.column_config.TextColumn("Tipo", width="small"),
                "categoria": st.column_config.TextColumn("Categoria", width="medium"),
                "descricao": st.column_config.TextColumn("Descrição", width="large"),
                "valor": st.column_config.TextColumn("Valor", width="small"),
                "conta": st.column_config.TextColumn("Conta", width="medium"),
                "status": st.column_config.TextColumn("Status", width="small"),
                "_tx_id": None,
            },
            height=min(620, max(210, 74 + len(display) * 36)),
        )

    selected_ids = []
    if can_manage and "selecionar" in edited.columns and "_tx_id" in edited.columns:
        selected_ids = edited.loc[edited["selecionar"] == True, "_tx_id"].astype(str).tolist()

    if can_manage:
        with st.container(key="transactions_bulk_actions"):
            info_col, edit_col, delete_col = st.columns([1.4, 1, 1])
            with info_col:
                if selected_ids:
                    st.markdown(f"**✓ {len(selected_ids)} selecionado(s)**")
                else:
                    st.caption("Selecione um ou mais lançamentos na tabela.")
            with edit_col:
                edit_disabled = len(selected_ids) != 1
                if st.button(
                    "✏️ Editar selecionado",
                    key="edit_checked_transaction",
                    use_container_width=True,
                    disabled=edit_disabled,
                ):
                    open_edit_transaction_dialog(selected_ids[0])
            with delete_col:
                delete_disabled = len(selected_ids) == 0
                if st.button(
                    f"🗑️ Excluir selecionados{f' ({len(selected_ids)})' if selected_ids else ''}",
                    key="delete_checked_transactions",
                    use_container_width=True,
                    type="primary" if selected_ids else "secondary",
                    disabled=delete_disabled,
                ):
                    open_bulk_delete_transactions_dialog(selected_ids)


def render_categories() -> None:
    hero(
        "Suas <strong>categorias</strong>",
        "Crie categorias próprias para receitas e despesas e deixe os lançamentos com a cara da sua rotina.",
    )
    categories = st.session_state.categories.copy()

    with st.expander("➕ Criar categoria personalizada", expanded=True):
        with st.form("new_category_form", clear_on_submit=True):
            c1, c2 = st.columns([1.5, 1])
            with c1:
                name = st.text_input("Nome da categoria", placeholder="Ex.: Ferramentas, Comissão, Manutenção")
            with c2:
                kind_label = st.selectbox("Usar em", ["Despesa", "Receita", "Receita e despesa"])
            submitted = st.form_submit_button("Criar categoria", use_container_width=True)
            if submitted:
                kind_map = {"Despesa": "despesa", "Receita": "receita", "Receita e despesa": "ambos"}
                kind_db = kind_map[kind_label]
                if not name.strip():
                    st.error("Informe o nome da categoria.")
                elif REAL_MODE:
                    try:
                        create_category(
                            active_user_id(),
                            name,
                            kind_db,
                            "💰" if kind_db == "receita" else "💸" if kind_db == "despesa" else "📌",
                        )
                        _refresh_categories()
                        st.success("Categoria criada.")
                        st.rerun()
                    except Exception:
                        st.error("Não foi possível criar a categoria. Verifique se ela já existe para esse tipo.")
                else:
                    new_row = pd.DataFrame(
                        [{"id": name.strip(), "name": name.strip(), "kind": kind_db, "icon": "📌", "is_active": True}]
                    )
                    st.session_state.categories = pd.concat([st.session_state.categories, new_row], ignore_index=True)
                    st.rerun()

    if categories.empty:
        st.info("Nenhuma categoria cadastrada.")
        return

    kind_names = {"receita": "Receita", "despesa": "Despesa", "ambos": "Receita e despesa"}
    view = categories.copy()
    if "kind" in view.columns:
        view["tipo"] = view["kind"].map(kind_names).fillna(view["kind"])
    if "is_active" in view.columns:
        view["status"] = view["is_active"].map({True: "Ativa", False: "Inativa"})
    visible = [col for col in ["icon", "name", "tipo", "status"] if col in view.columns]
    view = view.rename(columns={"icon": "ícone", "name": "categoria"})
    visible = ["ícone" if col == "icon" else "categoria" if col == "name" else col for col in visible]
    st.dataframe(view[visible], use_container_width=True, hide_index=True)
    st.caption("Categorias criadas aqui aparecem automaticamente nos modais de lançamento conforme o tipo selecionado.")


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
    visible = [col for col in ["data", "vencimento", "tipo", "categoria", "descricao", "valor", "conta", "status"] if col in report.columns]
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
    # Todo usuário autenticado recebe a IA Padrão gratuita.
    return bool(session_user_id())


def has_personalized_ai_training_access() -> bool:
    uid = session_user_id()
    if not uid:
        return False
    try:
        return bool(is_owner(uid) or has_active_ai_subscription(uid))
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
                "_allow_personalized_training": has_personalized_ai_training_access(),
            }

            pending_context = st.session_state.get("ai_pending_context")
            effective_prompt = prompt
            if pending_context:
                original = str(pending_context.get("original_message") or "").strip()
                if original:
                    effective_prompt = f"{original} {prompt}".strip()

            result = process_message(user_id, effective_prompt, bundle)

            if result.pending_confirmation:
                st.session_state.ai_pending_action = result.pending_confirmation
                st.session_state.ai_pending_command = effective_prompt

            if result.pending_context:
                st.session_state.ai_pending_context = result.pending_context
            else:
                st.session_state.pop("ai_pending_context", None)

        st.session_state.ai_messages.append({"role": "assistant", "content": result.text})
        if result.executed:
            st.session_state.pop("ai_pending_context", None)
            _refresh_active_financial_data(user_id)
    except Exception as exc:
        st.session_state.ai_messages.append(
            {
                "role": "assistant",
                "content": "Não consegui executar esse comando agora. Nenhuma ação parcial foi considerada concluída.",
            }
        )
        st.session_state.ai_last_error = str(exc)


def render_ai_chat(input_key: str, *, fragment_rerun: bool = False) -> None:
    _ensure_ai_messages()

    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.get("ai_pending_action"):
        st.warning("Existe uma ação sensível aguardando confirmação. Digite **CONFIRMAR** ou **CANCELAR**.")
    elif st.session_state.get("ai_pending_context"):
        st.info("Estou aguardando a informação que falta para concluir o pedido anterior.")

    prompt = st.chat_input("Digite seu comando financeiro...", key=input_key)
    if prompt:
        _execute_ai_prompt(prompt)
        if fragment_rerun:
            st.rerun(scope="fragment")
        else:
            st.rerun()


def render_ai_subscription_sales() -> None:
    # Regra de funil: assinatura sempre passa pela página comercial antes do checkout.
    st.switch_page("pages/Assinar_RENOVA_IA.py")


@st.dialog("🤖 Assistente Financeiro IA", width="large")
def open_ai_dialog() -> None:
    personalized = has_personalized_ai_training_access()

    st.markdown(
        """
        <style>
        /* RENOVA IA • modal de conversa inspirado em mensageiros modernos */
        div[role="dialog"]{
          width:min(94vw,1120px)!important;
          max-width:1120px!important;
        }
        div[role="dialog"] > div{
          border-radius:24px!important;
          border:1px solid rgba(25,217,255,.22)!important;
          background:
            radial-gradient(circle at 90% 0%,rgba(25,217,255,.09),transparent 24%),
            linear-gradient(145deg,rgba(5,18,31,.99),rgba(2,9,15,.995))!important;
          box-shadow:0 28px 90px rgba(0,0,0,.58),0 0 40px rgba(25,217,255,.08)!important;
          overflow:hidden!important;
        }
        div[role="dialog"] [data-testid="stDialog"]{
          max-height:88vh!important;
        }
        .ai-modal-status{
          display:flex;align-items:center;gap:10px;flex-wrap:wrap;
          margin:-2px 0 10px;padding:10px 12px;border-radius:16px;
          border:1px solid rgba(25,217,255,.16);
          background:rgba(8,31,50,.72);
        }
        .ai-modal-avatar{
          width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;
          background:linear-gradient(135deg,#087FF5,#18DFA5);color:white;font-size:18px;
          box-shadow:0 0 20px rgba(25,217,255,.24);
        }
        .ai-modal-status-copy{line-height:1.15}
        .ai-modal-status-copy strong{display:block;color:#F5FAFF;font-size:.88rem}
        .ai-modal-status-copy span{color:#9FC4D8;font-size:.68rem}
        .ai-online-dot{width:8px;height:8px;border-radius:50%;background:#18DFA5;box-shadow:0 0 10px rgba(24,223,165,.72)}

        .st-key-ai_chat_modal_shell{
          position:relative!important;
          min-height:470px!important;
          max-height:64vh!important;
          overflow-y:auto!important;
          padding:12px 10px 90px!important;
          margin-top:8px!important;
          border:1px solid rgba(25,217,255,.12)!important;
          border-radius:20px!important;
          background:
            radial-gradient(circle at 18% 12%,rgba(24,223,165,.035),transparent 30%),
            linear-gradient(180deg,rgba(2,12,21,.82),rgba(3,15,26,.94))!important;
          scrollbar-width:thin;
          scrollbar-color:rgba(25,217,255,.35) transparent;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatMessage"]{
          width:fit-content!important;
          max-width:min(78%,760px)!important;
          margin:8px 0!important;
          padding:10px 13px!important;
          border-radius:18px 18px 18px 5px!important;
          border:1px solid rgba(25,217,255,.15)!important;
          background:linear-gradient(145deg,rgba(12,37,57,.96),rgba(7,24,39,.98))!important;
          box-shadow:0 8px 20px rgba(0,0,0,.18)!important;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]){
          margin-left:auto!important;
          border-radius:18px 18px 5px 18px!important;
          border-color:rgba(24,223,165,.24)!important;
          background:linear-gradient(135deg,#0A6F60,#0D8A72)!important;
          box-shadow:0 8px 22px rgba(0,0,0,.18),0 0 18px rgba(24,223,165,.06)!important;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatMessage"] p{
          color:#F4FAFF!important;
          line-height:1.5!important;
          margin-bottom:.15rem!important;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatMessageAvatarUser"],
        .st-key-ai_chat_modal_shell [data-testid="stChatMessageAvatarAssistant"]{
          transform:scale(.86);
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatInput"]{
          position:sticky!important;
          bottom:0!important;
          z-index:20!important;
          margin-top:18px!important;
          border-radius:999px!important;
          border:1px solid rgba(25,217,255,.24)!important;
          background:rgba(6,24,39,.96)!important;
          box-shadow:0 -10px 32px rgba(2,9,15,.46),0 8px 24px rgba(0,0,0,.22)!important;
          backdrop-filter:blur(16px)!important;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatInput"] textarea{
          min-height:48px!important;
          color:#F5FAFF!important;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatInput"] textarea::placeholder{color:#7896AA!important}

        @media(max-width:768px){
          div[role="dialog"]{width:98vw!important;max-width:98vw!important}
          div[role="dialog"] > div{border-radius:18px!important}
          .st-key-ai_chat_modal_shell{min-height:58vh!important;max-height:68vh!important;padding:8px 6px 84px!important}
          .st-key-ai_chat_modal_shell [data-testid="stChatMessage"]{max-width:90%!important;padding:9px 11px!important}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    top_left, top_right = st.columns([3.3, 1.15])
    with top_left:
        mode_label = "IA Personalizada • Premium" if personalized else "IA Padrão • Gratuita"
        st.markdown(
            f"""
            <div class="ai-modal-status">
              <div class="ai-modal-avatar">🤖</div>
              <div class="ai-modal-status-copy">
                <strong>RENOVA IA Financeira</strong>
                <span>{mode_label} • pronta para analisar e executar</span>
              </div>
              <div class="ai-online-dot" title="Online"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top_right:
        if st.button("＋ Nova conversa", key="ai_new_conversation", use_container_width=True):
            for key in ["ai_messages", "ai_pending_action", "ai_pending_command", "ai_pending_context", "ai_last_error"]:
                st.session_state.pop(key, None)
            _ensure_ai_messages()
            st.rerun(scope="fragment")

    if personalized:
        action_left, action_right = st.columns([2.4, 1])
        with action_left:
            st.caption("🟢 Online • memória e treinamentos personalizados ativos nesta conta.")
        with action_right:
            st.page_link("pages/Treinamento_IA.py", label="🧠 Treinar minha IA", use_container_width=True)
    else:
        action_left, action_right = st.columns([2.25, 1])
        with action_left:
            st.caption("🟢 Online • lançamentos, consultas, análises e gestão essencial disponíveis gratuitamente.")
        with action_right:
            if st.button("🧠 Personalizar IA", key="modal_upgrade_training", use_container_width=True):
                st.session_state.nav_page = "Assinar RENOVA IA"
                st.rerun()

    with st.container(key="ai_chat_modal_shell"):
        render_ai_chat("ai_modal_input", fragment_rerun=True)


def render_ai() -> None:
    personalized = has_personalized_ai_training_access()
    hero(
        "RENOVA IA <strong>Financeira</strong>",
        "Converse com sua gestão financeira. A IA Padrão gratuita já executa lançamentos, consultas e análises.",
    )
    if personalized:
        st.success("🧠 IA Personalizada ativa — seus treinamentos, regras e memória privada podem ser usados pelo chat.")
        st.page_link("pages/Treinamento_IA.py", label="Treinar minha IA", icon="🧠", use_container_width=True)
    else:
        st.info(
            "🤖 **IA Padrão gratuita ativa.** Ela já sabe criar receitas e despesas, entender vencimentos, "
            "consultar seus números, analisar urgências e executar a gestão essencial. "
            "O treinamento com regras próprias e materiais é exclusivo da assinatura."
        )
        if st.button("🧠 Quero personalizar minha IA", key="page_upgrade_training", use_container_width=True):
            st.session_state.nav_page = "Assinar RENOVA IA"
            st.rerun()
    render_ai_chat("ai_page_input")


def render_sidebar_profile() -> None:
    user = current_user()
    if not user:
        return
    metadata = getattr(user, "user_metadata", {}) or {}
    email = str(getattr(user, "email", "") or "Usuário RENOVA")
    full_name = str(metadata.get("full_name") or "").strip() or email.split("@")[0].replace(".", " ").title()
    avatar_url = str(metadata.get("avatar_url") or metadata.get("picture") or "").strip()
    initials = "".join(part[0] for part in full_name.split()[:2] if part).upper() or "R"

    uid = session_user_id()
    owner = False
    ai_active = False
    if REAL_MODE and uid:
        try:
            owner = is_owner(uid)
            ai_active = owner or has_active_ai_subscription(uid)
        except Exception:
            pass

    role_label = "Dono • Acesso Global" if owner else "Usuário RENOVA"
    plan_label = "IA Personalizada • Premium" if ai_active else "IA Padrão • Gratuito"
    avatar_html = (
        f'<img class="sidebar-profile-avatar-img" src="{escape(avatar_url)}" alt="Foto de perfil" />'
        if avatar_url.startswith(("https://", "http://"))
        else f'<div class="sidebar-profile-avatar">{escape(initials)}</div>'
    )

    st.markdown(
        f"""
        <style>
        .sidebar-profile-card{{
          margin:6px 4px 16px;padding:14px;border-radius:18px;
          border:1px solid rgba(0,174,239,.24);
          background:linear-gradient(145deg,rgba(5,24,38,.94),rgba(2,9,15,.98));
          box-shadow:0 12px 30px rgba(0,0,0,.28);
        }}
        .sidebar-profile-top{{display:flex;align-items:center;gap:11px}}
        .sidebar-profile-avatar,.sidebar-profile-avatar-img{{
          width:48px;height:48px;border-radius:50%;flex:0 0 48px;
          border:2px solid rgba(255,215,90,.72);box-shadow:0 0 18px rgba(0,174,239,.20);
        }}
        .sidebar-profile-avatar{{display:flex;align-items:center;justify-content:center;
          background:linear-gradient(135deg,#073454,#0A1620);color:#FFE477;font-weight:950;font-size:1rem}}
        .sidebar-profile-avatar-img{{object-fit:cover;background:#06131F}}
        .sidebar-profile-name{{color:#fff;font-weight:950;font-size:.92rem;line-height:1.1}}
        .sidebar-profile-email{{color:#94B5C7;font-size:.66rem;margin-top:4px;word-break:break-all}}
        .sidebar-profile-chips{{display:flex;gap:6px;flex-wrap:wrap;margin-top:11px}}
        .sidebar-profile-chip{{padding:4px 7px;border-radius:999px;background:rgba(0,174,239,.07);
          border:1px solid rgba(0,174,239,.22);color:#AEEBFF;font-size:.55rem;font-weight:850}}
        .sidebar-profile-chip.gold{{color:#FFE477;border-color:rgba(255,215,90,.28);background:rgba(255,215,90,.06)}}
        </style>
        <div class="sidebar-profile-card">
          <div class="sidebar-profile-top">
            {avatar_html}
            <div>
              <div class="sidebar-profile-name">{escape(full_name)}</div>
              <div class="sidebar-profile-email">{escape(email)}</div>
            </div>
          </div>
          <div class="sidebar-profile-chips">
            <span class="sidebar-profile-chip">{escape(role_label)}</span>
            <span class="sidebar-profile-chip gold">{escape(plan_label)}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


NAV_PAGES = [
    "Dashboard",
    "Lançamentos",
    "Categorias",
    "Contas",
    "Cartões",
    "Orçamentos",
    "Análises",
    "Relatórios",
    "RENOVA IA",
    "Treinamento IA",
    "Assinar RENOVA IA",
]

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Dashboard"


def render_mobile_modules_menu() -> None:
    """Menu mobile nativo e sempre visível, sem depender de JavaScript injetado."""
    mobile_icons = {
        "Dashboard": "🏠",
        "Lançamentos": "💸",
        "Categorias": "🏷️",
        "Contas": "🏦",
        "Cartões": "💳",
        "Orçamentos": "🎯",
        "Análises": "📊",
        "Relatórios": "📄",
        "RENOVA IA": "🤖",
        "Treinamento IA": "🧠",
        "Assinar RENOVA IA": "⭐",
    }
    current = str(st.session_state.get("nav_page") or "Dashboard")
    current_icon = mobile_icons.get(current, "•")

    with st.container(key="renova_fin_mobile_nav"):
        with st.popover(
            f"☰  MÓDULOS  •  {current_icon} {current}",
            use_container_width=True,
        ):
            st.markdown("**NAVEGAÇÃO RENOVA FINANÇAS**")
            st.caption("Escolha o módulo que deseja abrir.")
            for destination in NAV_PAGES:
                icon = mobile_icons.get(destination, "•")
                if st.button(
                    f"{icon}  {destination}",
                    key=f"mobile_module_{destination}",
                    use_container_width=True,
                    type="primary" if destination == current else "secondary",
                ):
                    st.session_state.nav_page = destination
                    st.session_state._last_nav_page = destination
                    st.rerun()


render_mobile_modules_menu()

with st.sidebar:
    brand_block()
    render_sidebar_profile()
    st.caption("MENU PRINCIPAL")
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
        user = current_user()
        if user:
            st.caption(f"Sistema conectado • Build {APP_BUILD}")
        if st.button("Sair", use_container_width=True):
            sign_out()
            st.rerun()
    else:
        st.warning("Modo demonstração")
        st.caption("Configure SUPABASE_URL e SUPABASE_PUBLISHABLE_KEY no Streamlit Secrets.")

if page == "Treinamento IA":
    st.switch_page("pages/Treinamento_IA.py")

pages = {
    "Dashboard": render_dashboard,
    "Lançamentos": render_transactions,
    "Categorias": render_categories,
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
    open_ai_dialog()
