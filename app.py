from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data import (
    CATEGORIES,
    brl,
    demo_accounts,
    demo_budgets,
    demo_cards,
    demo_transactions,
    financial_summary,
)
from src.supabase_client import is_configured
from src.theme import apply_renova_theme, brand_block


st.set_page_config(
    page_title="RENOVA Finanças",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_renova_theme()


if "transactions" not in st.session_state:
    st.session_state.transactions = demo_transactions()
if "accounts" not in st.session_state:
    st.session_state.accounts = demo_accounts()
if "cards" not in st.session_state:
    st.session_state.cards = demo_cards()
if "budgets" not in st.session_state:
    st.session_state.budgets = demo_budgets()


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


def render_dashboard() -> None:
    hero("Sua vida financeira, <strong>em um só lugar</strong>", "Visão rápida, inteligente e organizada para você decidir melhor.")
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
        chart_df = tx.copy().sort_values("data")
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
        expenses = tx[tx["tipo"] == "Despesa"].groupby("categoria", as_index=False)["valor"].sum()
        if not expenses.empty:
            fig = px.donut(expenses, names="categoria", values="valor", hole=.62)
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=True,
                margin=dict(l=0, r=0, t=20, b=0),
                height=360,
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Últimos lançamentos")
    latest = tx.sort_values("data", ascending=False).head(7).copy()
    latest["valor"] = latest["valor"].map(brl)
    st.dataframe(latest, use_container_width=True, hide_index=True)


def render_transactions() -> None:
    hero("Receitas e <strong>despesas</strong>", "Registre, categorize e acompanhe cada movimentação financeira.")
    with st.expander("➕ Novo lançamento", expanded=False):
        with st.form("new_transaction", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                dt = st.date_input("Data", value=date.today())
                kind = st.selectbox("Tipo", ["Receita", "Despesa"])
            with c2:
                category = st.selectbox("Categoria", CATEGORIES)
                account = st.selectbox("Conta", st.session_state.accounts["conta"].tolist())
            with c3:
                description = st.text_input("Descrição")
                value = st.number_input("Valor", min_value=0.0, step=10.0, format="%.2f")
            submitted = st.form_submit_button("Salvar lançamento", use_container_width=True)
            if submitted:
                if not description.strip() or value <= 0:
                    st.error("Informe uma descrição e um valor maior que zero.")
                else:
                    new_row = pd.DataFrame([[dt, kind, category, description.strip(), value, account]], columns=st.session_state.transactions.columns)
                    st.session_state.transactions = pd.concat([st.session_state.transactions, new_row], ignore_index=True)
                    st.success("Lançamento salvo.")
                    st.rerun()

    tx = st.session_state.transactions.copy().sort_values("data", ascending=False)
    f1, f2 = st.columns(2)
    with f1:
        type_filter = st.multiselect("Filtrar por tipo", ["Receita", "Despesa"], default=["Receita", "Despesa"])
    with f2:
        category_filter = st.multiselect("Filtrar por categoria", sorted(tx["categoria"].unique().tolist()))
    filtered = tx[tx["tipo"].isin(type_filter)]
    if category_filter:
        filtered = filtered[filtered["categoria"].isin(category_filter)]
    display = filtered.copy()
    display["valor"] = display["valor"].map(brl)
    st.dataframe(display, use_container_width=True, hide_index=True)


def render_accounts() -> None:
    hero("Gerencie suas <strong>contas</strong>", "Veja saldos e concentre sua estrutura financeira em uma única tela.")
    accounts = st.session_state.accounts.copy()
    total = float(accounts["saldo"].sum())
    c1, c2 = st.columns([1, 3])
    with c1:
        st.metric("Saldo consolidado", brl(total))
    with c2:
        st.caption("Conta corrente, conta digital, carteira e outras fontes de saldo.")
    view = accounts.copy()
    view["saldo"] = view["saldo"].map(brl)
    st.dataframe(view, use_container_width=True, hide_index=True)


def render_cards() -> None:
    hero("Controle todos os seus <strong>cartões</strong>", "Limite, fatura, fechamento e vencimento com leitura simples.")
    cards = st.session_state.cards.copy()
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
    hero("Orçamentos por <strong>categoria</strong>", "Defina limites e descubra antes quando uma categoria está saindo do controle.")
    budgets = st.session_state.budgets.copy()
    budgets["uso_%"] = (budgets["realizado"] / budgets["orcamento"] * 100).round(1)
    for _, row in budgets.iterrows():
        c1, c2 = st.columns([2.5, 1])
        with c1:
            st.write(f"**{row['categoria']}**")
            st.progress(min(float(row["uso_%"]), 100.0) / 100, text=f"{row['uso_%']:.0f}% utilizado")
        with c2:
            st.write(f"{brl(row['realizado'])} / {brl(row['orcamento'])}")


def render_analysis() -> None:
    hero("Gráficos avançados para <strong>análise</strong>", "Entenda padrões, categorias e pontos de atenção sem depender de planilhas externas.")
    tx = st.session_state.transactions.copy()
    expenses = tx[tx["tipo"] == "Despesa"].groupby("categoria", as_index=False)["valor"].sum().sort_values("valor", ascending=False)
    incomes = tx[tx["tipo"] == "Receita"].groupby("categoria", as_index=False)["valor"].sum().sort_values("valor", ascending=False)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(expenses, x="valor", y="categoria", orientation="h", title="Ranking de despesas")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=390)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(incomes, x="categoria", y="valor", title="Origem das receitas")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=390)
        st.plotly_chart(fig, use_container_width=True)


def render_reports() -> None:
    hero("Relatórios e <strong>exportação</strong>", "Prepare seus dados para análise, prestação de contas e tomada de decisão.")
    tx = st.session_state.transactions.copy().sort_values("data", ascending=False)
    report = tx.copy()
    report["valor"] = report["valor"].map(brl)
    st.dataframe(report, use_container_width=True, hide_index=True)
    csv = tx.to_csv(index=False).encode("utf-8-sig")
    st.download_button("Baixar CSV", data=csv, file_name="renova-financas-lancamentos.csv", mime="text/csv", use_container_width=True)
    st.caption("PDF e XLSX entram na próxima etapa do módulo de relatórios.")


def render_ai() -> None:
    hero("RENOVA IA <strong>Financeira</strong>", "Leitura automática dos números para destacar riscos, urgências e oportunidades.")
    tx = st.session_state.transactions.copy()
    summary = financial_summary(tx, st.session_state.accounts)
    budgets = st.session_state.budgets.copy()
    budgets["uso"] = budgets["realizado"] / budgets["orcamento"]

    alerts = []
    if summary["resultado"] < 0:
        alerts.append(("🔴", "Resultado negativo", f"As despesas superaram as receitas em {brl(abs(summary['resultado']))}."))
    if summary["taxa_economia"] < 10 and summary["receitas"] > 0:
        alerts.append(("🟠", "Margem de segurança baixa", f"A taxa de economia está em {summary['taxa_economia']:.1f}%."))
    for _, row in budgets[budgets["uso"] >= .85].iterrows():
        alerts.append(("🟡", f"Orçamento de {row['categoria']} em atenção", f"Já foi utilizado {row['uso']*100:.0f}% do limite definido."))
    if not alerts:
        alerts.append(("🟢", "Situação controlada", "Nenhuma urgência automática foi detectada nos dados atuais."))

    for icon, title, text in alerts:
        st.markdown(f"### {icon} {title}")
        st.write(text)
    st.info("A conversa com IA e execução de ações financeiras será conectada depois ao backend seguro. Nenhuma ação financeira automática será feita sem pedido explícito do usuário.")


brand_block()
with st.sidebar:
    st.caption("GESTÃO FINANCEIRA")
    page = st.radio(
        "Navegação",
        [
            "Dashboard",
            "Lançamentos",
            "Contas",
            "Cartões",
            "Orçamentos",
            "Análises",
            "Relatórios",
            "RENOVA IA",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    if is_configured():
        st.success("Supabase conectado")
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
}
pages[page]()
