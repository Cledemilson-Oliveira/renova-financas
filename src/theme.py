from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from src.visual_system import RENOVA_LOGO_URL, configure_plotly

PALETTE = {
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


def apply_renova_theme() -> None:
    configure_plotly()
    st.markdown(
        """
<style>
:root{
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

/* MENU MOBILE RENOVA: substitui completamente a sidebar em telas pequenas */
#renova-mobile-nav{display:none}
#renova-mobile-nav .rv-mobile-nav-inner{
  display:flex;align-items:center;gap:10px;
  padding:10px 12px;
  border:1px solid rgba(255,215,90,.42);
  border-radius:16px;
  background:linear-gradient(145deg,rgba(4,17,28,.98),rgba(2,8,14,.99));
  box-shadow:0 16px 40px rgba(0,0,0,.46),0 0 24px rgba(0,174,239,.13);
  backdrop-filter:blur(18px);
}
#renova-mobile-nav .rv-mobile-brand{
  flex:0 0 auto;color:#EAF7FF;font-size:.70rem;font-weight:950;line-height:1.05;letter-spacing:.02em;
}
#renova-mobile-nav .rv-mobile-brand span{display:block;color:#FFD75A;font-size:.62rem;margin-top:3px}
#renova-mobile-nav select{
  min-width:0;flex:1;height:46px;padding:0 36px 0 12px;
  border:1px solid rgba(0,174,239,.44);border-radius:12px;
  background:#06131F;color:#F7FBFF;font-weight:900;font-size:.88rem;
  box-shadow:inset 0 0 18px rgba(0,174,239,.04);outline:none;
}
#renova-mobile-nav select:focus{border-color:#FFD75A;box-shadow:0 0 0 2px rgba(255,215,90,.10)}

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

/* BOTÕES — RENOVA Dark V2 */
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

/* LANDING / PÁGINA DE VENDAS */
.sales-hero,.sales-section,.ai-sales,.pricing-section,.sales-final{max-width:1180px;margin:0 auto 26px}
.sales-hero{
  padding:64px 38px 52px;text-align:center;border:1px solid rgba(255,215,90,.32);border-radius:28px;
  background:radial-gradient(circle at 50% 0%,rgba(0,174,239,.22),transparent 42%),linear-gradient(135deg,#04131F,#061F35 52%,#02070D);
  box-shadow:0 28px 70px rgba(0,0,0,.42),0 0 36px rgba(0,174,239,.08)
}
.sales-badge,.sales-eyebrow{color:#FFE477;font-size:.67rem;font-weight:950;letter-spacing:.14em}
.sales-hero h1{font-size:clamp(2.2rem,6vw,4.6rem)!important;line-height:1.02!important;margin:18px 0!important}
.sales-hero h1 strong,.sales-section h2 strong,.ai-sales h2 strong,.pricing-section h2 strong,.sales-final h2 strong{color:#FFD75A!important}
.sales-lead{max-width:820px;margin:0 auto!important;font-size:1.08rem!important;line-height:1.7!important}
.sales-cta-row{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:28px 0 18px}
.sales-cta{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:0 20px;border-radius:12px;text-decoration:none!important;font-weight:950}
.sales-cta.primary{background:linear-gradient(110deg,#C99308,#FFD75A,#FFF0A3,#D8A716);color:#06111B!important;border:1px solid #FFE57B}
.sales-cta.secondary{background:#071C2D;color:#EAF7FF!important;border:1px solid rgba(0,174,239,.42)}
.sales-cta.full{width:100%;box-sizing:border-box;margin-top:16px}
.sales-cta.static{cursor:default}
.sales-proof{color:#9FC4D8;font-size:.78rem;font-weight:800}
.sales-section,.pricing-section,.sales-final{padding:42px 26px}
.sales-section h2,.ai-sales h2,.pricing-section h2,.sales-final h2{font-size:clamp(1.8rem,4vw,2.8rem)!important;margin:10px 0 24px!important}
.sales-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.sales-card,.price-card{
  border:1px solid rgba(0,174,239,.20);border-radius:20px;padding:22px;
  background:linear-gradient(145deg,rgba(7,24,38,.97),rgba(3,10,16,.99));box-shadow:0 14px 34px rgba(0,0,0,.28)
}
.sales-card span{font-size:1.6rem}.sales-card h3{font-size:1rem!important;margin:12px 0 7px}.sales-card p{font-size:.83rem!important;line-height:1.55}
.ai-sales{
  display:grid;grid-template-columns:1fr 1fr;gap:28px;align-items:center;padding:38px;
  border:1px solid rgba(0,174,239,.26);border-radius:25px;background:radial-gradient(circle at 90% 0%,rgba(0,174,239,.14),transparent 34%),#04111C
}
.ai-sales p{line-height:1.7}.ai-chip{display:inline-block;margin-top:10px;padding:8px 11px;border-radius:999px;background:rgba(0,174,239,.08);border:1px solid rgba(0,174,239,.25);color:#8EDFFF;font-size:.75rem;font-weight:900}
.ai-demo{padding:18px;border-radius:18px;background:#020A11;border:1px solid rgba(255,215,90,.20)}
.bubble{max-width:88%;padding:12px 14px;border-radius:15px;margin:9px 0;font-size:.82rem;line-height:1.5}
.bubble.user{margin-left:auto;background:#092C48;color:#EAF7FF}.bubble.bot{background:#101B20;color:#FFE477;border:1px solid rgba(255,215,90,.14)}
.pricing-section{text-align:center}.pricing-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;max-width:820px;margin:0 auto;text-align:left}
.price-card.featured{position:relative;border-color:rgba(255,215,90,.62);box-shadow:0 18px 45px rgba(0,0,0,.35),0 0 25px rgba(255,215,90,.08)}
.popular{position:absolute;right:15px;top:14px;color:#FFD75A;font-size:.58rem;font-weight:950;letter-spacing:.12em}
.plan{color:#8EDFFF;font-size:.68rem;font-weight:950;letter-spacing:.13em}.price{font-size:2.1rem;font-weight:950;color:#fff;margin:8px 0}.price small{font-size:.75rem;color:#AFC3D2}
.price-card ul{padding:0;list-style:none;color:#C7D8E3;line-height:2;font-size:.82rem}.pricing-note{font-size:.72rem!important;margin-top:18px!important}
.sales-final{text-align:center;border-top:1px solid rgba(0,174,239,.15)}
.auth-anchor{scroll-margin-top:30px}

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
  min-width:42px!important;min-height:42px!important;
  border-radius:12px!important;border:1px solid rgba(255,215,90,.76)!important;
  background:linear-gradient(145deg,#071C2D,#03101A)!important;color:var(--rv-gold)!important;
  box-shadow:0 8px 22px rgba(0,0,0,.35),0 0 18px rgba(0,174,239,.22)!important;
  opacity:1!important;visibility:visible!important;
}
[data-testid="stSidebarCollapseButton"] svg,[data-testid="stSidebarCollapsedControl"] svg,[data-testid="collapsedControl"] svg{
  color:var(--rv-gold)!important;fill:var(--rv-gold)!important;stroke:var(--rv-gold)!important;
  width:22px!important;height:22px!important;
}
@media(min-width:901px){
  [data-testid="stSidebarCollapseButton"],
  [data-testid="stSidebarCollapsedControl"],
  [data-testid="collapsedControl"]{
    visibility:visible!important;opacity:1!important;z-index:10002!important;
  }
}

/* HUD AMBIENTE */
[data-testid="stAppViewContainer"]:after{
  content:"";position:fixed;left:0;right:0;bottom:-7vh;height:22vh;pointer-events:none;
  background:linear-gradient(rgba(0,174,239,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(0,174,239,.055) 1px,transparent 1px);
  background-size:52px 28px;transform:perspective(380px) rotateX(62deg);transform-origin:bottom;opacity:.38;z-index:0;
}

.st-key-renova_ai_fab{
  position:fixed!important;
  right:24px!important;
  bottom:24px!important;
  z-index:9999!important;
  width:auto!important;
}
.st-key-renova_ai_fab [data-testid="stButton"]{width:auto!important}
.st-key-renova_ai_fab button{
  min-height:56px!important;
  padding:0 18px!important;
  border-radius:999px!important;
  border:1px solid rgba(255,215,90,.78)!important;
  background:linear-gradient(135deg,#071C2D,#0A2A48 58%,#03101A)!important;
  color:#FFE477!important;
  -webkit-text-fill-color:#FFE477!important;
  font-weight:950!important;
  font-size:.86rem!important;
  box-shadow:0 16px 38px rgba(0,0,0,.42),0 0 24px rgba(0,174,239,.20),0 0 16px rgba(255,215,90,.12)!important;
  backdrop-filter:blur(14px)!important;
}
.st-key-renova_ai_fab button:hover{
  transform:translateY(-3px) scale(1.015)!important;
  border-color:#FFF0A3!important;
  background:linear-gradient(135deg,#0A2A48,#0B3A63 58%,#04131F)!important;
  color:#FFE477!important;
  -webkit-text-fill-color:#FFE477!important;
  box-shadow:0 20px 44px rgba(0,0,0,.48),0 0 30px rgba(0,174,239,.28),0 0 19px rgba(255,215,90,.20)!important;
}
.st-key-renova_ai_fab button *{color:#FFE477!important;-webkit-text-fill-color:#FFE477!important}

@media(max-width:900px){
  /* Mobile usa menu suspenso próprio; sidebar e seus controles deixam de ocupar a tela. */
  [data-testid="stSidebar"],
  [data-testid="stSidebarCollapsedControl"],
  [data-testid="stSidebarCollapseButton"],
  [data-testid="collapsedControl"]{display:none!important}

  body.renova-mobile-menu-active #renova-mobile-nav{
    display:block!important;
    position:fixed!important;
    top:8px!important;left:8px!important;right:8px!important;
    z-index:10050!important;
  }
  body.renova-mobile-menu-active [data-testid="stMainBlockContainer"]{
    padding-top:6.15rem!important;
  }

  .sales-hero{padding:42px 18px 34px;border-radius:20px}
  .sales-hero h1{font-size:2.45rem!important}
  .sales-lead{font-size:.94rem!important}
  .sales-grid{grid-template-columns:1fr 1fr}
  .ai-sales{grid-template-columns:1fr;padding:24px 18px}
  .pricing-grid{grid-template-columns:1fr}
  .sales-section,.pricing-section,.sales-final{padding:30px 6px}

  .stApp{background-size:32px 32px,32px 32px,auto,auto,auto,auto!important}
  [data-testid="stMainBlockContainer"]{padding-left:1rem!important;padding-right:1rem!important;padding-bottom:4.5rem!important}
  .renova-hero{padding:24px 18px 20px;border-radius:18px}
  .renova-hero:before{font-size:.54rem;letter-spacing:.11em}
  .renova-hero h1{font-size:1.78rem!important}
  .renova-hero p{font-size:.9rem!important}
  .metric-card{min-height:108px;padding:15px}
  .metric-card .value{font-size:1.38rem}
  [data-testid="stAppViewContainer"]:after{opacity:.14;height:13vh}
  [data-baseweb="tab-list"]{overflow-x:auto!important;flex-wrap:nowrap!important}
  [data-baseweb="tab"]{min-width:max-content!important;padding:0 12px!important}
  .st-key-renova_ai_fab{
    right:14px!important;
    bottom:78px!important;
    max-width:calc(100vw - 28px)!important;
  }
  .st-key-renova_ai_fab button{
    min-height:50px!important;
    padding:0 14px!important;
    font-size:.78rem!important;
  }
}

@media(max-width:430px){
  #renova-mobile-nav .rv-mobile-brand{font-size:.62rem}
  #renova-mobile-nav .rv-mobile-brand span{font-size:.56rem}
  #renova-mobile-nav select{font-size:.80rem;padding-left:9px}
  #renova-mobile-nav .rv-mobile-nav-inner{gap:8px;padding:9px}
}

[data-testid="stDialog"]>div{
  border:1px solid rgba(255,215,90,.35)!important;
  background:linear-gradient(145deg,rgba(4,17,28,.99),rgba(2,8,14,.99))!important;
  box-shadow:0 28px 80px rgba(0,0,0,.55),0 0 35px rgba(0,174,239,.12)!important;
}
[data-testid="stDialog"] [data-testid="stChatMessage"]{
  border:1px solid rgba(0,174,239,.12);
  border-radius:14px;
  padding:8px 10px;
  background:rgba(6,19,31,.70);
}



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

/* ========================================================================
   MOBILE V3 • contraste leve + menu de módulos nativo sempre acessível
   ======================================================================== */
.st-key-renova_fin_mobile_nav{display:none!important}

@media(max-width:900px){
  /* A navegação mobile não depende mais da sidebar ou de injeção JavaScript. */
  #renova-mobile-nav{display:none!important}
  .st-key-renova_fin_mobile_nav{
    display:block!important;
    position:fixed!important;
    top:8px!important;left:10px!important;right:10px!important;
    z-index:10050!important;
    margin:0!important;
    filter:drop-shadow(0 10px 24px rgba(2,12,24,.32))!important;
  }
  .st-key-renova_fin_mobile_nav button{
    width:100%!important;min-height:52px!important;
    border-radius:15px!important;
    border:1px solid rgba(25,217,255,.58)!important;
    background:linear-gradient(135deg,#123A5D 0%,#0F3150 55%,#17365D 100%)!important;
    color:#F8FCFF!important;-webkit-text-fill-color:#F8FCFF!important;
    font-size:.88rem!important;font-weight:950!important;
    box-shadow:0 10px 24px rgba(0,0,0,.24),0 0 18px rgba(25,217,255,.11),inset 0 1px rgba(255,255,255,.08)!important;
  }
  .st-key-renova_fin_mobile_nav button *{
    color:#F8FCFF!important;-webkit-text-fill-color:#F8FCFF!important;font-weight:950!important;
  }
  [data-testid="stMainBlockContainer"]{
    padding-top:5.45rem!important;
  }

  /* Superfícies menos pesadas: azul intermediário, borda leve e sombra externa. */
  .metric-card,
  div[data-testid="stMetric"],
  [data-testid="stExpander"],
  [data-testid="stPlotlyChart"],
  [data-testid="stDataFrame"],
  [data-testid="stForm"]{
    border-color:rgba(64,207,255,.30)!important;
    background:
      radial-gradient(circle at 92% 7%,rgba(25,217,255,.10),transparent 29%),
      linear-gradient(145deg,rgba(18,52,82,.96),rgba(12,38,64,.95))!important;
    box-shadow:
      0 10px 24px rgba(1,13,27,.26),
      0 0 18px rgba(25,217,255,.075),
      inset 0 1px rgba(255,255,255,.055)!important;
  }
  .metric-card{min-height:102px!important;padding:15px 16px!important}
  .metric-card .label,div[data-testid="stMetric"] label{color:#C8DDEB!important}
  .metric-card .hint{color:#71E6FF!important}
  .metric-card .value,div[data-testid="stMetric"] [data-testid="stMetricValue"]{
    color:#FFFFFF!important;-webkit-text-fill-color:#FFFFFF!important;
    text-shadow:0 1px 16px rgba(25,217,255,.08)!important;
  }

  .renova-hero{
    border-color:rgba(64,207,255,.32)!important;
    background:
      linear-gradient(rgba(25,217,255,.026) 1px,transparent 1px),
      linear-gradient(90deg,rgba(25,217,255,.026) 1px,transparent 1px),
      radial-gradient(circle at 88% 12%,rgba(25,217,255,.13),transparent 30%),
      linear-gradient(135deg,#123A5D 0%,#0E2D4B 55%,#0B2540 100%)!important;
    box-shadow:0 12px 28px rgba(1,13,27,.28),0 0 18px rgba(25,217,255,.08)!important;
  }

  [data-baseweb="tab-list"]{
    background:linear-gradient(145deg,#123A5D,#0E2D4B)!important;
    border-color:rgba(64,207,255,.28)!important;
    box-shadow:0 8px 20px rgba(1,13,27,.20)!important;
  }

  [data-testid="stAlert"]{
    background:linear-gradient(135deg,rgba(18,52,82,.96),rgba(12,38,64,.96))!important;
    border-color:rgba(64,207,255,.28)!important;
    box-shadow:0 8px 20px rgba(1,13,27,.20),inset 3px 0 rgba(25,217,255,.22)!important;
  }
}

@media(prefers-reduced-motion:reduce){
  *{animation:none!important;scroll-behavior:auto!important;transition:none!important}
}
</style>
        """,
        unsafe_allow_html=True,
    )
    # O menu mobile é renderizado nativamente no app.py para maior estabilidade.


def install_mobile_navigation() -> None:
    """Install a resilient mobile dropdown that mirrors the sidebar navigation."""
    components.html(
        """
        <script>
        (function () {
          const win = window.parent;
          const doc = win.document;
          const ROOT_ID = 'renova-mobile-nav';
          const MOBILE_MAX = 900;
          const icons = {
            'Dashboard':'🏠',
            'Lançamentos':'💸',
            'Categorias':'🏷️',
            'Contas':'🏦',
            'Cartões':'💳',
            'Orçamentos':'🎯',
            'Análises':'📊',
            'Relatórios':'📄',
            'RENOVA IA':'🤖',
            'Treinamento IA':'🧠',
            'Assinar RENOVA IA':'⭐'
          };

          function isMobile() {
            return win.innerWidth <= MOBILE_MAX;
          }

          function items() {
            return Array.from(doc.querySelectorAll(
              '[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]'
            )).map(function (label) {
              const input = label.querySelector('input');
              const textNode = label.querySelector('p');
              const text = (textNode ? textNode.textContent : label.textContent || '').trim();
              return {label: label, input: input, text: text};
            }).filter(function (item) { return item.text; });
          }

          function removeMenu() {
            const old = doc.getElementById(ROOT_ID);
            if (old) old.remove();
            doc.body.classList.remove('renova-mobile-menu-active');
          }

          function mount() {
            if (!isMobile()) {
              removeMenu();
              return;
            }

            const navItems = items();
            if (!navItems.length) {
              removeMenu();
              return;
            }

            let root = doc.getElementById(ROOT_ID);
            if (!root) {
              root = doc.createElement('div');
              root.id = ROOT_ID;
              root.innerHTML = `
                <div class="rv-mobile-nav-inner">
                  <div class="rv-mobile-brand">RENOVA<span>FINANÇAS</span></div>
                  <select id="renova-mobile-nav-select" aria-label="Menu principal RENOVA Finanças"></select>
                </div>`;
              doc.body.appendChild(root);
            }

            const select = root.querySelector('#renova-mobile-nav-select');
            if (!select) return;

            const signature = navItems.map(function (item) { return item.text; }).join('|');
            if (select.dataset.signature !== signature) {
              select.innerHTML = '';
              navItems.forEach(function (item) {
                const option = doc.createElement('option');
                option.value = item.text;
                option.textContent = (icons[item.text] || '•') + '  ' + item.text;
                select.appendChild(option);
              });
              select.dataset.signature = signature;
            }

            const active = navItems.find(function (item) {
              return item.input && item.input.checked;
            });
            if (active && select.value !== active.text) {
              select.value = active.text;
            }

            if (select.dataset.bound !== '1') {
              select.addEventListener('change', function () {
                const target = items().find(function (item) {
                  return item.text === select.value;
                });
                if (target && target.label) {
                  target.label.click();
                }
              });
              select.dataset.bound = '1';
            }

            doc.body.classList.add('renova-mobile-menu-active');
          }

          if (win.__renovaMobileNavTimer) {
            win.clearInterval(win.__renovaMobileNavTimer);
          }
          if (win.__renovaMobileNavResizeHandler) {
            win.removeEventListener('resize', win.__renovaMobileNavResizeHandler);
          }

          win.__renovaMobileNavResizeHandler = mount;
          win.addEventListener('resize', win.__renovaMobileNavResizeHandler);

          mount();
          setTimeout(mount, 120);
          setTimeout(mount, 350);
          setTimeout(mount, 800);
          win.__renovaMobileNavTimer = win.setInterval(mount, 900);
          setTimeout(function () {
            if (win.__renovaMobileNavTimer) {
              win.clearInterval(win.__renovaMobileNavTimer);
              win.__renovaMobileNavTimer = null;
            }
          }, 12000);
        })();
        </script>
        """,
        height=0,
        width=0,
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


def floating_ai_button() -> bool:
    with st.container(key="renova_ai_fab"):
        return st.button(
            "🤖 Assistente Financeiro IA",
            key="open_renova_ai_dialog",
            help="Abrir o chat da RENOVA IA sem sair desta página",
        )


def auto_collapse_sidebar() -> None:
    """Collapse the desktop sidebar after a navigation choice when possible."""
    components.html(
        """
        <script>
        (function () {
          const doc = window.parent.document;
          const isMobile = window.parent.innerWidth <= 900;
          if (isMobile) return;

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

          setTimeout(collapse, 180);
          setTimeout(collapse, 520);
        })();
        </script>
        """,
        height=0,
        width=0,
    )
