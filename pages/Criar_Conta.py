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
    .signup-shell h1{font-size:clamp(2rem,5vw,4.1rem);line-height:1.02;margin:.4rem 0 1rem;color:#113248}
    .signup-shell h1 strong{color:#0D71A8}
    .signup-shell p{max-width:760px;margin:0 auto;font-size:1.02rem;line-height:1.65;color:#627D8F}

    .signup-plan-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin:26px 0 22px}
    .signup-plan{
      position:relative;overflow:hidden;min-height:292px;padding:24px;border-radius:24px;text-align:left;
      color:#F8FCFF;border:1px solid rgba(124,223,255,.28);
      background:linear-gradient(145deg,#082B49 0%,#0A4674 48%,#0B6B9E 100%);
      box-shadow:0 18px 42px rgba(7,48,78,.22),inset 0 1px 0 rgba(255,255,255,.08);
      transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease;
    }
    .signup-plan::before{
      content:"";position:absolute;width:220px;height:220px;border-radius:50%;right:-90px;top:-115px;
      background:radial-gradient(circle,rgba(79,204,255,.26),rgba(79,204,255,0) 68%);pointer-events:none;
    }
    .signup-plan:hover{transform:translateY(-3px);box-shadow:0 22px 48px rgba(4,52,84,.30),0 0 26px rgba(0,174,239,.12)}
    .signup-plan.featured{
      border:1px solid rgba(255,215,90,.72);
      background:linear-gradient(145deg,#061F39 0%,#0A3968 44%,#0B5E99 100%);
      box-shadow:0 20px 48px rgba(3,39,68,.34),0 0 26px rgba(255,215,90,.12),inset 0 1px 0 rgba(255,255,255,.08);
    }
    .signup-plan.featured::after{
      content:"";position:absolute;left:0;top:0;right:0;height:4px;
      background:linear-gradient(90deg,#D89A00,#FFD75A,#FFF1A5,#FFD75A,#D89A00);
    }
    .signup-plan .tag{
      display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:999px;
      font-size:.66rem;font-weight:950;letter-spacing:.12em;color:#DDF7FF;
      background:rgba(5,24,40,.34);border:1px solid rgba(159,230,255,.22);
    }
    .signup-plan.featured .tag{color:#122F42;background:linear-gradient(90deg,#FFD75A,#FFE992);border-color:rgba(255,255,255,.30)}
    .signup-plan h3{margin:.85rem 0 .55rem;font-size:1.48rem;line-height:1.15;color:#FFFFFF;font-weight:950}
    .signup-plan p{font-size:.90rem;line-height:1.55;margin:0;color:#E1F3FC}
    .signup-plan strong{color:#FFE477}
    .plan-benefits{list-style:none;padding:0;margin:16px 0 0;display:grid;gap:8px}
    .plan-benefits li{font-size:.80rem;line-height:1.35;color:#F1FAFF;display:flex;align-items:flex-start;gap:8px}
    .plan-benefits li::before{content:"✓";color:#7BE3FF;font-weight:950;flex:0 0 auto}
    .signup-plan.featured .plan-benefits li::before{color:#FFE477}
    .old-price{text-decoration:line-through;opacity:.74;font-size:.83rem;color:#D9EBF5;margin-top:14px}
    .launch-price{font-size:1.75rem;font-weight:950;color:#FFE477;margin:.18rem 0;text-shadow:0 0 18px rgba(255,215,90,.15)}
    .price-lock{font-size:.72rem!important;color:#D9F4FF!important;margin-top:.5rem!important}

    /* Formulário: contraste e acabamento premium */
    [data-testid="stForm"]{
      border:1px solid rgba(0,127,184,.16)!important;border-radius:22px!important;
      background:rgba(255,255,255,.86)!important;box-shadow:0 18px 42px rgba(19,63,88,.14)!important;
      backdrop-filter:blur(12px)!important;
    }
    [data-testid="stTextInput"] input{
      border-radius:10px!important;
    }
    [data-testid="stTextInput"]:focus-within > div > div{
      border-color:#0B84C4!important;box-shadow:0 0 0 3px rgba(11,132,196,.11)!important;
    }

    /* Botão do olhinho: azul tecnológico + ícone branco */
    .stApp [data-testid="stTextInput"] button{
      min-width:42px!important;min-height:100%!important;padding:0 11px!important;
      border-left:1px solid rgba(255,255,255,.10)!important;border-radius:0 9px 9px 0!important;
      background:linear-gradient(135deg,#082B49 0%,#0B4F82 56%,#087CB5 100%)!important;
      color:#FFFFFF!important;-webkit-text-fill-color:#FFFFFF!important;
      box-shadow:inset 0 1px 0 rgba(255,255,255,.10)!important;
      transition:filter .18s ease,box-shadow .18s ease!important;
    }
    .stApp [data-testid="stTextInput"] button:hover{
      filter:brightness(1.12)!important;box-shadow:0 0 18px rgba(0,174,239,.22),inset 0 1px 0 rgba(255,255,255,.13)!important;
    }
    .stApp [data-testid="stTextInput"] button svg,
    .stApp [data-testid="stTextInput"] button svg path{
      color:#FFFFFF!important;fill:none!important;stroke:#FFFFFF!important;opacity:1!important;
    }

    [data-testid="stCheckbox"] label{font-weight:700!important;color:#385D72!important}
    [data-testid="stFormSubmitButton"] button{
      min-height:46px!important;border:0!important;border-radius:12px!important;
      background:linear-gradient(90deg,#D89A00,#FFD75A 48%,#F0B90B)!important;
      color:#102B3E!important;font-weight:950!important;box-shadow:0 10px 24px rgba(201,148,0,.22)!important;
    }
    [data-testid="stFormSubmitButton"] button:hover{filter:brightness(1.03)!important;box-shadow:0 13px 30px rgba(201,148,0,.28)!important}
    [data-testid="stPageLink"] a{font-weight:850!important;color:#0A6D9F!important}

    @media(max-width:700px){
      .signup-plan-grid{grid-template-columns:1fr;gap:14px}
      .signup-shell{text-align:left}
      .signup-shell h1{font-size:clamp(2rem,11vw,3.1rem)}
      .signup-plan{min-height:0;padding:20px}
      [data-testid="stForm"]{border-radius:18px!important}
    }
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
        <p>Gestão financeira essencial para começar sem cartão e sem complicação.</p>
        <ul class="plan-benefits">
          <li>Receitas, despesas e vencimentos</li>
          <li>Central de urgências e análises essenciais</li>
          <li>IA Padrão para lançar, consultar e organizar</li>
          <li>Contas, cartões, metas e orçamentos</li>
        </ul>
      </article>
      <article class="signup-plan featured">
        <div class="tag">OFERTA DE LANÇAMENTO</div>
        <h3>🧠 RENOVA IA Personal</h3>
        <p><strong>Sua IA financeira que aprende seu jeito de cuidar do dinheiro.</strong></p>
        <ul class="plan-benefits">
          <li>Tudo do plano gratuito</li>
          <li>Memória privada de preferências e regras</li>
          <li>Treinamento com seu vocabulário e contexto</li>
          <li>PDFs e YouTube como conhecimento personalizado</li>
        </ul>
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
        full_name = st.text_input("Nome completo", placeholder="Ex.: Cledemilson Oliveira")
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
