from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def sub_once(text: str, pattern: str, replacement: str, label: str, *, flags: int = 0) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise RuntimeError(f"Patch não encontrou alvo único: {label} (encontrados={count})")
    return updated


# ---------------------------------------------------------------------------
# 1) Tema base: RENOVA Dark V2 — azul-marinho + ciano + azul + roxo.
# ---------------------------------------------------------------------------
theme_path = "src/theme.py"
theme = read(theme_path)

theme = sub_once(
    theme,
    r'PALETTE = \{.*?\}\n\n\ndef apply_renova_theme',
    '''PALETTE = {
    "bg": "#061426",
    "surface": "#0B2038",
    "surface_2": "#102B49",
    "gold": "#7457FF",       # alias legado: agora é o acento violeta RENOVA
    "gold_dark": "#5E45E8",
    "blue": "#19D9FF",
    "blue_dark": "#087FF5",
    "text": "#F5FAFF",
    "muted": "#A7BED4",
    "success": "#18DFA5",
    "danger": "#FF5E6C",
    "info": "#68D3FF",
}


def apply_renova_theme''',
    "PALETTE",
    flags=re.S,
)

theme = sub_once(
    theme,
    r':root\{.*?\n\}',
    ''':root{
  --rv-bg:#061426;
  --rv-bg2:#081A2F;
  --rv-panel:#0B2038;
  --rv-panel2:#102B49;
  --rv-blue:#19D9FF;
  --rv-blue2:#087FF5;
  --rv-gold:#7457FF;
  --rv-gold2:#A997FF;
  --rv-text:#F5FAFF;
  --rv-muted:#A7BED4;
  --rv-green:#18DFA5;
  --rv-red:#FF5E6C;
}''',
    "CSS tokens",
    flags=re.S,
)

theme = sub_once(
    theme,
    r'/\* BOTÕES \*/.*?/\* TABS \*/',
    '''/* BOTÕES — RENOVA Dark V2 */
.stButton>button,.stLinkButton>a,[data-testid="stFormSubmitButton"] button,[data-testid="stDownloadButton"] button{
  background:linear-gradient(112deg,#087FF5 0%,#19D9FF 48%,#7457FF 100%)!important;
  color:#FFFFFF!important;-webkit-text-fill-color:#FFFFFF!important;
  border:1px solid rgba(25,217,255,.76)!important;border-radius:11px!important;
  font-weight:950!important;min-height:43px!important;
  box-shadow:0 7px 20px rgba(0,0,0,.28),0 0 16px rgba(25,217,255,.14)!important;
  transition:.18s ease!important;
}
.stButton>button *,.stLinkButton>a *{color:#FFFFFF!important;-webkit-text-fill-color:#FFFFFF!important}
.stButton>button:hover,.stLinkButton>a:hover,[data-testid="stFormSubmitButton"] button:hover,[data-testid="stDownloadButton"] button:hover{
  background:linear-gradient(112deg,#7457FF 0%,#087FF5 48%,#19D9FF 100%)!important;
  color:#FFFFFF!important;-webkit-text-fill-color:#FFFFFF!important;
  border-color:#A7F2FF!important;
  box-shadow:0 10px 26px rgba(0,0,0,.34),0 0 24px rgba(25,217,255,.22),0 0 18px rgba(116,87,255,.16)!important;
  transform:translateY(-1px)!important;
}
.stButton>button:hover *,.stLinkButton>a:hover *{color:#FFFFFF!important;-webkit-text-fill-color:#FFFFFF!important}

/* TABS */''',
    "botões",
    flags=re.S,
)

DARK_V2 = r'''

/* ========================================================================
   RENOVA DARK V2 • Identidade oficial inspirada na campanha institucional
   ======================================================================== */
html,body,.stApp{background:#061426!important;color:#F5FAFF!important}
.stApp{
  background-image:
    linear-gradient(rgba(25,217,255,.035) 1px,transparent 1px),
    linear-gradient(90deg,rgba(25,217,255,.035) 1px,transparent 1px),
    radial-gradient(circle at 46% -8%,rgba(8,127,245,.18),transparent 38%),
    radial-gradient(circle at 92% 14%,rgba(116,87,255,.14),transparent 27%),
    radial-gradient(circle at 4% 82%,rgba(25,217,255,.07),transparent 28%),
    linear-gradient(135deg,#061426 0%,#081A2F 52%,#061426 100%)!important;
}
[data-testid="stHeader"]{
  background:rgba(6,20,38,.88)!important;
  border-bottom:1px solid rgba(25,217,255,.12)!important;
}
[data-testid="stSidebar"]>div:first-child{
  background:linear-gradient(180deg,rgba(7,20,37,.98),rgba(8,26,47,.97))!important;
  border-right:1px solid rgba(25,217,255,.20)!important;
}
.renova-brand{
  border-color:rgba(25,217,255,.30)!important;
  background:radial-gradient(circle at 50% 0%,rgba(25,217,255,.16),transparent 48%),linear-gradient(145deg,#0B2038,#071425)!important;
}
.renova-brand .gold,.renova-brand .status-chip.gold{color:#A997FF!important}
.renova-brand .status-chip.gold{border-color:rgba(116,87,255,.34)!important;background:rgba(116,87,255,.09)!important}
.renova-brand:after,.metric-card:before,div[data-testid="stMetric"]:before{
  background:linear-gradient(90deg,transparent,#19D9FF,#087FF5,#7457FF,transparent)!important;
}
.renova-hero{
  border-color:rgba(25,217,255,.30)!important;
  background:linear-gradient(rgba(25,217,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(25,217,255,.04) 1px,transparent 1px),radial-gradient(circle at 88% 12%,rgba(25,217,255,.18),transparent 28%),radial-gradient(circle at 7% 115%,rgba(116,87,255,.13),transparent 34%),linear-gradient(125deg,#08192C 0%,#0B2038 48%,#061426 100%)!important;
}
.renova-hero:before{color:#19D9FF!important;text-shadow:0 0 15px rgba(25,217,255,.20)!important}
.renova-hero strong{color:#A997FF!important;text-shadow:0 0 18px rgba(116,87,255,.18)!important}
.metric-card,div[data-testid="stMetric"],[data-testid="stExpander"]{
  border-color:rgba(25,217,255,.24)!important;
  background:radial-gradient(circle at 92% 8%,rgba(25,217,255,.08),transparent 27%),linear-gradient(145deg,#0B2038,#0A1C31)!important;
}
.metric-card:hover,div[data-testid="stMetric"]:hover,[data-testid="stExpander"]:hover{border-color:rgba(116,87,255,.56)!important}
.metric-card .hint{color:#19D9FF!important}
[data-baseweb="input"]>div,[data-baseweb="textarea"]>div,[data-baseweb="select"]>div,div[data-testid="stNumberInput"] input{
  background:#0A1C31!important;border-color:rgba(25,217,255,.28)!important
}
[data-baseweb="input"]:focus-within,[data-baseweb="textarea"]:focus-within,[data-baseweb="select"]>div:focus-within{
  border-color:#19D9FF!important;box-shadow:0 0 0 2px rgba(25,217,255,.10),0 0 18px rgba(25,217,255,.10)!important
}
[data-baseweb="tab-list"]{background:linear-gradient(145deg,#0B2038,#081A2F)!important;border-color:rgba(25,217,255,.22)!important}
[data-baseweb="tab"][aria-selected="true"]{
  color:#FFFFFF!important;border-color:rgba(25,217,255,.62)!important;
  background:linear-gradient(120deg,rgba(8,127,245,.34),rgba(25,217,255,.20),rgba(116,87,255,.30))!important;
  box-shadow:0 0 20px rgba(25,217,255,.10)!important
}
[data-testid="stPlotlyChart"],[data-testid="stDataFrame"]{
  border-color:rgba(25,217,255,.20)!important;
  background:linear-gradient(145deg,#0B2038,#081A2F)!important;
  box-shadow:0 12px 30px rgba(0,0,0,.24)!important
}
[data-testid="stAlert"]{border-color:rgba(25,217,255,.22)!important;box-shadow:inset 3px 0 0 rgba(25,217,255,.22)!important}
[data-testid="stProgress"]>div>div>div>div{background:linear-gradient(90deg,#087FF5,#19D9FF,#7457FF)!important}
.sales-cta.primary{background:linear-gradient(112deg,#087FF5,#19D9FF 50%,#7457FF)!important;color:#FFFFFF!important;border-color:rgba(25,217,255,.72)!important}
.sales-badge,.sales-eyebrow,.popular{color:#19D9FF!important}
.sales-hero h1 strong,.sales-section h2 strong,.ai-sales h2 strong,.pricing-section h2 strong,.sales-final h2 strong{color:#A997FF!important}
.price-card.featured{border-color:rgba(116,87,255,.58)!important;box-shadow:0 18px 45px rgba(0,0,0,.35),0 0 26px rgba(116,87,255,.10)!important}
.st-key-renova_ai_fab button{
  border-color:rgba(25,217,255,.72)!important;
  background:linear-gradient(135deg,#0B2038,#0A2E52 58%,#172B55)!important;
  color:#F5FAFF!important;-webkit-text-fill-color:#F5FAFF!important;
  box-shadow:0 16px 38px rgba(0,0,0,.42),0 0 24px rgba(25,217,255,.20),0 0 18px rgba(116,87,255,.14)!important
}
.st-key-renova_ai_fab button *{color:#F5FAFF!important;-webkit-text-fill-color:#F5FAFF!important}
.st-key-renova_ai_fab button:hover{border-color:#A997FF!important;background:linear-gradient(135deg,#172B55,#087FF5 58%,#0B2038)!important;color:#FFFFFF!important;-webkit-text-fill-color:#FFFFFF!important}
.st-key-urgencies_open_transactions button{
  background:#0B2038!important;border:1px solid rgba(25,217,255,.58)!important;color:#F5FAFF!important;-webkit-text-fill-color:#F5FAFF!important
}
.st-key-urgencies_open_transactions button *{color:#F5FAFF!important;-webkit-text-fill-color:#F5FAFF!important}
.st-key-urgencies_open_ai button{
  background:linear-gradient(112deg,#087FF5,#19D9FF 48%,#7457FF)!important;border:1px solid rgba(25,217,255,.78)!important;color:#FFFFFF!important;-webkit-text-fill-color:#FFFFFF!important
}
.st-key-urgencies_open_ai button *{color:#FFFFFF!important;-webkit-text-fill-color:#FFFFFF!important}
[data-testid="stDialog"]>div{border-color:rgba(25,217,255,.34)!important;background:linear-gradient(145deg,#08192C,#061426)!important}
#renova-mobile-nav .rv-mobile-brand span{color:#19D9FF!important}
#renova-mobile-nav .rv-mobile-nav-inner{border-color:rgba(25,217,255,.42)!important}
'''

marker = '@media(prefers-reduced-motion:reduce){\n  *{animation:none!important;scroll-behavior:auto!important;transition:none!important}\n}'
if "RENOVA DARK V2" not in theme:
    if marker not in theme:
        raise RuntimeError("Marcador final do CSS não encontrado em theme.py")
    theme = theme.replace(marker, DARK_V2 + "\n" + marker, 1)

write(theme_path, theme)


# ---------------------------------------------------------------------------
# 2) Plotly / sistema visual: mesma família cromática.
# ---------------------------------------------------------------------------
visual_path = "src/visual_system.py"
visual = read(visual_path)
visual = sub_once(
    visual,
    r'COLORS = \{.*?\}\n\n_DATE_COLUMNS',
    '''COLORS = {
    "bg": "#061426",
    "panel": "#0B2038",
    "panel_2": "#102B49",
    "blue": "#19D9FF",
    "blue_2": "#087FF5",
    "gold": "#7457FF",
    "gold_2": "#A997FF",
    "green": "#18DFA5",
    "red": "#FF5E6C",
    "white": "#F5FAFF",
    "muted": "#A7BED4",
}

_DATE_COLUMNS''',
    "COLORS",
    flags=re.S,
)
visual = visual.replace('"#7B8CFF",\n                "#19D3F3",\n                "#FF9F40",', '"#A997FF",\n                "#4A9DFF",\n                "#18DFA5",')
visual = visual.replace('"linecolor": "rgba(255,215,90,.18)"', '"linecolor": "rgba(116,87,255,.20)"')
write(visual_path, visual)


# ---------------------------------------------------------------------------
# 3) Sidebar desktop: controles sem dourado residual.
# ---------------------------------------------------------------------------
shell_path = "src/ui/desktop_shell.py"
shell = read(shell_path)
shell = shell.replace('border:1px solid rgba(247,214,100,.88);', 'border:1px solid rgba(25,217,255,.64);')
shell = shell.replace('background:linear-gradient(120deg,#061827 0%,#07508a 65%,#0090f0 100%);', 'background:linear-gradient(120deg,#0B2038 0%,#087FF5 58%,#19D9FF 100%);')
shell = shell.replace('color:#ffe477;', 'color:#19D9FF;').replace('-webkit-text-fill-color:#ffe477;', '-webkit-text-fill-color:#19D9FF;')
shell = shell.replace('border-color:#fff0a3;', 'border-color:#A997FF;')
write(shell_path, shell)


# ---------------------------------------------------------------------------
# 4) Card do Ecossistema: CSS autocontido. Corrige o texto "solto" observado.
# ---------------------------------------------------------------------------
sidebar_path = "src/sidebar_runtime.py"
sidebar = read(sidebar_path)
new_card = '''def render_ecosystem_product_card(st_ref=st) -> None:
    markup = f"""
    <style>
      .renova-ecosystem-offer{{
        position:relative;overflow:hidden;margin:10px 0 5px;padding:14px;border-radius:16px;
        border:1px solid rgba(25,217,255,.38);
        background:radial-gradient(circle at 100% 0%,rgba(116,87,255,.18),transparent 42%),linear-gradient(145deg,#0B2038,#081A2F);
        box-shadow:0 12px 28px rgba(0,0,0,.22),0 0 20px rgba(25,217,255,.06);
        font-family:Inter,Arial,sans-serif;
      }}
      .renova-ecosystem-offer:before{{
        content:"";position:absolute;left:0;right:0;top:0;height:2px;
        background:linear-gradient(90deg,transparent,#19D9FF,#087FF5,#7457FF,transparent)
      }}
      .renova-offer-kicker{{color:#19D9FF;font-size:.52rem;font-weight:950;letter-spacing:.14em;margin-bottom:7px}}
      .renova-offer-title{{color:#F5FAFF;font-size:.92rem;font-weight:950;line-height:1.15}}
      .renova-offer-copy{{color:#A7BED4;font-size:.63rem;line-height:1.45;margin:6px 0 10px}}
      .renova-offer-benefits{{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin:0 0 10px}}
      .renova-offer-benefit{{padding:7px 8px;border-radius:9px;background:rgba(25,217,255,.055);border:1px solid rgba(25,217,255,.13);color:#DDF8FF;font-size:.52rem;font-weight:850;line-height:1.25}}
      .renova-offer-cta{{display:flex;align-items:center;justify-content:center;min-height:35px;padding:0 10px;border-radius:10px;text-decoration:none!important;background:linear-gradient(112deg,#087FF5,#19D9FF 50%,#7457FF);border:1px solid rgba(25,217,255,.72);color:#FFFFFF!important;font-size:.58rem;font-weight:950;box-shadow:0 7px 18px rgba(0,0,0,.22),0 0 14px rgba(25,217,255,.10);transition:.18s ease}}
      .renova-offer-cta:hover{{transform:translateY(-1px);filter:brightness(1.08)}}
    </style>
    <section class="renova-ecosystem-offer" aria-label="Oferta Ecossistema RENOVA">
      <div class="renova-offer-kicker">ECOSSISTEMA RENOVA</div>
      <div class="renova-offer-title">Seu próximo nível de gestão digital</div>
      <div class="renova-offer-copy">Ferramentas, conteúdos e oportunidades para organizar, vender, crescer e acompanhar seus resultados.</div>
      <div class="renova-offer-benefits">
        <div class="renova-offer-benefit">⚙️ Gestão digital</div>
        <div class="renova-offer-benefit">🤝 Área de afiliados</div>
        <div class="renova-offer-benefit">🛍️ Produtos e serviços</div>
        <div class="renova-offer-benefit">✦ IA de apoio</div>
      </div>
      <a class="renova-offer-cta" href="{ECOSSISTEMA_RENOVA_PUBLIC_URL}" target="_blank" rel="noopener noreferrer">Conhecer o Ecossistema RENOVA ↗</a>
    </section>
    """
    html_renderer = getattr(st_ref, "html", None)
    if callable(html_renderer):
        html_renderer(markup)
    else:
        st_ref.markdown(markup, unsafe_allow_html=True)
'''
sidebar = sub_once(
    sidebar,
    r'def render_ecosystem_product_card\(st_ref=st\) -> None:.*?\n\ndef auto_collapse_sidebar_robust',
    new_card + '\n\ndef auto_collapse_sidebar_robust',
    "card Ecossistema",
    flags=re.S,
)
write(sidebar_path, sidebar)


# ---------------------------------------------------------------------------
# 5) Streamlit nativo alinhado ao modo escuro RENOVA.
# ---------------------------------------------------------------------------
config_path = ".streamlit/config.toml"
config = read(config_path)
config = config.replace('primaryColor = "#FFD75A"', 'primaryColor = "#19D9FF"')
config = config.replace('backgroundColor = "#02070C"', 'backgroundColor = "#061426"')
config = config.replace('secondaryBackgroundColor = "#07131D"', 'secondaryBackgroundColor = "#0B2038"')
config = config.replace('textColor = "#F7FAFC"', 'textColor = "#F5FAFF"')
write(config_path, config)

print("RENOVA Dark V2 aplicado com sucesso.")
