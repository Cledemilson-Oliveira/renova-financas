from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8")


# -----------------------------------------------------------------------------
# 1) APP: menu de módulos mobile nativo do Streamlit.
# -----------------------------------------------------------------------------
app = read("app.py")

anchor = '''if "nav_page" not in st.session_state:\n    st.session_state.nav_page = "Dashboard"\n\nwith st.sidebar:\n'''

mobile_menu = '''if "nav_page" not in st.session_state:\n    st.session_state.nav_page = "Dashboard"\n\n\ndef render_mobile_modules_menu() -> None:\n    \"\"\"Menu mobile nativo e sempre visível, sem depender de JavaScript injetado.\"\"\"\n    mobile_icons = {\n        "Dashboard": "🏠",\n        "Lançamentos": "💸",\n        "Categorias": "🏷️",\n        "Contas": "🏦",\n        "Cartões": "💳",\n        "Orçamentos": "🎯",\n        "Análises": "📊",\n        "Relatórios": "📄",\n        "RENOVA IA": "🤖",\n        "Treinamento IA": "🧠",\n        "Assinar RENOVA IA": "⭐",\n    }\n    current = str(st.session_state.get("nav_page") or "Dashboard")\n    current_icon = mobile_icons.get(current, "•")\n\n    with st.container(key="renova_fin_mobile_nav"):\n        with st.popover(\n            f"☰  MÓDULOS  •  {current_icon} {current}",\n            use_container_width=True,\n        ):\n            st.markdown("**NAVEGAÇÃO RENOVA FINANÇAS**")\n            st.caption("Escolha o módulo que deseja abrir.")\n            for destination in NAV_PAGES:\n                icon = mobile_icons.get(destination, "•")\n                if st.button(\n                    f"{icon}  {destination}",\n                    key=f"mobile_module_{destination}",\n                    use_container_width=True,\n                    type="primary" if destination == current else "secondary",\n                ):\n                    st.session_state.nav_page = destination\n                    st.session_state._last_nav_page = destination\n                    st.rerun()\n\n\nrender_mobile_modules_menu()\n\nwith st.sidebar:\n'''

if 'key="renova_fin_mobile_nav"' not in app:
    if anchor not in app:
        raise SystemExit("Âncora de navegação do app.py não encontrada")
    app = app.replace(anchor, mobile_menu, 1)

write("app.py", app)


# -----------------------------------------------------------------------------
# 2) THEME: remove navegação JS frágil e melhora contraste mobile.
# -----------------------------------------------------------------------------
theme = read("src/theme.py")

theme = theme.replace(
    "    install_mobile_navigation()\n",
    "    # O menu mobile é renderizado nativamente no app.py para maior estabilidade.\n",
    1,
)

css_anchor = '''@media(prefers-reduced-motion:reduce){\n  *{animation:none!important;scroll-behavior:auto!important;transition:none!important}\n}\n'''

mobile_css = '''/* ========================================================================\n   MOBILE V3 • contraste leve + menu de módulos nativo sempre acessível\n   ======================================================================== */\n.st-key-renova_fin_mobile_nav{display:none!important}\n\n@media(max-width:900px){\n  /* A navegação mobile não depende mais da sidebar ou de injeção JavaScript. */\n  #renova-mobile-nav{display:none!important}\n  .st-key-renova_fin_mobile_nav{\n    display:block!important;\n    position:fixed!important;\n    top:8px!important;left:10px!important;right:10px!important;\n    z-index:10050!important;\n    margin:0!important;\n    filter:drop-shadow(0 10px 24px rgba(2,12,24,.32))!important;\n  }\n  .st-key-renova_fin_mobile_nav button{\n    width:100%!important;min-height:52px!important;\n    border-radius:15px!important;\n    border:1px solid rgba(25,217,255,.58)!important;\n    background:linear-gradient(135deg,#123A5D 0%,#0F3150 55%,#17365D 100%)!important;\n    color:#F8FCFF!important;-webkit-text-fill-color:#F8FCFF!important;\n    font-size:.88rem!important;font-weight:950!important;\n    box-shadow:0 10px 24px rgba(0,0,0,.24),0 0 18px rgba(25,217,255,.11),inset 0 1px rgba(255,255,255,.08)!important;\n  }\n  .st-key-renova_fin_mobile_nav button *{\n    color:#F8FCFF!important;-webkit-text-fill-color:#F8FCFF!important;font-weight:950!important;\n  }\n  [data-testid="stMainBlockContainer"]{\n    padding-top:5.45rem!important;\n  }\n\n  /* Superfícies menos pesadas: azul intermediário, borda leve e sombra externa. */\n  .metric-card,\n  div[data-testid="stMetric"],\n  [data-testid="stExpander"],\n  [data-testid="stPlotlyChart"],\n  [data-testid="stDataFrame"],\n  [data-testid="stForm"]{\n    border-color:rgba(64,207,255,.30)!important;\n    background:\n      radial-gradient(circle at 92% 7%,rgba(25,217,255,.10),transparent 29%),\n      linear-gradient(145deg,rgba(18,52,82,.96),rgba(12,38,64,.95))!important;\n    box-shadow:\n      0 10px 24px rgba(1,13,27,.26),\n      0 0 18px rgba(25,217,255,.075),\n      inset 0 1px rgba(255,255,255,.055)!important;\n  }\n  .metric-card{min-height:102px!important;padding:15px 16px!important}\n  .metric-card .label,div[data-testid="stMetric"] label{color:#C8DDEB!important}\n  .metric-card .hint{color:#71E6FF!important}\n  .metric-card .value,div[data-testid="stMetric"] [data-testid="stMetricValue"]{\n    color:#FFFFFF!important;-webkit-text-fill-color:#FFFFFF!important;\n    text-shadow:0 1px 16px rgba(25,217,255,.08)!important;\n  }\n\n  .renova-hero{\n    border-color:rgba(64,207,255,.32)!important;\n    background:\n      linear-gradient(rgba(25,217,255,.026) 1px,transparent 1px),\n      linear-gradient(90deg,rgba(25,217,255,.026) 1px,transparent 1px),\n      radial-gradient(circle at 88% 12%,rgba(25,217,255,.13),transparent 30%),\n      linear-gradient(135deg,#123A5D 0%,#0E2D4B 55%,#0B2540 100%)!important;\n    box-shadow:0 12px 28px rgba(1,13,27,.28),0 0 18px rgba(25,217,255,.08)!important;\n  }\n\n  [data-baseweb="tab-list"]{\n    background:linear-gradient(145deg,#123A5D,#0E2D4B)!important;\n    border-color:rgba(64,207,255,.28)!important;\n    box-shadow:0 8px 20px rgba(1,13,27,.20)!important;\n  }\n\n  [data-testid="stAlert"]{\n    background:linear-gradient(135deg,rgba(18,52,82,.96),rgba(12,38,64,.96))!important;\n    border-color:rgba(64,207,255,.28)!important;\n    box-shadow:0 8px 20px rgba(1,13,27,.20),inset 3px 0 rgba(25,217,255,.22)!important;\n  }\n}\n\n'''

if "MOBILE V3 • contraste leve" not in theme:
    if css_anchor not in theme:
        raise SystemExit("Âncora CSS final do theme.py não encontrada")
    theme = theme.replace(css_anchor, mobile_css + css_anchor, 1)

write("src/theme.py", theme)

print("Mobile RENOVA Finanças: contraste e menu de módulos corrigidos.")
