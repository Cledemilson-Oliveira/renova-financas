from __future__ import annotations

import pandas as pd
import streamlit as st

from src.access import ROLE_LABELS, STATUS_LABELS, get_current_access, update_user_access
from src.supabase_client import current_user, is_authenticated, is_configured, sign_out
from src.theme import apply_renova_theme, brand_block
from src.user_admin import (
    list_owner_users,
    send_password_reset,
    set_user_plan,
    update_user_profile,
    whatsapp_url,
)


st.set_page_config(
    page_title="Administração • RENOVA Finanças",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_renova_theme()


if not is_configured() or not is_authenticated():
    st.error("Faça login no RENOVA Finanças antes de acessar a administração.")
    st.page_link("app.py", label="Voltar para o login", icon="↩️")
    st.stop()

user = current_user()
user_id = str(user.id)

try:
    access = get_current_access(user_id)
except Exception:
    st.error("Não foi possível validar suas permissões agora.")
    st.stop()

if not access or access.get("role") != "dono" or access.get("status") != "ativo":
    st.error("Área restrita ao dono do sistema.")
    st.page_link("app.py", label="Voltar ao financeiro", icon="↩️")
    st.stop()


with st.sidebar:
    brand_block()
    st.success("Modo Dono • Acesso Global")
    st.caption(str(getattr(user, "email", "Dono autenticado")))
    st.page_link("app.py", label="Voltar ao RENOVA Finanças", icon="🏠", use_container_width=True)
    if st.button("Sair", use_container_width=True):
        sign_out()
        st.switch_page("app.py")

st.markdown(
    """
    <div class="renova-hero">
      <h1>Gestão de <strong>Usuários</strong></h1>
      <p>Contatos, planos, acessos e suporte em uma única área da conta dono.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    rows = list_owner_users()
except Exception as exc:
    st.error("Não foi possível carregar a gestão de usuários agora.")
    st.caption(str(exc))
    st.stop()

users = pd.DataFrame(rows)
if users.empty:
    st.info("Ainda não existem usuários cadastrados para gerenciamento.")
    st.stop()

active_count = int((users["status"] == "ativo").sum())
suspended_count = int((users["status"] == "suspenso").sum())
premium_count = int((users["plan"] == "RENOVA IA Personal").sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Usuários", len(users))
c2.metric("Ativos", active_count)
c3.metric("RENOVA IA Personal", premium_count)
c4.metric("Suspensos", suspended_count)

st.subheader("Visão geral")
view = users[["full_name", "email", "phone", "plan", "role", "status", "created_at"]].copy()
view["role"] = view["role"].map(ROLE_LABELS).fillna(view["role"])
view["status"] = view["status"].map(STATUS_LABELS).fillna(view["status"])
view.columns = ["Nome", "E-mail", "WhatsApp", "Plano", "Nível", "Status", "Criado em"]
st.dataframe(view, use_container_width=True, hide_index=True)

editable = users[users["role"] != "dono"].copy()
st.subheader("Gerenciar usuário")

if editable.empty:
    st.info("Nenhum usuário editável no momento. O acesso do dono é protegido pelo sistema.")
else:
    options = {}
    for row in editable.to_dict("records"):
        display_name = row.get("full_name") or row.get("email") or row.get("user_id")
        options[f"{display_name} • {row.get('plan', 'Gratuito')} • {STATUS_LABELS.get(row.get('status'), row.get('status'))}"] = row

    selected_label = st.selectbox("Usuário", list(options.keys()))
    selected = options[selected_label]
    selected_user_id = str(selected["user_id"])

    profile_tab, access_tab, security_tab = st.tabs(["👤 Perfil e contato", "💳 Plano e acesso", "🔐 Segurança"])

    with profile_tab:
        with st.form("owner_profile_form"):
            p1, p2 = st.columns(2)
            with p1:
                full_name = st.text_input("Nome", value=str(selected.get("full_name") or ""))
            with p2:
                phone = st.text_input("Celular / WhatsApp", value=str(selected.get("phone") or ""), placeholder="(14) 99999-9999")
            profile_submit = st.form_submit_button("Salvar contato", type="primary", use_container_width=True)

        if profile_submit:
            try:
                update_user_profile(selected_user_id, full_name, phone)
                st.success("Perfil e contato atualizados.")
                st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível atualizar o contato: {exc}")

        contact_cols = st.columns(2)
        wa = whatsapp_url(str(selected.get("phone") or ""), str(selected.get("full_name") or ""))
        with contact_cols[0]:
            if wa:
                st.link_button("💬 Falar no WhatsApp", wa, use_container_width=True)
            else:
                st.button("💬 WhatsApp não cadastrado", disabled=True, use_container_width=True)
        with contact_cols[1]:
            email_value = str(selected.get("email") or "")
            if email_value:
                st.link_button("✉️ Enviar e-mail", f"mailto:{email_value}", use_container_width=True)

    with access_tab:
        current_plan = "RENOVA IA Personal" if selected.get("plan") == "RENOVA IA Personal" else "Gratuito"
        with st.form("owner_access_plan_form"):
            a1, a2, a3 = st.columns(3)
            with a1:
                role = st.selectbox(
                    "Nível de acesso",
                    ["usuario", "admin"],
                    index=0 if selected.get("role") == "usuario" else 1,
                    format_func=lambda value: ROLE_LABELS[value],
                )
            with a2:
                status = st.selectbox(
                    "Status",
                    ["ativo", "suspenso"],
                    index=0 if selected.get("status") == "ativo" else 1,
                    format_func=lambda value: STATUS_LABELS[value],
                )
            with a3:
                plan = st.selectbox(
                    "Plano",
                    ["Gratuito", "RENOVA IA Personal"],
                    index=0 if current_plan == "Gratuito" else 1,
                )

            st.caption(
                "Alterações manuais da conta dono não interferem nos lançamentos financeiros. "
                "Ao ativar RENOVA IA Personal manualmente, o preço vigente do plano fica registrado para a assinatura."
            )
            access_submit = st.form_submit_button("Salvar acesso e plano", type="primary", use_container_width=True)

        if access_submit:
            try:
                update_user_access(selected_user_id, role, status)
                set_user_plan(selected_user_id, plan)
                st.success("Acesso e plano atualizados com sucesso.")
                st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível atualizar o usuário: {exc}")

        if selected.get("locked_price") is not None:
            st.info(f"🔒 Preço registrado nesta assinatura: R$ {float(selected['locked_price']):.2f}/mês".replace(".", ","))

    with security_tab:
        st.markdown("### Recuperação de senha")
        st.write(
            "Por segurança, a conta dono não visualiza nem define a senha atual do usuário. "
            "O suporte envia um link oficial de recuperação para o e-mail cadastrado."
        )
        if st.button("📧 Enviar recuperação de senha", use_container_width=True, type="primary"):
            try:
                send_password_reset(str(selected.get("email") or ""))
                st.success("E-mail de recuperação solicitado ao Supabase.")
            except Exception as exc:
                st.error(f"Não foi possível solicitar a recuperação: {exc}")

st.divider()
st.caption(
    "Proteção do dono: a conta dono não pode ser rebaixada ou suspensa por esta interface. "
    "Senhas nunca são exibidas no painel administrativo."
)
