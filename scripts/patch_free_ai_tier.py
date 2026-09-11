from pathlib import Path


APP = Path("app.py")
TRAINING_PAGE = Path("pages/Treinamento_IA.py")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: esperado 1 trecho, encontrado {count}")
    return text.replace(old, new, 1)


app = APP.read_text(encoding="utf-8")

app = replace_once(app, 'APP_BUILD = "2026.09.11.5"', 'APP_BUILD = "2026.09.11.6"', "build")

app = replace_once(
    app,
    """            Tenha contas, receitas, despesas, cartões, metas e orçamentos em um só lugar.\n            Comece gratuitamente e, quando quiser acelerar sua gestão, ative a RENOVA IA.""",
    """            Tenha contas, receitas, despesas, cartões, metas e orçamentos em um só lugar.\n            A IA Padrão já vem incluída gratuitamente; personalize a memória e o treinamento quando quiser.""",
    "landing lead",
)
app = replace_once(
    app,
    '<div class="ai-chip">🧠 Aprende suas preferências de uso</div>',
    '<div class="ai-chip">🤖 IA Padrão gratuita • 🧠 Treinamento personalizado no Premium</div>',
    "ai chip",
)
app = replace_once(
    app,
    '<h2>Comece grátis. <strong>Ative a IA quando quiser.</strong></h2>',
    '<h2>Comece grátis com IA. <strong>Personalize quando quiser.</strong></h2>',
    "pricing title",
)
app = replace_once(
    app,
    """                <li>✓ Dashboard financeiro</li><li>✓ Receitas e despesas</li>\n                <li>✓ Contas e cartões</li><li>✓ Orçamentos e análises</li>""",
    """                <li>✓ Dashboard financeiro</li><li>✓ Receitas e despesas</li>\n                <li>✓ Contas e cartões</li><li>✓ Orçamentos e análises</li>\n                <li>✓ IA Padrão para lançamentos e consultas</li>""",
    "free benefits",
)
app = replace_once(
    app,
    """              <p>Para administrar suas finanças conversando com a IA.</p>\n              <ul>\n                <li>✓ Tudo do plano gratuito</li><li>✓ Assistente Financeiro IA</li>\n                <li>✓ Modo Execução</li><li>✓ Memória de preferências</li>\n                <li>✓ Análises e comandos pelo chat</li>\n              </ul>""",
    """              <p>Para transformar a IA padrão em um assistente treinado para o seu jeito de trabalhar.</p>\n              <ul>\n                <li>✓ Tudo do plano gratuito</li><li>✓ Treinamento personalizado</li>\n                <li>✓ Memória de preferências e regras</li><li>✓ PDFs e YouTube como conhecimento privado</li>\n                <li>✓ Vocabulário, conta padrão e contexto próprio</li>\n              </ul>""",
    "premium benefits",
)
app = replace_once(
    app,
    '<div class="sales-cta primary full static">Crie sua conta e ative por R$ 9,90/mês</div>',
    '<div class="sales-cta primary full static">Personalize sua IA por R$ 9,90/mês</div>',
    "premium cta",
)
app = replace_once(
    app,
    '<p class="pricing-note">A assinatura da IA é opcional. O usuário pode continuar utilizando os recursos gratuitos sem ativá-la.</p>',
    '<p class="pricing-note">A IA Padrão faz parte da conta gratuita. A assinatura é opcional e libera treinamento e memória personalizados.</p>',
    "pricing note",
)

app = replace_once(
    app,
    '            st.session_state.nav_page = "RENOVA IA" if has_renova_ai_access() else "Assinar RENOVA IA"',
    '            st.session_state.nav_page = "RENOVA IA"',
    "urgency ai route",
)

old_access = '''def has_renova_ai_access() -> bool:\n    uid = session_user_id()\n    if not uid:\n        return False\n    try:\n        if is_owner(uid):\n            return True\n        return has_active_ai_subscription(uid)\n    except Exception:\n        return False\n'''
new_access = '''def has_renova_ai_access() -> bool:\n    # Todo usuário autenticado recebe a IA Padrão gratuita.\n    return bool(session_user_id())\n\n\ndef has_personalized_ai_training_access() -> bool:\n    uid = session_user_id()\n    if not uid:\n        return False\n    try:\n        return bool(is_owner(uid) or has_active_ai_subscription(uid))\n    except Exception:\n        return False\n'''
app = replace_once(app, old_access, new_access, "ai access functions")

app = replace_once(
    app,
    '''                "goals": st.session_state.goals,\n            }''',
    '''                "goals": st.session_state.goals,\n                "_allow_personalized_training": has_personalized_ai_training_access(),\n            }''',
    "ai tier bundle",
)

old_sales = '''    hero(\n        "Ative o <strong>RENOVA IA</strong>",\n        "Transforme o RENOVA Finanças em um assistente que entende seus pedidos e executa sua gestão pelo chat.",\n    )\n\n    st.markdown(\n        f"""\n        <section class="ai-subscribe-gate">\n          <div class="sales-eyebrow">PLANO RENOVA IA</div>\n          <h2>Seu assistente financeiro por <strong>R$ {price:,.2f}/mês</strong></h2>\n          <p>\n            O plano gratuito continua disponível para sua gestão manual.\n            A assinatura RENOVA IA libera o chat, Modo Execução, memória de preferências\n            e análises por conversa.\n          </p>\n          <div class="gate-benefits">\n            <span>✓ Chat financeiro IA</span>\n            <span>✓ Lançamentos por conversa</span>\n            <span>✓ Metas e orçamentos por comando</span>\n            <span>✓ Memória das suas preferências</span>\n            <span>✓ Modo Execução</span>\n          </div>\n        </section>\n        """.replace("9,90", f"{price:.2f}".replace(".", ",")),\n        unsafe_allow_html=True,\n    )'''
new_sales = '''    hero(\n        "Personalize sua <strong>RENOVA IA</strong>",\n        "A IA Padrão já é gratuita. A assinatura libera memória, regras e treinamento exclusivos para sua conta.",\n    )\n\n    st.markdown(\n        f"""\n        <section class="ai-subscribe-gate">\n          <div class="sales-eyebrow">RENOVA IA PERSONALIZADA</div>\n          <h2>Treinamento exclusivo por <strong>R$ {price:,.2f}/mês</strong></h2>\n          <p>\n            Continue usando a IA Padrão gratuitamente para lançar receitas, despesas, consultar e analisar.\n            No Premium, você ensina o seu jeito de trabalhar e a IA passa a usar memória privada da sua conta.\n          </p>\n          <div class="gate-benefits">\n            <span>✓ Tudo da IA Padrão gratuita</span>\n            <span>✓ Regras e preferências permanentes</span>\n            <span>✓ Vocabulário e conta padrão</span>\n            <span>✓ Estudo de PDFs e YouTube</span>\n            <span>✓ Memória personalizada privada</span>\n          </div>\n        </section>\n        """.replace("9,90", f"{price:.2f}".replace(".", ",")),\n        unsafe_allow_html=True,\n    )'''
app = replace_once(app, old_sales, new_sales, "subscription sales")
app = replace_once(
    app,
    '            "Assinar RENOVA IA por R$ 9,90/mês com Mercado Pago",',
    '            "Ativar IA Personalizada por R$ 9,90/mês com Mercado Pago",',
    "subscription button",
)
app = replace_once(
    app,
    '        st.caption("Após a confirmação do Mercado Pago, o acesso à IA será liberado automaticamente.")',
    '        st.caption("Após a confirmação do Mercado Pago, o treinamento personalizado será liberado automaticamente.")',
    "subscription caption",
)

old_dialog = '''@st.dialog("🤖 Assistente Financeiro IA", width="large")\ndef open_ai_dialog() -> None:\n    if not has_renova_ai_access():\n        st.warning("O chat com a RENOVA IA é exclusivo do plano RENOVA IA.")\n        plan = get_ai_plan() if REAL_MODE else None\n        price = float(plan.get("price", 9.90)) if plan else 9.90\n        st.markdown(\n            f"Ative o plano por **R$ {price:.2f}/mês** para usar o Assistente Financeiro IA."\n        )\n        if st.button("Ver plano RENOVA IA", use_container_width=True):\n            st.session_state.nav_page = "Assinar RENOVA IA"\n            st.rerun()\n        return\n\n    st.caption("Converse sem sair desta tela. A IA pode executar as ações permitidas para sua conta.")\n    st.page_link("pages/Treinamento_IA.py", label="Treinar minha IA", icon="🧠", use_container_width=True)\n    render_ai_chat("ai_modal_input", fragment_rerun=True)\n'''
new_dialog = '''@st.dialog("🤖 Assistente Financeiro IA", width="large")\ndef open_ai_dialog() -> None:\n    personalized = has_personalized_ai_training_access()\n    if personalized:\n        st.caption("IA Personalizada ativa: execução financeira + memória e treinamentos da sua conta.")\n        st.page_link("pages/Treinamento_IA.py", label="🧠 Treinar minha IA", use_container_width=True)\n    else:\n        st.caption("IA Padrão gratuita ativa: lançamentos, consultas, análises e gestão essencial pelo chat.")\n        if st.button("🧠 Desbloquear treinamento personalizado", key="modal_upgrade_training", use_container_width=True):\n            st.session_state.nav_page = "Assinar RENOVA IA"\n            st.rerun()\n    render_ai_chat("ai_modal_input", fragment_rerun=True)\n'''
app = replace_once(app, old_dialog, new_dialog, "ai dialog")

old_render_ai = '''def render_ai() -> None:\n    if not has_renova_ai_access():\n        render_ai_subscription_sales()\n        return\n\n    hero(\n        "RENOVA IA <strong>Financeira</strong>",\n        "Converse com sua gestão financeira. A IA analisa e executa ações quando você pedir.",\n    )\n    st.caption("🧠 A IA aprende preferências, regras e materiais de treinamento vinculados à sua conta.")\n    st.page_link("pages/Treinamento_IA.py", label="Treinar minha IA", icon="🧠", use_container_width=True)\n    render_ai_chat("ai_page_input")\n'''
new_render_ai = '''def render_ai() -> None:\n    personalized = has_personalized_ai_training_access()\n    hero(\n        "RENOVA IA <strong>Financeira</strong>",\n        "Converse com sua gestão financeira. A IA Padrão gratuita já executa lançamentos, consultas e análises.",\n    )\n    if personalized:\n        st.success("🧠 IA Personalizada ativa — seus treinamentos, regras e memória privada podem ser usados pelo chat.")\n        st.page_link("pages/Treinamento_IA.py", label="Treinar minha IA", icon="🧠", use_container_width=True)\n    else:\n        st.info(\n            "🤖 **IA Padrão gratuita ativa.** Ela já sabe criar receitas e despesas, entender vencimentos, "\n            "consultar seus números, analisar urgências e executar a gestão essencial. "\n            "O treinamento com regras próprias e materiais é exclusivo da assinatura."\n        )\n        if st.button("🧠 Quero personalizar minha IA", key="page_upgrade_training", use_container_width=True):\n            st.session_state.nav_page = "Assinar RENOVA IA"\n            st.rerun()\n    render_ai_chat("ai_page_input")\n'''
app = replace_once(app, old_render_ai, new_render_ai, "render ai")

app = replace_once(
    app,
    '    plan_label = "RENOVA IA ativa" if ai_active else "Plano Gratuito"',
    '    plan_label = "IA Personalizada • Premium" if ai_active else "IA Padrão • Gratuito"',
    "sidebar plan",
)

old_fab = '''if AI_FAB_CLICKED:\n    if has_renova_ai_access():\n        open_ai_dialog()\n    else:\n        st.session_state.nav_page = "Assinar RENOVA IA"\n        st.rerun()\n'''
new_fab = '''if AI_FAB_CLICKED:\n    open_ai_dialog()\n'''
app = replace_once(app, old_fab, new_fab, "floating ai")

APP.write_text(app, encoding="utf-8")

page = TRAINING_PAGE.read_text(encoding="utf-8")
page = replace_once(
    page,
    '<h1>🧠 Treinamento da <strong>RENOVA IA</strong></h1>',
    '<h1>🧠 Treinamento <strong>Personalizado da RENOVA IA</strong></h1>',
    "training hero",
)
page = replace_once(
    page,
    '    st.warning("🧠 O Treinamento da IA é exclusivo para assinantes RENOVA IA.")',
    '    st.warning("🧠 O Treinamento Personalizado é exclusivo para assinantes RENOVA IA.")',
    "training gate",
)
page = replace_once(
    page,
    '        "No plano RENOVA IA, cada usuário possui uma memória de treinamento própria, isolada e protegida pelo Supabase."',
    '        "Sua conta gratuita já possui a IA Padrão para gestão financeira. No Premium, você libera uma memória de treinamento própria, isolada e protegida pelo Supabase."',
    "training gate copy",
)
TRAINING_PAGE.write_text(page, encoding="utf-8")

print("Patch do tier gratuito da RENOVA IA aplicado com sucesso.")
