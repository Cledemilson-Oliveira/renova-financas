from __future__ import annotations

import re
from html import escape

import streamlit as st

from src.mercado_pago_checkout import create_subscription_checkout
from src.repository import bootstrap_user, get_ai_plan, has_active_ai_subscription
from src.supabase_client import (
    current_user,
    is_authenticated,
    is_configured,
    sign_in,
    sign_up,
)
from src.theme import apply_renova_theme, brand_block


st.set_page_config(
    page_title="Checkout RENOVA IA • Minhas Finanças",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_renova_theme()

if is_authenticated():
    with st.sidebar:
        brand_block()
        st.page_link("pages/Assinar_RENOVA_IA.py", label="← Voltar à oferta", use_container_width=True)
else:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapseButton"]{display:none!important}
        [data-testid="stMainBlockContainer"]{max-width:980px!important;margin:0 auto!important}
        </style>
        """,
        unsafe_allow_html=True,
    )

if not is_configured():
    st.error("O sistema de pagamento ainda não está disponível neste ambiente.")
    st.stop()

try:
    plan = get_ai_plan() or {}
except Exception:
    plan = {}
price = float(plan.get("price") or 9.90)
price_label = f"{price:.2f}".replace(".", ",")

st.markdown(
    f"""
    <section class="renova-hero">
      <h1>Finalize sua <strong>RENOVA IA Personal</strong></h1>
      <p>R$ {price_label}/mês • informe seus dados abaixo e siga para o ambiente seguro do Mercado Pago.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.info("🔐 O Minhas Finanças não armazena os dados do seu cartão. O pagamento é concluído no Mercado Pago.")


def _normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if len(digits) in {10, 11}:
        return f"+55{digits}"
    if len(digits) in {12, 13}:
        return f"+{digits}"
    return ""


def _prepare_checkout() -> None:
    try:
        with st.spinner("Preparando seu checkout seguro..."):
            checkout = create_subscription_checkout("renova_ia")
        if checkout.get("already_active"):
            st.session_state.pop("renova_subscription_checkout_url", None)
            st.session_state.renova_subscription_already_active = True
            return
        checkout_url = str(checkout.get("checkout_url") or "").strip()
        if not checkout_url:
            raise RuntimeError("O Mercado Pago não devolveu o endereço do checkout.")
        st.session_state.renova_subscription_checkout_url = checkout_url
    except Exception:
        raise


if not is_authenticated():
    st.markdown("## Dados da assinatura")
    st.caption("Esses dados criam seu acesso ao Minhas Finanças como parte da contratação. Não existe uma etapa separada de conta grátis neste fluxo.")

    with st.form("subscription_identity_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("Nome completo", placeholder="Seu nome")
            email = st.text_input("E-mail", placeholder="voce@email.com")
            phone = st.text_input("Celular / WhatsApp", placeholder="(14) 99999-9999")
        with c2:
            password = st.text_input("Senha de acesso", type="password", placeholder="Mínimo de 8 caracteres")
            confirm = st.text_input("Confirmar senha", type="password", placeholder="Repita a senha")
        accepted = st.checkbox("Concordo com a criação do meu acesso e com o início da contratação mensal.")
        submitted = st.form_submit_button(
            f"CONTINUAR PARA O PAGAMENTO SEGURO • R$ {price_label}/MÊS",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        clean_name = " ".join(full_name.split()).strip()
        clean_email = email.strip().lower()
        normalized_phone = _normalize_phone(phone)

        if len(clean_name) < 2:
            st.error("Informe seu nome completo.")
        elif not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", clean_email):
            st.error("Informe um e-mail válido.")
        elif not normalized_phone:
            st.error("Informe um celular/WhatsApp válido com DDD.")
        elif len(password) < 8:
            st.error("Use uma senha com pelo menos 8 caracteres.")
        elif password != confirm:
            st.error("As senhas não conferem.")
        elif not accepted:
            st.error("Confirme os dados da contratação para continuar.")
        else:
            response = None
            try:
                # Se o cliente já possui acesso, a mesma tela funciona como identificação segura.
                response = sign_in(clean_email, password)
            except Exception:
                try:
                    response = sign_up(clean_email, password, clean_name, normalized_phone)
                except Exception as exc:
                    text = str(exc).lower()
                    if "already registered" in text or "user_already_exists" in text:
                        st.error("Este e-mail já possui acesso. Confira a senha informada para continuar a assinatura.")
                    else:
                        st.error("Não foi possível validar seus dados para a assinatura. Tente novamente em instantes.")

            if response is not None:
                if getattr(response, "session", None) is None:
                    st.warning("Confirme seu e-mail para validar o acesso. Depois, volte a este checkout para concluir a assinatura.")
                else:
                    user = current_user()
                    if user:
                        try:
                            bootstrap_user(user)
                        except Exception:
                            pass
                    try:
                        _prepare_checkout()
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Não foi possível abrir o checkout agora: {exc}")
    st.stop()


user = current_user()
uid = str(user.id) if user and getattr(user, "id", None) else ""

try:
    if uid and has_active_ai_subscription(uid):
        st.success("✅ Sua RENOVA IA Personal já está ativa. Não é necessário pagar novamente.")
        st.page_link("app.py", label="Ir para o Minhas Finanças", icon="🏠", use_container_width=True)
        st.stop()
except Exception:
    pass

checkout_url = str(st.session_state.get("renova_subscription_checkout_url") or "").strip()
if checkout_url:
    safe_url = escape(checkout_url, quote=True)
    st.success("Tudo certo com seus dados. Seu checkout está pronto.")
    st.markdown(
        f'<a href="{safe_url}" target="_self" rel="noopener" '
        'style="display:flex;align-items:center;justify-content:center;min-height:56px;'
        'border-radius:16px;text-decoration:none;font-weight:950;font-size:1.02rem;'
        'background:linear-gradient(112deg,#087FF5,#19D9FF 50%,#7457FF);color:#fff;'
        'border:1px solid rgba(25,217,255,.72);box-shadow:0 14px 36px rgba(25,217,255,.18);margin-top:10px;">'
        'ABRIR CHECKOUT SEGURO NO MERCADO PAGO →</a>',
        unsafe_allow_html=True,
    )
    st.caption("Depois da confirmação do Mercado Pago, o sistema libera automaticamente os recursos da RENOVA IA Personal.")
else:
    email = str(getattr(user, "email", "") or "") if user else ""
    st.markdown("## Confirmar contratação")
    if email:
        st.caption(f"A assinatura será vinculada ao acesso {email}.")
    if st.button(
        f"ABRIR CHECKOUT • R$ {price_label}/MÊS",
        type="primary",
        use_container_width=True,
    ):
        try:
            _prepare_checkout()
            st.rerun()
        except Exception as exc:
            st.error(f"Não foi possível abrir o checkout agora: {exc}")

st.caption("Você pode voltar à oferta antes de concluir o pagamento. Nenhuma cobrança é feita sem confirmação no Mercado Pago.")
