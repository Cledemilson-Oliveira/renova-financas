from __future__ import annotations

import pandas as pd
import streamlit as st

from src.access import ROLE_LABELS, STATUS_LABELS, get_current_access, list_user_access, update_user_access
from src.supabase_client import current_user, is_authenticated, is_configured, sign_out
from src.theme import apply_renova_theme, brand_block


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
    st.success("Modo Dono")
    st.caption(str(getattr(user, "email", "Dono autenticado")))
    st.page_link("app.py", label="Voltar ao RENOVA Finanças", icon="🏠", use_container_width=True)
    if st.button("Sair", use_container_width=True):
        sign_out()
        st.switch_page("app.py")

st.markdown(
    """
    <div class="renova-hero">
      <h1>Central do <strong>Dono</strong></h1>
      <p>Gerencie acessos manualmente sem interferir nas automações financeiras do usuário.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    rows = list_user_access()
except Exception:
    st.error("Não foi possível carregar a lista de usuários.")
    st.stop()

users = pd.DataFrame(rows)
if users.empty:
    st.info("Ainda não existem usuários cadastrados para gerenciamento.")
    st.stop()

active_count = int((users["status"] == "ativo").sum())
suspended_count = int((users["status"] == "suspenso").sum())
admin_count = int((users["role"] == "admin").sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Usuários", len(users))
c2.metric("Ativos", active_count)
c3.metric("Suspensos", suspended_count)
c4.metric("Administradores", admin_count)

st.subheader("Acessos cadastrados")
view = users[["email", "role", "status", "created_at"]].copy()
view["role"] = view["role"].map(ROLE_LABELS).fillna(view["role"])
view["status"] = view["status"].map(STATUS_LABELS).fillna(view["status"])
view.columns = ["E-mail", "Nível", "Status", "Criado em"]
st.dataframe(view, use_container_width=True, hide_index=True)

editable = users[users["role"] != "dono"].copy()
st.subheader("Gerenciar acesso manualmente")

if editable.empty:
    st.info("Nenhum usuário editável no momento. O acesso do dono é protegido pelo sistema.")
else:
    options = {
        f"{row['email']} • {ROLE_LABELS.get(row['role'], row['role'])} • {STATUS_LABELS.get(row['status'], row['status'])}": row
        for row in editable.to_dict("records")
    }
    selected_label = st.selectbox("Usuário", list(options.keys()))
    selected = options[selected_label]

    with st.form("access_management_form"):
        left, right = st.columns(2)
        with left:
            role = st.selectbox(
                "Nível de acesso",
                ["usuario", "admin"],
                index=0 if selected["role"] == "usuario" else 1,
                format_func=lambda value: ROLE_LABELS[value],
            )
        with right:
            status = st.selectbox(
                "Status",
                ["ativo", "suspenso"],
                index=0 if selected["status"] == "ativo" else 1,
                format_func=lambda value: STATUS_LABELS[value],
            )

        st.caption(
            "Administrador recebe nível administrativo do RENOVA Finanças. "
            "Suspender bloqueia o acesso aos dados financeiros sem excluir o cadastro ou o histórico."
        )
        submitted = st.form_submit_button("Salvar alteração", use_container_width=True)

    if submitted:
        try:
            update_user_access(str(selected["user_id"]), role, status)
            st.success("Acesso atualizado com sucesso.")
            st.rerun()
        except Exception as exc:
            st.error(f"Não foi possível atualizar o acesso: {exc}")

st.divider()
st.caption(
    "Proteção do dono: o papel 'dono' não pode ser transferido, rebaixado ou suspenso por esta interface."
)
