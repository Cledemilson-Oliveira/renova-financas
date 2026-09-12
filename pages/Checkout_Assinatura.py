from __future__ import annotations

import base64
import json
import re

import streamlit as st
import streamlit.components.v1 as components

from src.mercado_pago_checkout import (
    create_boleto_payment,
    create_pix_payment,
    get_transparent_checkout_config,
    transparent_auth_token,
    transparent_function_url,
)
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
    page_title="Checkout Transparente • RENOVA IA",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_renova_theme()

st.markdown(
    """
    <style>
    [data-testid="stMainBlockContainer"]{max-width:1080px!important;margin:0 auto!important;padding-top:1.3rem!important}
    .renova-pay-hero{padding:20px 22px;border-radius:22px;border:1px solid rgba(25,217,255,.18);background:linear-gradient(135deg,rgba(7,31,50,.96),rgba(10,24,43,.96));box-shadow:0 18px 46px rgba(0,0,0,.18);margin-bottom:16px}
    .renova-pay-hero h1{margin:0;color:#F7FBFF;font-size:clamp(1.45rem,3vw,2.25rem)}
    .renova-pay-hero strong{color:#19D9FF}.renova-pay-hero p{color:#A9C3D7;margin:.55rem 0 0}
    .renova-pay-note{padding:12px 14px;border-radius:14px;background:rgba(25,217,255,.06);border:1px solid rgba(25,217,255,.14);color:#BFD5E5;margin:.4rem 0 1rem}
    .renova-method-card{padding:15px 16px;border-radius:18px;background:rgba(8,29,47,.76);border:1px solid rgba(255,255,255,.08);margin-bottom:10px}
    @media(max-width:768px){
      [data-testid="stMainBlockContainer"]{padding-left:12px!important;padding-right:12px!important;padding-top:.7rem!important}
      .renova-pay-hero{padding:16px 15px;border-radius:18px}
      [data-testid="stHorizontalBlock"]{gap:.45rem!important}
      button{min-height:48px!important}
      input,textarea{font-size:16px!important}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    <section class="renova-pay-hero">
      <h1>Checkout <strong>Transparente</strong> RENOVA IA</h1>
      <p>RENOVA IA Personal • R$ {price_label}/mês • pagamento processado pelo Mercado Pago sem redirecionar você para outro checkout.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="renova-pay-note">🔐 Dados sensíveis de cartão são tokenizados diretamente pelo Mercado Pago. O RENOVA não armazena número completo do cartão nem código de segurança.</div>',
    unsafe_allow_html=True,
)


def _normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if len(digits) in {10, 11}:
        return f"+55{digits}"
    if len(digits) in {12, 13}:
        return f"+{digits}"
    return ""


if not is_authenticated():
    st.markdown("## Identificação para a assinatura")
    st.caption("Se você já possui conta, use o mesmo e-mail e senha. Caso ainda não tenha, o acesso é criado antes do pagamento.")

    with st.form("subscription_identity_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("Nome completo", placeholder="Seu nome")
            email = st.text_input("E-mail", placeholder="voce@email.com")
            phone = st.text_input("Celular / WhatsApp", placeholder="(14) 99999-9999")
        with c2:
            password = st.text_input("Senha de acesso", type="password", placeholder="Mínimo de 8 caracteres")
            confirm = st.text_input("Confirmar senha", type="password", placeholder="Repita a senha")
        accepted = st.checkbox("Concordo com a criação/uso do meu acesso para concluir a contratação.")
        submitted = st.form_submit_button("CONTINUAR PARA AS FORMAS DE PAGAMENTO", type="primary", use_container_width=True)

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
            st.error("Confirme os dados para continuar.")
        else:
            response = None
            try:
                response = sign_in(clean_email, password)
            except Exception:
                try:
                    response = sign_up(clean_email, password, clean_name, normalized_phone)
                except Exception as exc:
                    text = str(exc).lower()
                    if "already registered" in text or "user_already_exists" in text:
                        st.error("Este e-mail já possui acesso. Confira a senha informada.")
                    else:
                        st.error("Não foi possível validar seus dados agora. Tente novamente em instantes.")

            if response is not None:
                if getattr(response, "session", None) is None:
                    st.warning("Confirme seu e-mail para validar o acesso. Depois volte a esta página para concluir o pagamento.")
                else:
                    user = current_user()
                    if user:
                        try:
                            bootstrap_user(user)
                        except Exception:
                            pass
                    st.rerun()
    st.stop()


user = current_user()
uid = str(user.id) if user and getattr(user, "id", None) else ""
email = str(getattr(user, "email", "") or "") if user else ""
metadata = (getattr(user, "user_metadata", {}) or {}) if user else {}
default_name = str(metadata.get("full_name") or "").strip() or (email.split("@")[0] if email else "Cliente RENOVA")

try:
    if uid and has_active_ai_subscription(uid):
        st.success("✅ Sua RENOVA IA Personal já está ativa.")
        st.page_link("app.py", label="Ir para o Minhas Finanças", use_container_width=True)
        st.stop()
except Exception:
    pass

try:
    checkout_config = get_transparent_checkout_config("renova_ia")
except Exception as exc:
    st.error(f"Não foi possível carregar o Checkout Transparente agora: {exc}")
    st.stop()

price = float(checkout_config.get("price") or price)
price_label = f"{price:.2f}".replace(".", ",")

st.markdown("## Como você prefere pagar?")
method = st.radio(
    "Forma de pagamento",
    ["💳 Cartão", "⚡ Pix", "🧾 Boleto"],
    horizontal=True,
    label_visibility="collapsed",
)

if method == "💳 Cartão":
    st.markdown('<div class="renova-method-card"><strong>Cartão de crédito</strong><br><span>Cobrança mensal automática. Seus dados são digitados em campos seguros do Mercado Pago.</span></div>', unsafe_allow_html=True)
    public_key = str(checkout_config.get("public_key") or "").strip()
    if not public_key:
        st.warning("A estrutura do cartão transparente está pronta, mas falta configurar a **MP_PUBLIC_KEY** de produção no backend do Mercado Pago.")
    else:
        try:
            auth_token = transparent_auth_token()
            function_url = transparent_function_url()
        except Exception as exc:
            st.error(str(exc))
            st.stop()

        card_html = f"""
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<script src="https://sdk.mercadopago.com/js/v2"></script>
<script src="https://www.mercadopago.com/v2/security.js" view="checkout"></script>
<style>
:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:transparent;color:#F7FBFF;font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif}}
#form-checkout{{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:14px;border:1px solid rgba(25,217,255,.18);border-radius:18px;background:#0B1E31}}
.field{{display:flex;flex-direction:column;gap:6px}}.full{{grid-column:1/-1}}label{{font-size:12px;color:#A8C1D4;font-weight:700}}
input,select,.mp-field{{width:100%;min-height:48px;border:1px solid rgba(255,255,255,.14);border-radius:12px;background:#10283C;color:#F7FBFF;padding:11px 12px;outline:none}}
.mp-field{{padding:0 12px;display:flex;align-items:center}}input:focus,select:focus,.mp-field:focus-within{{border-color:#19D9FF;box-shadow:0 0 0 2px rgba(25,217,255,.12)}}
button{{grid-column:1/-1;min-height:52px;border:0;border-radius:14px;background:linear-gradient(112deg,#087FF5,#19D9FF 50%,#7457FF);color:white;font-weight:900;font-size:15px;cursor:pointer}}
button:disabled{{opacity:.55;cursor:wait}}#status{{grid-column:1/-1;padding:10px 12px;border-radius:12px;display:none;font-size:13px;line-height:1.45}}#status.ok{{display:block;background:rgba(24,223,165,.10);border:1px solid rgba(24,223,165,.24)}}#status.err{{display:block;background:rgba(255,91,91,.10);border:1px solid rgba(255,91,91,.24)}}
.hidden{{display:none}}@media(max-width:620px){{#form-checkout{{grid-template-columns:1fr;padding:12px}}.full{{grid-column:1}}}}
</style>
</head>
<body>
<form id="form-checkout">
  <div class="field full"><label>Número do cartão</label><div id="form-checkout__cardNumber" class="mp-field"></div></div>
  <div class="field"><label>Validade</label><div id="form-checkout__expirationDate" class="mp-field"></div></div>
  <div class="field"><label>CVV</label><div id="form-checkout__securityCode" class="mp-field"></div></div>
  <div class="field full"><label>Nome impresso no cartão</label><input id="form-checkout__cardholderName" autocomplete="cc-name" /></div>
  <div class="field"><label>Documento</label><select id="form-checkout__identificationType"></select></div>
  <div class="field"><label>CPF</label><input id="form-checkout__identificationNumber" inputmode="numeric" /></div>
  <div class="field full"><label>E-mail</label><input id="form-checkout__cardholderEmail" type="email" value={json.dumps(email)} /></div>
  <select id="form-checkout__issuer" class="hidden"></select>
  <select id="form-checkout__installments" class="hidden"></select>
  <button type="submit" id="form-checkout__submit">ASSINAR POR R$ {price_label}/MÊS</button>
  <div id="status"></div>
</form>
<script>
const publicKey = {json.dumps(public_key)};
const endpoint = {json.dumps(function_url)};
const authToken = {json.dumps(auth_token)};
const amount = {json.dumps(f"{price:.2f}")};
const statusBox = document.getElementById('status');
const submitButton = document.getElementById('form-checkout__submit');
const showStatus = (text, ok=false) => {{ statusBox.textContent=text; statusBox.className=ok?'ok':'err'; }};
try {{
  const mp = new MercadoPago(publicKey, {{ locale: 'pt-BR' }});
  const cardForm = mp.cardForm({{
    amount,
    iframe: true,
    form: {{
      id: 'form-checkout',
      cardNumber: {{ id: 'form-checkout__cardNumber', placeholder: 'Número do cartão' }},
      expirationDate: {{ id: 'form-checkout__expirationDate', placeholder: 'MM/AA' }},
      securityCode: {{ id: 'form-checkout__securityCode', placeholder: 'CVV' }},
      cardholderName: {{ id: 'form-checkout__cardholderName', placeholder: 'Titular do cartão' }},
      issuer: {{ id: 'form-checkout__issuer', placeholder: 'Banco emissor' }},
      installments: {{ id: 'form-checkout__installments', placeholder: 'Parcelas' }},
      identificationType: {{ id: 'form-checkout__identificationType', placeholder: 'Documento' }},
      identificationNumber: {{ id: 'form-checkout__identificationNumber', placeholder: 'CPF' }},
      cardholderEmail: {{ id: 'form-checkout__cardholderEmail', placeholder: 'E-mail' }},
    }},
    callbacks: {{
      onFormMounted: (error) => {{ if (error) showStatus('Não foi possível carregar os campos seguros do cartão.'); }},
      onSubmit: async (event) => {{
        event.preventDefault();
        submitButton.disabled = true;
        statusBox.className=''; statusBox.textContent='';
        try {{
          const data = cardForm.getCardFormData();
          if (!data.token) throw new Error('Não foi possível tokenizar o cartão. Confira os dados.');
          const response = await fetch(endpoint, {{
            method: 'POST',
            headers: {{ 'Authorization': `Bearer ${{authToken}}`, 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
              action: 'card',
              plan_code: 'renova_ia',
              card_token: data.token,
              payment_method_id: data.paymentMethodId || null,
            }}),
          }});
          const payload = await response.json().catch(() => ({{}}));
          if (!response.ok) throw new Error(payload.message || 'Não foi possível criar a assinatura.');
          showStatus(payload.message || 'Assinatura enviada. Aguardando confirmação automática do Mercado Pago.', true);
        }} catch (err) {{
          showStatus(err?.message || 'Falha ao processar a assinatura.');
        }} finally {{ submitButton.disabled = false; }}
      }},
    }},
  }});
}} catch (err) {{ showStatus(err?.message || 'Falha ao iniciar Mercado Pago.'); }}
</script>
</body>
</html>
"""
        components.html(card_html, height=650, scrolling=False)
        if st.button("↻ Atualizar status da assinatura", use_container_width=True, key="refresh_card_subscription"):
            st.rerun()
        st.caption("Após a confirmação do Mercado Pago, o acesso é liberado automaticamente pelo webhook.")

elif method == "⚡ Pix":
    st.markdown('<div class="renova-method-card"><strong>Pix</strong><br><span>O QR Code e o Pix Copia e Cola aparecem aqui mesmo. Após a confirmação, o acesso é liberado automaticamente.</span></div>', unsafe_allow_html=True)
    with st.form("pix_form", clear_on_submit=False):
        pix_name = st.text_input("Nome completo", value=default_name, key="pix_name")
        pix_cpf = st.text_input("CPF", placeholder="000.000.000-00", key="pix_cpf")
        pix_submit = st.form_submit_button(f"GERAR PIX • R$ {price_label}", type="primary", use_container_width=True)
    if pix_submit:
        try:
            with st.spinner("Gerando Pix no Mercado Pago..."):
                st.session_state.mp_pix_result = create_pix_payment(payer_name=pix_name, cpf=pix_cpf)
        except Exception as exc:
            st.error(f"Não foi possível gerar o Pix: {exc}")

    pix_result = st.session_state.get("mp_pix_result") or {}
    if pix_result:
        qr_b64 = str(pix_result.get("qr_code_base64") or "").strip()
        qr_code = str(pix_result.get("qr_code") or "").strip()
        st.success("Pix gerado. Pague pelo aplicativo do seu banco e aguarde a confirmação automática.")
        if qr_b64:
            try:
                st.image(base64.b64decode(qr_b64), width=260, caption="QR Code Pix")
            except Exception:
                pass
        if qr_code:
            st.text_area("Pix Copia e Cola", value=qr_code, height=120, disabled=True)
        st.caption("Pix e boleto liberam 30 dias após a confirmação. A renovação desses meios é manual; cartão possui cobrança mensal automática.")
        if st.button("↻ Verificar se o Pix já foi confirmado", use_container_width=True, key="refresh_pix"):
            st.rerun()

else:
    st.markdown('<div class="renova-method-card"><strong>Boleto bancário</strong><br><span>Informe os dados exigidos pelo Mercado Pago. O acesso é liberado somente depois da compensação.</span></div>', unsafe_allow_html=True)
    with st.form("boleto_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            boleto_name = st.text_input("Nome completo", value=default_name, key="boleto_name")
            boleto_cpf = st.text_input("CPF", placeholder="000.000.000-00", key="boleto_cpf")
            boleto_zip = st.text_input("CEP", placeholder="00000-000", key="boleto_zip")
            boleto_street = st.text_input("Rua / Avenida", key="boleto_street")
        with c2:
            boleto_number = st.text_input("Número", key="boleto_number")
            boleto_neighborhood = st.text_input("Bairro", key="boleto_neighborhood")
            boleto_city = st.text_input("Cidade", key="boleto_city")
            boleto_state = st.text_input("UF", placeholder="SP", max_chars=2, key="boleto_state")
        boleto_submit = st.form_submit_button(f"GERAR BOLETO • R$ {price_label}", type="primary", use_container_width=True)

    if boleto_submit:
        try:
            with st.spinner("Gerando boleto no Mercado Pago..."):
                st.session_state.mp_boleto_result = create_boleto_payment(
                    payer_name=boleto_name,
                    cpf=boleto_cpf,
                    zip_code=boleto_zip,
                    street_name=boleto_street,
                    street_number=boleto_number,
                    neighborhood=boleto_neighborhood,
                    city=boleto_city,
                    state=boleto_state,
                )
        except Exception as exc:
            st.error(f"Não foi possível gerar o boleto: {exc}")

    boleto_result = st.session_state.get("mp_boleto_result") or {}
    if boleto_result:
        barcode = str(boleto_result.get("barcode") or "").strip()
        ticket_url = str(boleto_result.get("ticket_url") or "").strip()
        st.success("Boleto gerado. O acesso será liberado automaticamente após a compensação.")
        if barcode:
            st.text_area("Código de barras", value=barcode, height=90, disabled=True)
        if ticket_url:
            st.link_button("Abrir boleto gerado", ticket_url, use_container_width=True)
        st.caption("A compensação do boleto pode levar até algumas horas úteis. A renovação mensal por boleto é manual.")
        if st.button("↻ Verificar compensação", use_container_width=True, key="refresh_boleto"):
            st.rerun()

st.markdown("---")
st.caption("Mercado Pago processa o pagamento. O RENOVA recebe somente o resultado/token necessário e libera o plano por webhook.")
