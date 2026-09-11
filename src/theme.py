from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from src.visual_system import RENOVA_LOGO_URL, configure_plotly

PALETTE = {
    "bg": "#02070D",
    "surface": "#06131F",
    "surface_2": "#081C2B",
    "gold": "#FFD75A",
    "gold_dark": "#D9A520",
    "blue": "#00AEEF",
    "blue_dark": "#05225A",
    "text": "#F7FBFF",
    "muted": "#AFC3D2",
    "success": "#35D07F",
    "danger": "#FF5E6C",
    "info": "#68D3FF",
}


def apply_renova_theme() -> None:
    configure_plotly()
    st.markdown(
        """
<style>
:root{
  --rv-bg:#02070D;
  --rv-bg2:#03121E;
  --rv-panel:#06131F;
  --rv-panel2:#081C2B;
  --rv-blue:#00AEEF;
  --rv-blue2:#0077FF;
  --rv-gold:#FFD75A;
  --rv-gold2:#D9A520;
  --rv-text:#F7FBFF;
  --rv-muted:#AFC3D2;
  --rv-green:#35D07F;
  --rv-red:#FF5E6C;
}

html,body,.stApp{
  background:#02070D!important;
  color:var(--rv-text)!important;
}

.stApp{
  background-image:
    linear-gradient(rgba(0,174,239,.038) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,174,239,.038) 1px,transparent 1px),
    radial-gradient(circle at 46% -8%,rgba(0,174,239,.17),transparent 38%),
    radial-gradient(circle at 93% 16%,rgba(255,215,90,.085),transparent 25%),
    radial-gradient(circle at 5% 82%,rgba(0,119,255,.08),transparent 28%),
    linear-gradient(135deg,#02070D 0%,#03111C 52%,#02080E 100%)!important;
  background-size:42px 42px,42px 42px,auto,auto,auto,auto!important;
  background-attachment:fixed!important;
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"]{background:transparent!important}

[data-testid="stMainBlockContainer"]{
  max-width:1480px!important;
  padding-top:2.05rem!important;
  padding-bottom:5rem!important;
  position:relative;
  z-index:1;
}

[data-testid="stHeader"]{
  background:rgba(2,7,13,.82)!important;
  backdrop-filter:blur(16px)!important;
  border-bottom:1px solid rgba(0,174,239,.10)!important;
}

[data-testid="stSidebar"]{
  background:transparent!important;
  border:0!important;
}
[data-testid="stSidebar"]>div:first-child{
  background:linear-gradient(180deg,rgba(2,8,14,.96),rgba(4,17,27,.94))!important;
  backdrop-filter:blur(18px)!important;
  border-right:1px solid rgba(0,174,239,.18)!important;
  box-shadow:12px 0 38px rgba(0,0,0,.25)!important;
}

h1,h2,h3,h4{color:var(--rv-text)!important;letter-spacing:-.025em!important}
p,label,.stCaption{color:var(--rv-muted)!important}

/* IDENTIDADE LATERAL */
.renova-brand{
  position:relative;
  overflow:hidden;
  margin:4px 4px 17px;
  padding:17px 14px 15px;
  text-align:center;
  border:1px solid rgba(0,174,239,.25);
  border-radius:20px;
  background:
    radial-gradient(circle at 50% 0%,rgba(0,174,239,.18),transparent 48%),
    linear-gradient(145deg,rgba(5,24,38,.98),rgba(2,9,15,.99));
  box-shadow:0 15px 30px rgba(0,0,0,.30),inset 0 1px rgba(255,255,255,.025);
}
.renova-brand:after{
  content:"";
  position:absolute;
  left:-45%;bottom:0;width:42%;height:2px;
  background:linear-gradient(90deg,transparent,var(--rv-blue),var(--rv-gold),transparent);
  box-shadow:0 0 13px rgba(0,174,239,.55);
  animation:rvBrandScan 5.5s ease-in-out infinite;
}
@keyframes rvBrandScan{0%,15%{left:-45%}78%,100%{left:112%}}
.renova-brand img{
  width:88px;
  max-width:45%;
  filter:drop-shadow(0 0 14px rgba(0,174,239,.25)) drop-shadow(0 0 8px rgba(255,215,90,.14));
  animation:rvLogoFloat 4.5s ease-in-out infinite;
}
@keyframes rvLogoFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
.renova-brand .kicker{
  margin-top:7px;
  color:#75D8FF;
  font-size:.58rem;
  font-weight:950;
  letter-spacing:.17em;
}
.renova-brand h2{margin:4px 0 0;color:#fff!important;font-size:1.17rem!important;font-weight:950!important}
.renova-brand .gold{color:var(--rv-gold)!important}
.renova-brand p{margin:5px 0 0;color:#AFC8D8!important;font-size:.72rem!important;font-weight:700}
.renova-brand .status-line{
  display:flex;justify-content:center;gap:6px;flex-wrap:wrap;margin-top:11px;
}
.renova-brand .status-chip{
  padding:4px 8px;border-radius:999px;font-size:.55rem;font-weight:900;letter-spacing:.05em;
  border:1px solid rgba(0,174,239,.20);color:#AEEBFF;background:rgba(0,174,239,.06);
}
.renova-brand .status-chip.gold{border-color:rgba(255,215,90,.24);color:#FFE477;background:rgba(255,215,90,.055)}

/* MENU */
[data-testid="stSidebar"] [data-testid="stRadio"]>label{display:none!important}
[data-testid="stSidebar"] [role="radiogroup"]{gap:8px!important;padding:3px 4px 16px!important}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]{
  position:relative!important;
  min-height:49px!important;
  padding:10px 13px!important;
  border-radius:15px!important;
  border:1px solid rgba(0,174,239,.25)!important;
  background:linear-gradient(135deg,rgba(5,23,37,.92),rgba(3,11,19,.87))!important;
  box-shadow:0 8px 22px rgba(0,0,0,.25),inset 0 0 18px rgba(0,174,239,.025)!important;
  transition:.2s ease!important;
  overflow:hidden!important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:before{
  content:"";position:absolute;inset:-1px auto -1px -55%;width:38%;
  background:linear-gradient(100deg,transparent,rgba(104,211,255,.16),transparent);
  transform:skewX(-18deg);transition:left .45s ease;pointer-events:none;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover{
  transform:translateX(5px)!important;
  border-color:rgba(0,195,255,.72)!important;
  background:linear-gradient(135deg,rgba(5,40,64,.97),rgba(3,16,28,.94))!important;
  box-shadow:0 10px 28px rgba(0,0,0,.33),0 0 20px rgba(0,174,255,.14)!important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover:before{left:125%}
[data-testid="stSidebar"] [data-testid="stRadio"] label p{
  color:#EAF7FF!important;font-weight:780!important;font-size:.91rem!important;margin:0!important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]>div:first-child{
  width:11px!important;height:11px!important;min-width:11px!important;margin-right:9px!important;
  background:#061725!important;border:1.5px solid #00B8FF!important;box-shadow:0 0 10px rgba(0,184,255,.50)!important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked){
  border-color:rgba(255,215,90,.84)!important;
  background:linear-gradient(120deg,rgba(38,31,7,.94),rgba(7,28,43,.96))!important;
  box-shadow:0 10px 28px rgba(0,0,0,.36),0 0 22px rgba(255,215,90,.13),inset 0 0 18px rgba(255,215,90,.05)!important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked)>div:first-child{
  background:var(--rv-gold)!important;border-color:#FFF1A4!important;box-shadow:0 0 14px rgba(255,215,90,.78)!important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) p{color:#FFE477!important;font-weight:950!important}

/* HERO */
.renova-hero{
  position:relative;
  overflow:hidden;
  border:1px solid rgba(255,215,90,.30);
  border-radius:22px;
  padding:30px 27px 25px;
  margin-bottom:19px;
  background:
    linear-gradient(rgba(0,174,239,.045) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,174,239,.045) 1px,transparent 1px),
    radial-gradient(circle at 88% 12%,rgba(0,174,239,.22),transparent 28%),
    radial-gradient(circle at 7% 115%,rgba(255,215,90,.13),transparent 34%),
    linear-gradient(125deg,#04111C 0%,#061D31 46%,#02070D 100%);
  background-size:28px 28px,28px 28px,auto,auto,auto;
  box-shadow:0 20px 48px rgba(0,0,0,.38),0 0 32px rgba(0,174,239,.075),inset 0 1px rgba(255,255,255,.035);
}
.renova-hero:before{
  content:"RENOVA FINANÇAS • CENTRAL INTELIGENTE";
  display:block;
  color:var(--rv-gold);
  font-size:.61rem;font-weight:950;letter-spacing:.16em;margin-bottom:9px;
  text-shadow:0 0 15px rgba(255,215,90,.22);
}
.renova-hero:after{
  content:"";position:absolute;left:-36%;bottom:0;width:36%;height:2px;
  background:linear-gradient(90deg,transparent,var(--rv-blue),var(--rv-gold),transparent);
  box-shadow:0 0 14px rgba(0,174,239,.38);
  animation:rvHeroScan 5.1s ease-in-out infinite;
}
@keyframes rvHeroScan{0%,18%{left:-36%}76%,100%{left:110%}}
.renova-hero h1{margin:0;color:#fff!important;font-size:clamp(1.85rem,4vw,2.85rem)!important;font-weight:950!important;letter-spacing:-.045em!important}
.renova-hero strong{color:var(--rv-gold)!important;text-shadow:0 0 18px rgba(255,215,90,.16)}
.renova-hero p{color:#BED0DC!important;margin:9px 0 0!important;font-size:.96rem!important;max-width:880px}

/* CARDS E KPIs */
.metric-card,div[data-testid="stMetric"],[data-testid="stExpander"]{
  position:relative!important;
  overflow:hidden!important;
  border:1px solid rgba(0,174,239,.22)!important;
  background:radial-gradient(circle at 92% 8%,rgba(0,174,239,.11),transparent 27%),linear-gradient(145deg,rgba(7,24,38,.97),rgba(3,10,16,.99))!important;
  border-radius:18px!important;
  box-shadow:0 14px 34px rgba(0,0,0,.30),inset 0 1px rgba(255,255,255,.025)!important;
  transition:transform .2s ease,border-color .2s ease,box-shadow .2s ease!important;
}
.metric-card{padding:18px 18px;min-height:124px}
.metric-card:before,div[data-testid="stMetric"]:before{
  content:"";position:absolute;left:0;right:0;top:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--rv-blue),var(--rv-gold),transparent);opacity:.82;
}
.metric-card:hover,div[data-testid="stMetric"]:hover,[data-testid="stExpander"]:hover{
  transform:translateY(-3px)!important;
  border-color:rgba(255,215,90,.48)!important;
  box-shadow:0 18px 42px rgba(0,0,0,.36),0 0 24px rgba(0,174,239,.09)!important;
}
.metric-card .label{color:#9FB7C8;font-size:.76rem;font-weight:850;letter-spacing:.02em}
.metric-card .value{color:#fff;font-size:clamp(1.35rem,2.2vw,1.75rem);font-weight:950;margin-top:10px;letter-spacing:-.035em}
.metric-card .hint{color:var(--rv-gold);font-size:.72rem;font-weight:800;margin-top:7px}
div[data-testid="stMetric"]{padding:17px!important;min-height:118px}
div[data-testid="stMetric"] label{color:#9FB7C8!important;font-size:.76rem!important;font-weight:850!important}
div[data-testid="stMetric"] [data-testid="stMetricValue"]{color:#fff!important;font-weight:950!important;letter-spacing:-.035em!important}

/* FORMULÁRIOS */
[data-baseweb="input"]>div,[data-baseweb="textarea"]>div,[data-baseweb="select"]>div,
div[data-testid="stNumberInput"] input{
  background:#06131E!important;color:#fff!important;
  border:1px solid rgba(0,174,239,.25)!important;border-radius:11px!important;
}
[data-baseweb="input"]:focus-within,[data-baseweb="textarea"]:focus-within,[data-baseweb="select"]>div:focus-within{
  border-color:var(--rv-gold)!important;
  box-shadow:0 0 0 2px rgba(0,174,239,.08),0 0 16px rgba(0,174,239,.08)!important;
}
[data-testid="stForm"]{
  border:1px solid rgba(0,174,239,.16)!important;
  border-radius:18px!important;
  padding:18px!important;
  background:linear-gradient(145deg,rgba(5,20,32,.82),rgba(2,9,15,.72))!important;
}

/* BOTÕES */
.stButton>button,.stLinkButton>a,[data-testid="stFormSubmitButton"] button,[data-testid="stDownloadButton"] button{
  background:linear-gradient(110deg,#C99308,#FFCA2C 30%,#FFF0A3 49%,#FFD75A 63%,#D8A716)!important;
  color:#06111B!important;-webkit-text-fill-color:#06111B!important;
  border:1px solid #FFE57B!important;border-radius:11px!important;
  font-weight:950!important;min-height:43px!important;
  box-shadow:0 6px 17px rgba(0,0,0,.25),0 0 11px rgba(255,202,44,.10)!important;
  transition:.18s ease!important;
}
.stButton>button *,.stLinkButton>a *{color:#06111B!important;-webkit-text-fill-color:#06111B!important}
.stButton>button:hover,.stLinkButton>a:hover,[data-testid="stFormSubmitButton"] button:hover,[data-testid="stDownloadButton"] button:hover{
  background:linear-gradient(135deg,#03101B,#07305B 60%,#02070D)!important;
  color:var(--rv-gold)!important;-webkit-text-fill-color:var(--rv-gold)!important;
  border-color:var(--rv-gold)!important;
  box-shadow:0 0 20px rgba(0,174,239,.22),0 0 15px rgba(255,215,90,.16)!important;
  transform:translateY(-1px)!important;
}
.stButton>button:hover *,.stLinkButton>a:hover *{color:var(--rv-gold)!important;-webkit-text-fill-color:var(--rv-gold)!important}

/* TABS */
[data-baseweb="tab-list"]{
  gap:7px!important;padding:6px!important;margin:.35rem 0 .9rem!important;
  border:1px solid rgba(0,174,239,.18)!important;border-radius:14px!important;
  background:linear-gradient(145deg,rgba(4,17,28,.92),rgba(2,8,14,.96))!important;
}
[data-baseweb="tab"]{
  min-height:43px!important;padding:0 16px!important;border-radius:10px!important;
  border:1px solid transparent!important;background:rgba(7,19,29,.50)!important;
  color:#AFC3D2!important;font-weight:850!important;
}
[data-baseweb="tab"][aria-selected="true"]{
  color:#FFE477!important;border-color:rgba(255,215,90,.48)!important;
  background:linear-gradient(135deg,rgba(255,215,90,.11),rgba(0,174,239,.08))!important;
  box-shadow:0 0 18px rgba(0,174,239,.08)!important;
}

/* GRÁFICOS / TABELAS */
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"]{
  border:1px solid rgba(0,174,239,.16)!important;
  border-radius:18px!important;
  overflow:hidden!important;
  background:linear-gradient(145deg,rgba(5,19,30,.72),rgba(2,8,14,.68))!important;
  box-shadow:0 12px 30px rgba(0,0,0,.22)!important;
}
[data-testid="stPlotlyChart"]{padding:5px!important}

/* ALERTAS */
[data-testid="stAlert"]{
  border-radius:14px!important;
  border:1px solid rgba(0,174,239,.22)!important;
  background:linear-gradient(135deg,rgba(5,25,40,.94),rgba(3,11,19,.96))!important;
  color:#EAF7FF!important;
}
[data-testid="stProgress"]>div>div>div>div{
  background:linear-gradient(90deg,var(--rv-blue2),var(--rv-blue),var(--rv-gold))!important;
  box-shadow:0 0 15px rgba(0,174,239,.20)!important;
}

/* AUTH / LOGIN */
body:has(form#login_form) [data-testid="stMainBlockContainer"],
body:has(input[aria-label="E-mail"]) [data-testid="stMainBlockContainer"]{
  max-width:1180px!important;
}
body:has(input[aria-label="Senha"]) [data-testid="stForm"]{
  box-shadow:0 24px 65px rgba(0,0,0,.35),0 0 28px rgba(0,174,239,.07)!important;
}

/* CONTROLES STREAMLIT */
[data-testid="stSidebarCollapseButton"] button,[data-testid="stSidebarCollapsedControl"] button,[data-testid="collapsedControl"] button{
  border-radius:12px!important;border:1px solid rgba(255,215,90,.60)!important;
  background:linear-gradient(145deg,#071C2D,#03101A)!important;color:var(--rv-gold)!important;
  box-shadow:0 8px 22px rgba(0,0,0,.35),0 0 15px rgba(0,174,239,.16)!important;
}
[data-testid="stSidebarCollapseButton"] svg,[data-testid="stSidebarCollapsedControl"] svg,[data-testid="collapsedControl"] svg{
  color:var(--rv-gold)!important;fill:var(--rv-gold)!important;stroke:var(--rv-gold)!important;
}

/* HUD AMBIENTE */
[data-testid="stAppViewContainer"]:after{
  content:"";position:fixed;left:0;right:0;bottom:-7vh;height:22vh;pointer-events:none;
  background:linear-gradient(rgba(0,174,239,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(0,174,239,.055) 1px,transparent 1px);
  background-size:52px 28px;transform:perspective(380px) rotateX(62deg);transform-origin:bottom;opacity:.38;z-index:0;
}

.renova-ai-fab{
  position:fixed;
  right:24px;
  bottom:24px;
  z-index:9999;
  display:flex;
  align-items:center;
  gap:10px;
  padding:13px 17px;
  border-radius:999px;
  border:1px solid rgba(255,215,90,.78);
  background:linear-gradient(135deg,#071C2D,#0A2A48 58%,#03101A);
  color:#FFE477!important;
  text-decoration:none!important;
  font-weight:950;
  font-size:.86rem;
  letter-spacing:.01em;
  box-shadow:0 16px 38px rgba(0,0,0,.42),0 0 24px rgba(0,174,239,.20),0 0 16px rgba(255,215,90,.12);
  backdrop-filter:blur(14px);
  transition:.2s ease;
}
.renova-ai-fab:hover{
  transform:translateY(-3px) scale(1.015);
  border-color:#FFF0A3;
  box-shadow:0 20px 44px rgba(0,0,0,.48),0 0 30px rgba(0,174,239,.28),0 0 19px rgba(255,215,90,.20);
}
.renova-ai-fab .icon{
  width:34px;height:34px;border-radius:50%;
  display:grid;place-items:center;
  background:linear-gradient(135deg,#00AEEF,#0077FF);
  color:#fff!important;
  font-size:1.05rem;
  box-shadow:0 0 18px rgba(0,174,239,.34);
}
.renova-ai-fab .copy{display:flex;flex-direction:column;line-height:1.05}
.renova-ai-fab .copy small{
  color:#8EDFFF!important;font-size:.58rem;font-weight:900;letter-spacing:.08em;margin-bottom:4px
}
.renova-ai-fab .copy strong{color:#FFE477!important;font-size:.84rem}

@media(max-width:768px){
  .stApp{background-size:32px 32px,32px 32px,auto,auto,auto,auto!important}
  [data-testid="stMainBlockContainer"]{padding:1rem 1rem 4.5rem!important}
  .renova-hero{padding:24px 18px 20px;border-radius:18px}
  .renova-hero:before{font-size:.54rem;letter-spacing:.11em}
  .renova-hero h1{font-size:1.78rem!important}
  .renova-hero p{font-size:.9rem!important}
  .metric-card{min-height:108px;padding:15px}
  .metric-card .value{font-size:1.38rem}
  [data-testid="stAppViewContainer"]:after{opacity:.14;height:13vh}
  [data-baseweb="tab-list"]{overflow-x:auto!important;flex-wrap:nowrap!important}
  [data-baseweb="tab"]{min-width:max-content!important;padding:0 12px!important}
  .renova-ai-fab{
    right:14px;
    bottom:78px;
    padding:10px 12px;
    gap:8px;
    max-width:calc(100vw - 28px);
  }
  .renova-ai-fab .icon{width:31px;height:31px;font-size:.95rem}
  .renova-ai-fab .copy small{font-size:.52rem}
  .renova-ai-fab .copy strong{font-size:.76rem}
}

@media(prefers-reduced-motion:reduce){
  *{animation:none!important;scroll-behavior:auto!important;transition:none!important}
}
</style>
        """,
        unsafe_allow_html=True,
    )


def brand_block() -> None:
    st.markdown(
        f"""
        <div class="renova-brand">
          <img src="{RENOVA_LOGO_URL}" alt="Logo Ecossistema RENOVA" />
          <div class="kicker">ECOSSISTEMA RENOVA</div>
          <h2>RENOVA <span class="gold">Finanças</span></h2>
          <p>Gestão inteligente • Clareza • Decisão</p>
          <div class="status-line">
            <span class="status-chip">FINANCEIRO 360°</span>
            <span class="status-chip gold">IA READY</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def floating_ai_button() -> None:
    st.markdown(
        """
        <a class="renova-ai-fab" href="?assistant=1" target="_self" aria-label="Abrir Assistente Financeiro IA">
          <span class="icon">🤖</span>
          <span class="copy">
            <small>RENOVA IA</small>
            <strong>Assistente Financeiro IA</strong>
          </span>
        </a>
        """,
        unsafe_allow_html=True,
    )



def auto_collapse_sidebar() -> None:
    """Collapse the Streamlit sidebar after a navigation choice."""
    components.html(
        """
        <script>
        (function () {
          const doc = window.parent.document;
          const isMobile = window.parent.innerWidth <= 900;

          function collapse() {
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return;

            const visible = sidebar.getBoundingClientRect().width > 40;
            if (!visible) return;

            const candidates = [
              '[data-testid="stSidebarCollapseButton"] button',
              '[data-testid="stSidebarCollapseButton"]',
              'button[kind="header"]'
            ];

            for (const selector of candidates) {
              const button = doc.querySelector(selector);
              if (button) {
                button.click();
                return;
              }
            }
          }

          // Mobile: always close after navigation. Desktop: also close when
          // explicitly triggered, keeping the interface focused on content.
          setTimeout(collapse, isMobile ? 120 : 180);
          setTimeout(collapse, isMobile ? 420 : 520);
        })();
        </script>
        """,
        height=0,
        width=0,
    )
