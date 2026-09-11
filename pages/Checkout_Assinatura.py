from __future__ import annotations

from html import escape

import streamlit as st

from src.mercado_pago_checkout import create_subscription_checkout
from src.repository import get_ai_plan, has_active_ai_subscription
from src.supabase_client import current_user, is_authenticated, is_configured
from src.theme import apply_renova_theme, brand_block


st.set_page_config(
    page_title="Assinatura RENOVA IA • Mercado Pago",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_renova_theme()


with st.sidebar:
    brand_block()
    st.page_link("app.py", label="Voltar ao RENOVA Finanças", icon="🏠")

st.markdown(
    """
    <section class="renova-hero">
      <h1>RENOVA IA <strong>Personalizada</strong></h1>
      <p>Finalize sua assinatura mensal com segurança pelo Mercado Pago.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

if not is_configured():
    st.error("O Supabase ainda não está configurado neste ambiente.")
    st.stop()

if not is_authenticated():
    st.session_state["nav_page"] = "Assinar RENOVA IA"
    st.switch_page("app.py")

user = current_user()
uid = str(user.id) if user and getattr(user, "id", None) else ""

try:
    if uid and has_active_ai_subscription(uid):
        st.success("✅ Sua RENOVA IA Personalizada já está ativa.")
        st.page_link("app.py", label="Ir para o painel", icon="🏠", use_container_width=True)
        st.stop()
except Exception:
    pass

plan = get_ai_plan() or {}
price = float(plan.get("price") or 9.90)

st.markdown(
    f"""
    <section class="ai-subscribe-gate">
      <div class="sales-eyebrow">ASSINATURA MENSAL</div>
      <h2>RENOVA IA Personalizada • <strong>R$ {price:.2f}/mês</strong></h2>
      <p>
        A cobrança é processada pelo Mercado Pago. O acesso personalizado só é
        liberado depois da confirmação recebida pelo webhook do provedor.
      </p>
      <div class="gate-benefits">
        <span>✓ Memória e regras personalizadas</span>
        <span>✓ Treinamento privado da sua conta</span>
        <span>✓ Gestão financeira por IA</span>
        <span>✓ Liberação automática após confirmação</span>
      </div>
    </section>
    """.replace(".", ",", 1),
    unsafe_allow_html=True,
)

st.info("🔐 Seus dados de pagamento não passam pelo RENOVA Finanças. O pagamento é concluído no ambiente do Mercado Pago.")

if st.button("💳 CONTINUAR PARA O MERCADO PAGO", type="primary", use_container_width=True):
    try:
        with st.spinner("Preparando sua assinatura..."):
            checkout = create_subscription_checkout("renova_ia")

        if checkout.get("already_active"):
            st.success("Sua assinatura já está ativa.")
            st.page_link("app.py", label="Voltar ao painel", icon="🏠", use_container_width=True)
        else:
            checkout_url = str(checkout.get("checkout_url") or "").strip()
            if not checkout_url:
                st.error("O Mercado Pago não devolveu o endereço do checkout.")
            else:
                safe_url = escape(checkout_url, quote=True)
                st.success("Checkout criado. Continue no Mercado Pago para concluir.")
                st.markdown(
                    f'<a href="{safe_url}" target="_self" rel="noopener" '
                    'style="display:flex;align-items:center;justify-content:center;min-height:52px;'
                    'border-radius:14px;text-decoration:none;font-weight:950;'
                    'background:linear-gradient(120deg,#061827,#07508a 65%,#0090f0);'
                    'color:#fff;border:1px solid rgba(247,214,100,.85);">'
                    'ABRIR CHECKOUT SEGURO →</a>',
                    unsafe_allow_html=True,
                )
    except Exception as exc:
        st.error(str(exc))
        st.caption(
            "Se a mensagem indicar credencial ausente, configure o Access Token do Mercado Pago "
            "somente nos segredos das Edge Functions do Supabase."
        )

st.caption("Você pode voltar ao painel a qualquer momento sem perder seus dados financeiros.")
