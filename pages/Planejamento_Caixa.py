from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from src.cash_projection import build_cash_projection, projection_insights
from src.data import brl
from src.global_ai_modal import render_global_ai_assistant
from src.recurring_finance import (
    SCHEDULE_FIXED,
    SCHEDULE_INSTALLMENTS,
    create_recurring_plan,
    installment_amount,
    list_recurring_plans,
    materialize_due_recurring,
    set_recurring_active,
)
from src.repository import fetch_financial_data
from src.supabase_client import current_user, is_authenticated, is_configured
from src.theme import apply_renova_theme, brand_block


st.set_page_config(
    page_title="Planejamento de Caixa • RENOVA Finanças",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_renova_theme()


if not is_configured() or not is_authenticated():
    st.error("Faça login no RENOVA Finanças para acessar o planejamento de caixa.")
    st.page_link("app.py", label="Voltar para o login", icon="↩️")
    st.stop()

user = current_user()
user_id = str(user.id)

with st.sidebar:
    brand_block()
    st.page_link("app.py", label="🏠 Voltar ao painel financeiro", use_container_width=True)


st.markdown(
    """
    <section class="renova-hero">
      <h1>📈 Planejamento de <strong>Caixa</strong></h1>
      <p>
        Cadastre contas e receitas uma única vez, controle parcelamentos automaticamente
        e antecipe como seu saldo pode evoluir nos próximos meses.
      </p>
    </section>
    """,
    unsafe_allow_html=True,
)

try:
    materialize_due_recurring(user_id)
    bundle = fetch_financial_data(user_id)
except Exception as exc:
    st.error(f"Não foi possível carregar o planejamento financeiro agora: {exc}")
    st.stop()

accounts = bundle.get("accounts", pd.DataFrame())
transactions = bundle.get("transactions", pd.DataFrame())
categories = bundle.get("categories", pd.DataFrame())
try:
    recurring = list_recurring_plans(user_id, include_inactive=True)
except Exception:
    recurring = bundle.get("recurring", pd.DataFrame())


def _account_options() -> dict[str, str]:
    if accounts is None or accounts.empty:
        return {}
    return {str(row["conta"]): str(row["id"]) for _, row in accounts.iterrows() if bool(row.get("ativo", True))}


def _category_options(kind: str) -> dict[str, str]:
    if categories is None or categories.empty:
        return {}
    frame = categories.copy()
    if "is_active" in frame.columns:
        frame = frame[frame["is_active"] == True]
    if "kind" in frame.columns:
        frame = frame[frame["kind"].isin([kind, "ambos"])]
    return {str(row["name"]): str(row["id"]) for _, row in frame.iterrows()}


def _render_recurring_form(kind: str) -> None:
    is_income = kind == "receita"
    noun = "receita" if is_income else "conta"
    noun_title = "Receita" if is_income else "Conta"
    icon = "💰" if is_income else "💸"

    account_map = _account_options()
    category_map = _category_options(kind)
    if not account_map:
        st.warning("Cadastre uma conta financeira antes de criar lançamentos recorrentes.")
        return
    if not category_map:
        st.warning(f"Cadastre pelo menos uma categoria de {'receita' if is_income else 'despesa'} antes de continuar.")
        return

    st.markdown(f"### {icon} Nova {noun}")
    st.caption(
        "Escolha **Fixa mensal** para valores que se repetem todos os meses, ou **Parcelada** para valores com quantidade definida de parcelas."
    )

    mode_label = st.radio(
        "Modalidade",
        ["Fixa mensal", "Parcelada"],
        horizontal=True,
        key=f"recurring_mode_{kind}",
    )
    schedule_type = SCHEDULE_FIXED if mode_label == "Fixa mensal" else SCHEDULE_INSTALLMENTS

    with st.form(f"recurring_form_{kind}", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            description = st.text_input(
                f"Descrição da {noun}",
                placeholder="Ex.: Aluguel" if not is_income else "Ex.: Salário",
                key=f"recurring_description_{kind}",
            )
            account_label = st.selectbox(
                "Conta de movimentação",
                list(account_map.keys()),
                key=f"recurring_account_{kind}",
            )
        with c2:
            category_label = st.selectbox(
                "Categoria",
                list(category_map.keys()),
                key=f"recurring_category_{kind}",
            )
            first_due = st.date_input(
                "Primeiro vencimento / recebimento",
                value=date.today(),
                key=f"recurring_first_due_{kind}",
            )

        monthly_value: float | None = None
        total_value: float | None = None
        installments: int | None = None

        if schedule_type == SCHEDULE_FIXED:
            monthly_value = st.number_input(
                f"Valor mensal da {noun}",
                min_value=0.0,
                step=10.0,
                format="%.2f",
                key=f"recurring_monthly_value_{kind}",
            )
            st.info(
                f"🔁 O RENOVA criará automaticamente esta {noun} em cada mês até você pausar a recorrência."
            )
        else:
            p1, p2 = st.columns(2)
            with p1:
                total_value = st.number_input(
                    "Valor total",
                    min_value=0.0,
                    step=10.0,
                    format="%.2f",
                    key=f"recurring_total_value_{kind}",
                )
            with p2:
                installments = int(
                    st.number_input(
                        "Quantidade de parcelas",
                        min_value=1,
                        max_value=360,
                        value=2,
                        step=1,
                        key=f"recurring_installments_{kind}",
                    )
                )
            if total_value and installments:
                parcel = installment_amount(total_value, installments)
                st.info(
                    f"🧾 {installments} parcelas • aproximadamente **{brl(float(parcel))} por mês** • total {brl(float(total_value))}. "
                    "A última parcela é ajustada automaticamente se houver diferença de centavos."
                )

        notes = st.text_input(
            "Observação (opcional)",
            placeholder="Ex.: reajusta todo janeiro, contrato cliente X...",
            key=f"recurring_notes_{kind}",
        )

        submitted = st.form_submit_button(
            f"{icon} CADASTRAR {noun_title.upper()} {mode_label.upper()}",
            use_container_width=True,
        )

        if submitted:
            try:
                create_recurring_plan(
                    user_id,
                    account_id=account_map[account_label],
                    category_id=category_map[category_label],
                    kind=kind,
                    description=description,
                    schedule_type=schedule_type,
                    first_due_date=first_due,
                    monthly_amount=monthly_value,
                    total_amount=total_value,
                    total_installments=installments,
                    notes=notes,
                )
                st.success(
                    f"{noun_title} cadastrada. O RENOVA já incluiu os compromissos aplicáveis no fluxo de caixa."
                )
                st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível cadastrar: {exc}")


def _render_projection() -> None:
    st.markdown("### 🔭 Análise de caixa a longo prazo")
    st.caption(
        "A projeção parte do saldo atual e soma receitas/despesas previstas, contas fixas e parcelas futuras sem contar duas vezes o que já foi pago."
    )

    horizon = st.select_slider(
        "Horizonte da análise",
        options=[3, 6, 12, 18, 24, 36, 48, 60],
        value=12,
        format_func=lambda value: f"{value} meses",
        key="cash_projection_horizon",
    )

    projection, summary = build_cash_projection(
        accounts=accounts,
        transactions=transactions,
        recurring=recurring,
        months=int(horizon),
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Saldo atual", brl(float(summary["saldo_atual"])))
    c2.metric("Receitas previstas", brl(float(summary["receitas_previstas"])))
    c3.metric("Despesas previstas", brl(float(summary["despesas_previstas"])))
    c4.metric("Saldo ao final", brl(float(summary["saldo_final"])))

    risk = str(summary.get("nivel_risco") or "estável")
    if risk == "crítico":
        st.error("🚨 **Risco crítico de caixa:** há pelo menos um mês com saldo projetado negativo.")
    elif risk == "atenção":
        st.warning("⚠️ **Atenção ao caixa:** o período termina abaixo do saldo atual, mesmo sem entrar no negativo.")
    else:
        st.success("✅ **Projeção estável:** com os dados cadastrados, o caixa permanece positivo no horizonte escolhido.")

    if not projection.empty:
        line = px.line(
            projection,
            x="periodo",
            y="saldo_projetado",
            markers=True,
            labels={"periodo": "Mês", "saldo_projetado": "Saldo projetado"},
            title="Evolução do saldo projetado",
        )
        line.update_layout(height=390, margin=dict(l=12, r=12, t=54, b=18))
        st.plotly_chart(line, use_container_width=True)

        flow = projection[["periodo", "receitas_previstas", "despesas_previstas"]].melt(
            id_vars="periodo",
            var_name="fluxo",
            value_name="valor",
        )
        flow["fluxo"] = flow["fluxo"].map(
            {"receitas_previstas": "Receitas", "despesas_previstas": "Despesas"}
        )
        bars = px.bar(
            flow,
            x="periodo",
            y="valor",
            color="fluxo",
            barmode="group",
            labels={"periodo": "Mês", "valor": "Valor", "fluxo": "Fluxo"},
            title="Entradas e saídas previstas",
        )
        bars.update_layout(height=360, margin=dict(l=12, r=12, t=54, b=18))
        st.plotly_chart(bars, use_container_width=True)

    st.markdown("### 🧭 Análise automática")
    for insight in projection_insights(summary):
        text = f"**{insight['title']}**\n\n{insight['message']}\n\n**Ação recomendada:** {insight['action']}"
        severity = insight.get("severity")
        if severity == "critica":
            st.error(text)
        elif severity == "atencao":
            st.warning(text)
        elif severity == "ok":
            st.success(text)
        else:
            st.info(text)

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Despesas fixas/mês", brl(float(summary.get("despesas_fixas_mensais") or 0)))
    d2.metric("Receitas fixas/mês", brl(float(summary.get("receitas_fixas_mensais") or 0)))
    d3.metric("Parcelas a pagar", brl(float(summary.get("parcelamentos_a_pagar") or 0)))
    d4.metric("Parcelas a receber", brl(float(summary.get("parcelamentos_a_receber") or 0)))

    if not projection.empty:
        st.markdown("### 📅 Projeção mês a mês")
        view = projection[
            ["periodo", "receitas_previstas", "despesas_previstas", "resultado_previsto", "saldo_projetado"]
        ].copy()
        view.columns = ["Mês", "Receitas", "Despesas", "Resultado", "Saldo projetado"]
        for column in ["Receitas", "Despesas", "Resultado", "Saldo projetado"]:
            view[column] = view[column].map(lambda value: brl(float(value)))
        st.dataframe(view, use_container_width=True, hide_index=True)


def _render_management() -> None:
    st.markdown("### 🔁 Contas e receitas automáticas")
    st.caption(
        "Pausar interrompe os próximos lançamentos automáticos. Lançamentos já gerados permanecem no histórico para não apagar sua movimentação."
    )

    if recurring is None or recurring.empty:
        st.info("Ainda não existem contas ou receitas recorrentes cadastradas.")
        return

    view = recurring.copy()
    view["Descrição"] = view["description"]
    view["Valor/mês"] = view["valor_ciclo"].map(lambda value: brl(float(value or 0)))
    view["Status"] = view["ativo"].map({True: "Ativa", False: "Pausada / concluída"})
    view["Próximo"] = view["proximo_vencimento"].map(
        lambda value: value.strftime("%d/%m/%Y") if isinstance(value, date) else "—"
    )
    view["Parcelas"] = view.apply(
        lambda row: (
            f"{int(row['parcelas_geradas'])}/{int(row['parcelas_total'])} geradas"
            if pd.notna(row.get("parcelas_total")) and row.get("parcelas_total")
            else "Mensal contínua"
        ),
        axis=1,
    )
    st.dataframe(
        view[["tipo", "modalidade", "Descrição", "categoria", "conta", "Valor/mês", "Parcelas", "Próximo", "Status"]].rename(
            columns={"tipo": "Tipo", "modalidade": "Modalidade", "categoria": "Categoria", "conta": "Conta"}
        ),
        use_container_width=True,
        hide_index=True,
    )

    options = {}
    for _, row in recurring.iterrows():
        label = f"{row.get('tipo')} • {row.get('description')} • {row.get('modalidade')}"
        options[label] = row

    selected_label = st.selectbox("Gerenciar recorrência", list(options.keys()), key="manage_recurring_select")
    selected = options[selected_label]
    active = bool(selected.get("ativo"))

    c1, c2 = st.columns([1, 2])
    with c1:
        action = "⏸️ Pausar" if active else "▶️ Reativar"
        if st.button(action, use_container_width=True, key="toggle_recurring_active"):
            try:
                set_recurring_active(user_id, str(selected["id"]), not active)
                st.success("Recorrência atualizada.")
                st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível atualizar: {exc}")
    with c2:
        if selected.get("schedule_type") == SCHEDULE_INSTALLMENTS:
            remaining = int(selected.get("parcelas_restantes") or 0)
            st.info(f"Restam **{remaining} parcela(s)** para este lançamento.")
        else:
            st.info("Esta recorrência mensal continua até ser pausada pelo usuário.")


projection_tab, expense_tab, income_tab, management_tab = st.tabs(
    [
        "📊 Projeção de caixa",
        "💸 Contas fixas / parceladas",
        "💰 Receitas fixas / parceladas",
        "🔁 Gerenciar recorrências",
    ]
)

with projection_tab:
    _render_projection()
with expense_tab:
    _render_recurring_form("despesa")
with income_tab:
    _render_recurring_form("receita")
with management_tab:
    _render_management()

render_global_ai_assistant(user_id)
