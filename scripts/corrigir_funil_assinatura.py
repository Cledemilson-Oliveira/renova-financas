from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8")


# -----------------------------------------------------------------------------
# 1) CTAs públicos: gratuito permanece na tela inicial; Premium vai para vendas.
# -----------------------------------------------------------------------------
public_runtime = read("src/public_entry_runtime.py")
public_runtime = public_runtime.replace(
    '_FREE_CTA_TARGET = "/Criar_Conta"',
    '_FREE_CTA_TARGET = "#criar-conta"',
)
public_runtime = public_runtime.replace(
    '_PREMIUM_CTA_TARGET = "/Criar_Conta?plan=premium"',
    '_PREMIUM_CTA_TARGET = "/Assinar_RENOVA_IA"',
)
public_runtime = public_runtime.replace(
    '    Os CTAs usam ``target=_self`` de forma explícita para impedir que o cadastro\n    seja aberto em uma nova aba pelo navegador/host do Streamlit.\n',
    '    O CTA gratuito permanece na própria tela inicial/login. Todo CTA de assinatura\n    aponta para a página comercial RENOVA IA Personal, sem passar pelo cadastro grátis.\n',
)
legacy_anchor = "        if isinstance(body, str):\n"
legacy_rule = (
    "        if isinstance(body, str):\n"
    "            # Compatibilidade: qualquer link antigo de Premium deixa de passar pelo cadastro gratuito.\n"
    "            body = body.replace('/Criar_Conta?plan=premium', _PREMIUM_CTA_TARGET)\n"
)
if "qualquer link antigo de Premium" not in public_runtime:
    if legacy_anchor not in public_runtime:
        raise SystemExit("Âncora public_entry_runtime não encontrada")
    public_runtime = public_runtime.replace(legacy_anchor, legacy_rule, 1)
write("src/public_entry_runtime.py", public_runtime)


# -----------------------------------------------------------------------------
# 2) Rota antiga Criar_Conta: não mantém mais uma segunda página de cadastro.
#    Free volta para a tela inicial/login; Premium segue para a página de vendas.
# -----------------------------------------------------------------------------
write(
    "pages/Criar_Conta.py",
    '''from __future__ import annotations\n\nimport streamlit as st\n\n\nst.set_page_config(\n    page_title="RENOVA Finanças",\n    page_icon="💰",\n    layout="wide",\n    initial_sidebar_state="collapsed",\n)\n\n# Rota legada preservada apenas para não quebrar links antigos.\n# Cadastro gratuito existe exclusivamente na tela inicial/login do aplicativo.\nplan_param = str(st.query_params.get("plan", "free") or "free").lower()\nif plan_param == "premium":\n    st.switch_page("pages/Assinar_RENOVA_IA.py")\n\nst.switch_page("app.py")\n''',
)


# -----------------------------------------------------------------------------
# 3) Página comercial: pode ser vista sem login e possui apenas CTA de checkout.
# -----------------------------------------------------------------------------
sales = read("pages/Assinar_RENOVA_IA.py")
sales = sales.replace("from html import escape\n", "")
sales = sales.replace("from src.mercado_pago_checkout import create_subscription_checkout\n", "")

old_sidebar_auth = '''with st.sidebar:\n    brand_block()\n    st.page_link("app.py", label="Voltar ao RENOVA Finanças", icon="🏠", use_container_width=True)\n\nif not is_configured():\n    st.error("O Supabase ainda não está configurado neste ambiente.")\n    st.stop()\n\nif not is_authenticated():\n    st.session_state["nav_page"] = "Assinar RENOVA IA"\n    st.switch_page("app.py")\n\nuser = current_user()\nuid = str(user.id) if user and getattr(user, "id", None) else ""\n\ntry:\n    if uid and has_active_ai_subscription(uid):\n        st.success("✅ Sua RENOVA IA Personalizada já está ativa.")\n        st.page_link("pages/Treinamento_IA.py", label="🧠 Ir para o treinamento da minha IA", use_container_width=True)\n        st.page_link("app.py", label="🏠 Voltar ao painel", use_container_width=True)\n        st.stop()\nexcept Exception:\n    pass\n\nplan = get_ai_plan() or {}\n'''

new_sidebar_auth = '''if is_authenticated():\n    with st.sidebar:\n        brand_block()\n        st.page_link("app.py", label="Voltar ao RENOVA Finanças", icon="🏠", use_container_width=True)\nelse:\n    st.markdown(\n        """\n        <style>\n        [data-testid="stSidebar"],\n        [data-testid="stSidebarCollapsedControl"],\n        [data-testid="stSidebarCollapseButton"]{display:none!important}\n        </style>\n        """,\n        unsafe_allow_html=True,\n    )\n\nif not is_configured():\n    st.error("O Supabase ainda não está configurado neste ambiente.")\n    st.stop()\n\nuser = current_user() if is_authenticated() else None\nuid = str(user.id) if user and getattr(user, "id", None) else ""\n\ntry:\n    if uid and has_active_ai_subscription(uid):\n        st.success("✅ Sua RENOVA IA Personalizada já está ativa.")\n        st.page_link("pages/Treinamento_IA.py", label="🧠 Ir para o treinamento da minha IA", use_container_width=True)\n        st.page_link("app.py", label="🏠 Voltar ao painel", use_container_width=True)\n        st.stop()\nexcept Exception:\n    pass\n\ntry:\n    plan = get_ai_plan() or {}\nexcept Exception:\n    # A oferta pública precisa carregar mesmo quando a política RLS não expõe a tabela ao visitante anônimo.\n    plan = {}\n'''

if old_sidebar_auth in sales:
    sales = sales.replace(old_sidebar_auth, new_sidebar_auth, 1)
elif "A oferta pública precisa carregar" not in sales:
    raise SystemExit("Bloco de autenticação da página de vendas não encontrado")

button_start = sales.find('if st.button(\n    f"✨ ASSINAR RENOVA IA PERSONAL')
if button_start < 0:
    if "IR PARA O CHECKOUT SEGURO" not in sales:
        raise SystemExit("CTA antigo da página de vendas não encontrado")
else:
    sales = sales[:button_start] + '''st.caption("🔐 O próximo passo abre o checkout. Seus dados de acesso e pagamento são informados somente na etapa de contratação.")\n\nif st.button(\n    f"💳 IR PARA O CHECKOUT SEGURO • R$ {price_label}/MÊS",\n    type="primary",\n    use_container_width=True,\n):\n    st.switch_page("pages/Checkout_Assinatura.py")\n'''

write("pages/Assinar_RENOVA_IA.py", sales)


# -----------------------------------------------------------------------------
# 4) Checkout: dados da contratação ficam aqui. Nunca existe botão "criar grátis".
# -----------------------------------------------------------------------------
write(
    "pages/Checkout_Assinatura.py",
    '''from __future__ import annotations\n\nimport re\nfrom html import escape\n\nimport streamlit as st\n\nfrom src.mercado_pago_checkout import create_subscription_checkout\nfrom src.repository import bootstrap_user, get_ai_plan, has_active_ai_subscription\nfrom src.supabase_client import (\n    current_user,\n    is_authenticated,\n    is_configured,\n    sign_in,\n    sign_up,\n)\nfrom src.theme import apply_renova_theme, brand_block\n\n\nst.set_page_config(\n    page_title="Checkout RENOVA IA • Minhas Finanças",\n    page_icon="💳",\n    layout="wide",\n    initial_sidebar_state="collapsed",\n)\napply_renova_theme()\n\nif is_authenticated():\n    with st.sidebar:\n        brand_block()\n        st.page_link("pages/Assinar_RENOVA_IA.py", label="Voltar à oferta", icon="←", use_container_width=True)\nelse:\n    st.markdown(\n        """\n        <style>\n        [data-testid="stSidebar"],\n        [data-testid="stSidebarCollapsedControl"],\n        [data-testid="stSidebarCollapseButton"]{display:none!important}\n        [data-testid="stMainBlockContainer"]{max-width:980px!important;margin:0 auto!important}\n        </style>\n        """,\n        unsafe_allow_html=True,\n    )\n\nif not is_configured():\n    st.error("O sistema de pagamento ainda não está disponível neste ambiente.")\n    st.stop()\n\ntry:\n    plan = get_ai_plan() or {}\nexcept Exception:\n    plan = {}\nprice = float(plan.get("price") or 9.90)\nprice_label = f"{price:.2f}".replace(".", ",")\n\nst.markdown(\n    f"""\n    <section class="renova-hero">\n      <h1>Finalize sua <strong>RENOVA IA Personal</strong></h1>\n      <p>R$ {price_label}/mês • informe seus dados abaixo e siga para o ambiente seguro do Mercado Pago.</p>\n    </section>\n    """,\n    unsafe_allow_html=True,\n)\n\nst.info("🔐 O Minhas Finanças não armazena os dados do seu cartão. O pagamento é concluído no Mercado Pago.")\n\n\ndef _normalize_phone(value: str) -> str:\n    digits = re.sub(r"\\D", "", value or "")\n    if len(digits) in {10, 11}:\n        return f"+55{digits}"\n    if len(digits) in {12, 13}:\n        return f"+{digits}"\n    return ""\n\n\ndef _prepare_checkout() -> None:\n    try:\n        with st.spinner("Preparando seu checkout seguro..."):\n            checkout = create_subscription_checkout("renova_ia")\n        if checkout.get("already_active"):\n            st.session_state.pop("renova_subscription_checkout_url", None)\n            st.session_state.renova_subscription_already_active = True\n            return\n        checkout_url = str(checkout.get("checkout_url") or "").strip()\n        if not checkout_url:\n            raise RuntimeError("O Mercado Pago não devolveu o endereço do checkout.")\n        st.session_state.renova_subscription_checkout_url = checkout_url\n    except Exception:\n        raise\n\n\nif not is_authenticated():\n    st.markdown("## Dados da assinatura")\n    st.caption("Esses dados criam seu acesso ao Minhas Finanças como parte da contratação. Não existe uma etapa separada de conta grátis neste fluxo.")\n\n    with st.form("subscription_identity_form", clear_on_submit=False):\n        c1, c2 = st.columns(2)\n        with c1:\n            full_name = st.text_input("Nome completo", placeholder="Seu nome")\n            email = st.text_input("E-mail", placeholder="voce@email.com")\n            phone = st.text_input("Celular / WhatsApp", placeholder="(14) 99999-9999")\n        with c2:\n            password = st.text_input("Senha de acesso", type="password", placeholder="Mínimo de 8 caracteres")\n            confirm = st.text_input("Confirmar senha", type="password", placeholder="Repita a senha")\n        accepted = st.checkbox("Concordo com a criação do meu acesso e com o início da contratação mensal.")\n        submitted = st.form_submit_button(\n            f"CONTINUAR PARA O PAGAMENTO SEGURO • R$ {price_label}/MÊS",\n            type="primary",\n            use_container_width=True,\n        )\n\n    if submitted:\n        clean_name = " ".join(full_name.split()).strip()\n        clean_email = email.strip().lower()\n        normalized_phone = _normalize_phone(phone)\n\n        if len(clean_name) < 2:\n            st.error("Informe seu nome completo.")\n        elif not re.match(r"^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$", clean_email):\n            st.error("Informe um e-mail válido.")\n        elif not normalized_phone:\n            st.error("Informe um celular/WhatsApp válido com DDD.")\n        elif len(password) < 8:\n            st.error("Use uma senha com pelo menos 8 caracteres.")\n        elif password != confirm:\n            st.error("As senhas não conferem.")\n        elif not accepted:\n            st.error("Confirme os dados da contratação para continuar.")\n        else:\n            response = None\n            try:\n                # Se o cliente já possui acesso, a mesma tela funciona como identificação segura.\n                response = sign_in(clean_email, password)\n            except Exception:\n                try:\n                    response = sign_up(clean_email, password, clean_name, normalized_phone)\n                except Exception as exc:\n                    text = str(exc).lower()\n                    if "already registered" in text or "user_already_exists" in text:\n                        st.error("Este e-mail já possui acesso. Confira a senha informada para continuar a assinatura.")\n                    else:\n                        st.error("Não foi possível validar seus dados para a assinatura. Tente novamente em instantes.")\n\n            if response is not None:\n                if getattr(response, "session", None) is None:\n                    st.warning("Confirme seu e-mail para validar o acesso. Depois, volte a este checkout para concluir a assinatura.")\n                else:\n                    user = current_user()\n                    if user:\n                        try:\n                            bootstrap_user(user)\n                        except Exception:\n                            pass\n                    try:\n                        _prepare_checkout()\n                        st.rerun()\n                    except Exception as exc:\n                        st.error(f"Não foi possível abrir o checkout agora: {exc}")\n    st.stop()\n\n\nuser = current_user()\nuid = str(user.id) if user and getattr(user, "id", None) else ""\n\ntry:\n    if uid and has_active_ai_subscription(uid):\n        st.success("✅ Sua RENOVA IA Personal já está ativa. Não é necessário pagar novamente.")\n        st.page_link("app.py", label="Ir para o Minhas Finanças", icon="🏠", use_container_width=True)\n        st.stop()\nexcept Exception:\n    pass\n\ncheckout_url = str(st.session_state.get("renova_subscription_checkout_url") or "").strip()\nif checkout_url:\n    safe_url = escape(checkout_url, quote=True)\n    st.success("Tudo certo com seus dados. Seu checkout está pronto.")\n    st.markdown(\n        f'<a href="{safe_url}" target="_self" rel="noopener" '\n        'style="display:flex;align-items:center;justify-content:center;min-height:56px;'\n        'border-radius:16px;text-decoration:none;font-weight:950;font-size:1.02rem;'\n        'background:linear-gradient(112deg,#087FF5,#19D9FF 50%,#7457FF);color:#fff;'\n        'border:1px solid rgba(25,217,255,.72);box-shadow:0 14px 36px rgba(25,217,255,.18);margin-top:10px;">'\n        'ABRIR CHECKOUT SEGURO NO MERCADO PAGO →</a>',\n        unsafe_allow_html=True,\n    )\n    st.caption("Depois da confirmação do Mercado Pago, o sistema libera automaticamente os recursos da RENOVA IA Personal.")\nelse:\n    email = str(getattr(user, "email", "") or "") if user else ""\n    st.markdown("## Confirmar contratação")\n    if email:\n        st.caption(f"A assinatura será vinculada ao acesso {email}.")\n    if st.button(\n        f"ABRIR CHECKOUT • R$ {price_label}/MÊS",\n        type="primary",\n        use_container_width=True,\n    ):\n        try:\n            _prepare_checkout()\n            st.rerun()\n        except Exception as exc:\n            st.error(f"Não foi possível abrir o checkout agora: {exc}")\n\nst.caption("Você pode voltar à oferta antes de concluir o pagamento. Nenhuma cobrança é feita sem confirmação no Mercado Pago.")\n''',
)


# -----------------------------------------------------------------------------
# 5) Fallback interno do app: qualquer rota de assinatura abre a página comercial.
# -----------------------------------------------------------------------------
app = read("app.py")
start = app.find("def render_ai_subscription_sales() -> None:\n")
end = app.find("\n\n@st.dialog", start)
if start >= 0 and end > start:
    app = app[:start] + '''def render_ai_subscription_sales() -> None:\n    # Regra de funil: assinatura sempre passa pela página comercial antes do checkout.\n    st.switch_page("pages/Assinar_RENOVA_IA.py")\n''' + app[end:]
elif "Regra de funil: assinatura sempre passa" not in app:
    raise SystemExit("Função de assinatura no app.py não encontrada")
write("app.py", app)

print("Funil de assinatura corrigido: Login -> Vendas -> Checkout -> Mercado Pago.")
