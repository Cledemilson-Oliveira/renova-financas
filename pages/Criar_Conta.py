from __future__ import annotations

import re

import streamlit as st

from src.supabase_client import is_authenticated, sign_up
from src.theme import apply_renova_theme


st.set_page_config(
    page_title="Criar conta • RENOVA Finanças",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_renova_theme()

st.markdown(
    """
    <style>
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"]{display:none!important}
    [data-testid="stMainBlockContainer"]{max-width:1180px!important;margin:0 auto!important}
    .signup-shell{max-width:980px;margin:12px auto 22px;text-align:center}
    .signup-shell h1{font-size:clamp(2rem,5vw,4.1rem);line-height:1.02;margin:.4rem 0 1rem}
    .signup-shell p{max-width:760px;margin:0 auto;font-size:1.02rem;line-height:1.65}
    .signup-plan-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:24px 0 18px}
    .signup-plan{padding:20px;border:1px solid rgba(0,174,239,.20);border-radius:22px;background:rgba(7,24,38,.72);text-align:left}
    .signup-plan.featured{border-color:rgba(255,215,90,.42);box-shadow:0 14px 34px rgba(255,215,90,.08)}
    .signup-plan .tag{font-size:.68rem;font-weight:900;letter-spacing:.13em;color:#7BDFFF}
    .signup-plan.featured .tag{color:#FFE477}
    .signup-plan h3{margin:.45rem 0 .55rem}
    .signup-plan p{font-size:.86rem;margin:0;color:#9DB6C4}
    .signup-plan strong{color:#FFE477}
    .old-price{text-decoration:line-through;opacity:.65;font-size:.84rem}
    .launch-price{font-size:1.45rem;font-weight:950;color:#FFE477;margin:.25rem 0}
    .price-lock{font-size:.72rem!important;color:#BDEBFF!important;margin-top:.55rem!important}
    @media(max-width:700px){.signup-plan-grid{grid-template-columns:1fr}.signup-shell{text-align:left}}
    </style>
    """,
    unsafe_allow_html=True,
)

plan_param = str(st.query_params.get("plan", "free") or "free").lower()
wants_premium = plan_param == "premium"

if is_authenticated():
    if wants_premium:
        st.session_state.nav_page = "Assinar RENOVA IA"
    st.switch_page("app.py")

st.markdown(
    """
    <section class="signup-shell">
      <div class="sales-eyebrow">RENOVA FINANÇAS • COMECE AGORA</div>
      <h1>Crie sua conta grátis.<br><strong>Organize hoje. Decida melhor amanhã.</strong></h1>
      <p>
        Sua conta gratuita já inclui a IA Padrão para registrar receitas, despesas,
        acompanhar vencimentos, consultar números e analisar sua situação financeira.
      </p>
    </section>
    <section class="signup-plan-grid">
      <article class="signup-plan">
        <div class="tag">GRÁTIS • R$ 0</div>
        <h3>🤖 IA Padrão RENOVA</h3>
        <p>Gestão financeira, lançamentos, vencimentos, consultas e análises essenciais.</p>
      </article>
      <article class="signup-plan featured">
        <div class="tag">PREÇO DE LANÇAMENTO</div>
        <h3>🧠 RENOVA IA Personal</h3>
        <p><strong>Sua IA financeira que aprende seu jeito de cuidar do dinheiro.</strong></p>
        <div class="old-price">Valor de referência: R$ 29,90/mês</div>
        <div class="launch-price">R$ 9,90/mês</div>
        <p class="price-lock">Quem assinar nessa condição mantém R$ 9,90/mês enquanto a assinatura permanecer ativa.</p>
      </article>
    </section>
    """,
    unsafe_allow_html=True,
)

if wants_premium:
    st.info(
        "🧠 Você escolheu o **RENOVA IA Personal**. Primeiro crie sua conta. "
        "Depois do acesso, você seguirá para a assinatura de lançamento por **R$ 9,90/mês**."
    )
else:
    st.success("✅ O plano gratuito não exige cartão e já libera a IA Padrão RENOVA.")

st.markdown("## Criar minha conta")
st.caption("Sem CPF. Pedimos apenas os dados necessários para acesso e contato.")

with st.form("public_signup_form", clear_on_submit=False):
    c1, c2 = st.columns(2)
    with c1:
        full_name = st.text_input("Nome completo", placeholder="Seu nome")
        email = st.text_input("E-mail", placeholder="voce@email.com")
        phone = st.text_input("Celular / WhatsApp", placeholder="(14) 99999-9999")
    with c2:
        password = st.text_input("Senha", type="password", placeholder="Mínimo de 8 caracteres")
        confirm = st.text_input("Confirmar senha", type="password", placeholder="Repita a senha")

    accepted = st.checkbox("Li e concordo em criar minha conta RENOVA Finanças.")
    submitted = st.form_submit_button("Criar conta grátis", type="primary", use_container_width=True)

if submitted:
    clean_name = " ".join(full_name.split()).strip()
    clean_email = email.strip().lower()
    phone_digits = re.sub(r"\D", "", phone)

    if len(clean_name) < 2:
        st.error("Informe seu nome.")
    elif not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", clean_email):
        st.error("Informe um e-mail válido.")
    elif len(phone_digits) not in {10, 11, 12, 13}:
        st.error("Informe um celular/WhatsApp válido com DDD.")
    elif len(password) < 8:
        st.error("Use uma senha com pelo menos 8 caracteres.")
    elif password != confirm:
        st.error("As senhas não conferem.")
    elif not accepted:
        st.error("Confirme a criação da conta para continuar.")
    else:
        normalized_phone = f"+{phone_digits}" if len(phone_digits) in {12, 13} else f"+55{phone_digits}"
        try:
            with st.spinner("Criando sua conta RENOVA Finanças..."):
                response = sign_up(clean_email, password, clean_name, normalized_phone)

            if response.session is not None:
                st.success("✅ Conta criada com sucesso.")
                st.session_state.nav_page = "Assinar RENOVA IA" if wants_premium else "Dashboard"
                st.switch_page("app.py")
            else:
                st.session_state.signup_email_pending = clean_email
                st.success(
                    "✅ Conta criada. Verifique seu e-mail para confirmar o cadastro e depois entre no RENOVA Finanças."
                )
                st.info("Se a mensagem não aparecer, confira também Spam, Promoções e Lixo eletrônico.")
        except Exception as exc:
            raw = str(exc)
            normalized = raw.lower()
            st.session_state.signup_last_error = raw

            if "already registered" in normalized or "user_already_exists" in normalized:
                st.error("Este e-mail já possui uma conta. Use a opção **Já tenho uma conta**.")
            elif "rate limit" in normalized or "over_email_send_rate_limit" in normalized:
                st.error("Houve muitas tentativas em pouco tempo. Aguarde alguns minutos e tente novamente.")
            elif "password" in normalized and ("weak" in normalized or "invalid" in normalized):
                st.error("A senha não atende aos requisitos de segurança. Use pelo menos 8 caracteres.")
            elif "email" in normalized and "invalid" in normalized:
                st.error("O endereço de e-mail não é válido.")
            elif "redirect" in normalized:
                st.error("O cadastro está pronto, mas a nova URL pública ainda precisa ser autorizada no provedor de autenticação.")
            elif "signup" in normalized and "disabled" in normalized:
                st.error("O cadastro está temporariamente indisponível. A configuração de novos usuários precisa ser revisada.")
            else:
                st.error("Não foi possível criar a conta agora. Tente novamente em instantes.")

st.divider()
left, right = st.columns(2)
with left:
    st.page_link("app.py", label="← Já tenho uma conta", use_container_width=True)
with right:
    st.caption("Conta gratuita • IA Padrão incluída • RENOVA IA Personal opcional")
