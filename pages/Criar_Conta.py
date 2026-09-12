from __future__ import annotations

import streamlit as st


st.set_page_config(
    page_title="RENOVA Finanças",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Rota legada preservada apenas para não quebrar links antigos.
# Cadastro gratuito existe exclusivamente na tela inicial/login do aplicativo.
plan_param = str(st.query_params.get("plan", "free") or "free").lower()
if plan_param == "premium":
    st.switch_page("pages/Assinar_RENOVA_IA.py")

st.switch_page("app.py")
