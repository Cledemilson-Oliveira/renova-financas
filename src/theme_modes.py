from __future__ import annotations

from typing import Any

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

from src.supabase_client import current_user, get_supabase


THEME_OPTIONS = {
    "Automático": "system",
    "Claro": "light",
    "Escuro": "dark",
}
THEME_LABELS = {value: label for label, value in THEME_OPTIONS.items()}
_VALID_MODES = set(THEME_LABELS)


def current_theme_mode() -> str:
    override = str(st.session_state.get("renova_theme_mode") or "").strip().lower()
    if override in _VALID_MODES:
        return override

    user = current_user()
    metadata = (getattr(user, "user_metadata", {}) or {}) if user else {}
    stored = str(metadata.get("theme_mode") or "system").strip().lower()
    mode = stored if stored in _VALID_MODES else "system"
    st.session_state.renova_theme_mode = mode
    return mode


def save_theme_mode(mode: str) -> None:
    mode = str(mode or "system").strip().lower()
    if mode not in _VALID_MODES:
        raise ValueError("Modo de aparência inválido.")

    st.session_state.renova_theme_mode = mode
    user = current_user()
    if not user:
        return

    client = get_supabase()
    if client is None:
        return

    metadata = dict(getattr(user, "user_metadata", {}) or {})
    metadata["theme_mode"] = mode
    response = client.auth.update_user({"data": metadata})
    if getattr(response, "user", None) is not None:
        st.session_state.auth_user = response.user


def _light_plotly_template() -> go.layout.Template:
    return go.layout.Template(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#17364A", "family": "Inter, Arial, sans-serif"},
            colorway=["#0077B6", "#C89200", "#168A55", "#D8434F", "#5967D9", "#009EC3", "#D8791B"],
            xaxis={
                "gridcolor": "rgba(0,119,182,.10)",
                "linecolor": "rgba(13,73,101,.16)",
                "zerolinecolor": "rgba(13,73,101,.10)",
                "tickfont": {"color": "#5A7180"},
                "title": {"font": {"color": "#445E6E"}},
            },
            yaxis={
                "gridcolor": "rgba(0,119,182,.10)",
                "linecolor": "rgba(13,73,101,.16)",
                "zerolinecolor": "rgba(13,73,101,.10)",
                "tickfont": {"color": "#5A7180"},
                "title": {"font": {"color": "#445E6E"}},
            },
            legend={"font": {"color": "#536A79"}, "bgcolor": "rgba(255,255,255,.72)"},
            hoverlabel={"bgcolor": "#FFFFFF", "bordercolor": "#C89200", "font": {"color": "#17364A"}},
        )
    )


def _light_css_body() -> str:
    return r"""
:root{
  --rv-bg:#F3F7FA;
  --rv-bg2:#EAF2F7;
  --rv-panel:#FFFFFF;
  --rv-panel2:#F6FAFC;
  --rv-blue:#007FB8;
  --rv-blue2:#0067B1;
  --rv-gold:#B88400;
  --rv-gold2:#8A6500;
  --rv-text:#102D3E;
  --rv-muted:#597181;
  --rv-green:#168A55;
  --rv-red:#D8434F;
}
html,body,.stApp{background:#F3F7FA!important;color:var(--rv-text)!important}
.stApp{
  background-image:
    linear-gradient(rgba(0,127,184,.045) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,127,184,.045) 1px,transparent 1px),
    radial-gradient(circle at 48% -10%,rgba(0,174,239,.13),transparent 38%),
    radial-gradient(circle at 94% 18%,rgba(255,215,90,.18),transparent 27%),
    linear-gradient(135deg,#F8FBFD 0%,#EEF5F9 52%,#F7FAFC 100%)!important;
}
[data-testid="stHeader"]{background:rgba(248,251,253,.88)!important;border-bottom:1px solid rgba(0,127,184,.12)!important}
[data-testid="stSidebar"]>div:first-child{
  background:linear-gradient(180deg,rgba(251,253,254,.98),rgba(236,245,250,.98))!important;
  border-right:1px solid rgba(0,127,184,.16)!important;
  box-shadow:12px 0 38px rgba(31,67,86,.10)!important;
}
h1,h2,h3,h4{color:#102D3E!important}
p,label,.stCaption{color:#597181!important}
.renova-brand{
  border-color:rgba(0,127,184,.22)!important;
  background:radial-gradient(circle at 50% 0%,rgba(0,174,239,.13),transparent 48%),linear-gradient(145deg,#FFFFFF,#EAF4F9)!important;
  box-shadow:0 14px 32px rgba(31,67,86,.10),inset 0 1px rgba(255,255,255,.90)!important;
}
.renova-brand h2{color:#153448!important}.renova-brand p{color:#617989!important}.renova-brand .kicker{color:#0079AD!important}
.renova-brand .status-chip{color:#006E9D!important;background:rgba(0,127,184,.07)!important;border-color:rgba(0,127,184,.18)!important}
.renova-brand .status-chip.gold{color:#8A6500!important;background:rgba(184,132,0,.08)!important;border-color:rgba(184,132,0,.20)!important}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]{
  border-color:rgba(0,127,184,.16)!important;
  background:linear-gradient(135deg,#FFFFFF,#F1F7FA)!important;
  box-shadow:0 7px 18px rgba(31,67,86,.08)!important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover{
  border-color:rgba(0,127,184,.48)!important;
  background:linear-gradient(135deg,#FFFFFF,#E7F4FA)!important;
  box-shadow:0 10px 24px rgba(31,67,86,.12)!important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label p{color:#294A5C!important}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]>div:first-child{background:#F7FBFD!important;border-color:#008FCB!important;box-shadow:none!important}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked){
  border-color:rgba(184,132,0,.55)!important;
  background:linear-gradient(120deg,#FFF8DD,#EAF7FC)!important;
  box-shadow:0 9px 24px rgba(31,67,86,.11),inset 0 0 18px rgba(255,215,90,.10)!important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) p{color:#745600!important}
.renova-hero{
  border-color:rgba(184,132,0,.26)!important;
  background:linear-gradient(rgba(0,127,184,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(0,127,184,.035) 1px,transparent 1px),radial-gradient(circle at 88% 12%,rgba(0,174,239,.13),transparent 28%),radial-gradient(circle at 7% 115%,rgba(255,215,90,.24),transparent 34%),linear-gradient(125deg,#FFFFFF 0%,#EDF7FB 46%,#F8FBFD 100%)!important;
  box-shadow:0 18px 42px rgba(31,67,86,.11),0 0 26px rgba(0,127,184,.04),inset 0 1px rgba(255,255,255,.88)!important;
}
.renova-hero h1{color:#102D3E!important}.renova-hero p{color:#587181!important}.renova-hero strong{color:#9C7200!important;text-shadow:none!important}
.metric-card,div[data-testid="stMetric"],[data-testid="stExpander"]{
  border-color:rgba(0,127,184,.15)!important;
  background:radial-gradient(circle at 92% 8%,rgba(0,174,239,.07),transparent 27%),linear-gradient(145deg,#FFFFFF,#F7FAFC)!important;
  box-shadow:0 12px 28px rgba(31,67,86,.09),inset 0 1px rgba(255,255,255,.95)!important;
}
.metric-card:hover,div[data-testid="stMetric"]:hover,[data-testid="stExpander"]:hover{box-shadow:0 16px 34px rgba(31,67,86,.13)!important}
.metric-card .label,div[data-testid="stMetric"] label{color:#607786!important}.metric-card .value,div[data-testid="stMetric"] [data-testid="stMetricValue"]{color:#102D3E!important}.metric-card .hint{color:#8A6500!important}
[data-baseweb="input"]>div,[data-baseweb="textarea"]>div,[data-baseweb="select"]>div,div[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{
  background:#FFFFFF!important;color:#17364A!important;-webkit-text-fill-color:#17364A!important;
  border-color:rgba(0,127,184,.18)!important;
}
[data-testid="stForm"]{background:linear-gradient(145deg,#FFFFFF,#F4F9FB)!important;border-color:rgba(0,127,184,.14)!important}
[data-baseweb="tab-list"]{background:linear-gradient(145deg,#FFFFFF,#EFF6F9)!important;border-color:rgba(0,127,184,.14)!important}
[data-baseweb="tab"]{background:rgba(247,250,252,.92)!important;color:#587181!important}
[data-baseweb="tab"][aria-selected="true"]{color:#745600!important;background:linear-gradient(135deg,rgba(255,215,90,.18),rgba(0,174,239,.08))!important}
[data-testid="stPlotlyChart"],[data-testid="stDataFrame"]{
  border-color:rgba(0,127,184,.13)!important;
  background:linear-gradient(145deg,#FFFFFF,#F7FAFC)!important;
  box-shadow:0 10px 26px rgba(31,67,86,.08)!important;
}
[data-testid="stPlotlyChart"] .main-svg text{fill:#294A5C!important}
[data-testid="stPlotlyChart"] .main-svg{background:transparent!important}
[data-testid="stAlert"]{background:linear-gradient(135deg,#FFFFFF,#F3F8FA)!important;color:#17364A!important;border-color:rgba(0,127,184,.16)!important}
[data-testid="stAlert"] p,[data-testid="stAlert"] div{color:#294A5C!important}
.sales-hero{background:radial-gradient(circle at 50% 0%,rgba(0,174,239,.13),transparent 42%),linear-gradient(135deg,#FFFFFF,#ECF6FA 52%,#F8FBFD)!important;box-shadow:0 24px 58px rgba(31,67,86,.12)!important}
.sales-badge,.sales-eyebrow{color:#8A6500!important}.sales-hero h1 strong,.sales-section h2 strong,.ai-sales h2 strong,.pricing-section h2 strong,.sales-final h2 strong{color:#9C7200!important}
.sales-card,.price-card{background:linear-gradient(145deg,#FFFFFF,#F5F9FB)!important;border-color:rgba(0,127,184,.14)!important;box-shadow:0 12px 28px rgba(31,67,86,.08)!important}
.ai-sales{background:radial-gradient(circle at 90% 0%,rgba(0,174,239,.10),transparent 34%),#F7FBFD!important;border-color:rgba(0,127,184,.17)!important}
.ai-demo{background:#EDF5F8!important;border-color:rgba(184,132,0,.18)!important}.bubble.user{background:#D9EFF8!important;color:#17364A!important}.bubble.bot{background:#FFF7D8!important;color:#745600!important}
.plan{color:#0079AD!important}.price{color:#102D3E!important}.price small{color:#607786!important}.price-card ul{color:#445E6E!important}
.sales-cta.secondary{background:#E7F2F7!important;color:#17364A!important;border-color:rgba(0,127,184,.28)!important}
.sidebar-profile-card{background:linear-gradient(145deg,#FFFFFF,#ECF6FA)!important;border-color:rgba(0,127,184,.17)!important;box-shadow:0 10px 26px rgba(31,67,86,.09)!important}
.sidebar-profile-name{color:#17364A!important}.sidebar-profile-email{color:#607786!important}.sidebar-profile-chip{color:#006E9D!important;background:rgba(0,127,184,.07)!important}.sidebar-profile-chip.gold{color:#8A6500!important;background:rgba(184,132,0,.08)!important}
.st-key-launch_actions{background:linear-gradient(145deg,rgba(255,255,255,.97),rgba(239,247,250,.98))!important;border-color:rgba(184,132,0,.22)!important;box-shadow:0 16px 36px rgba(31,67,86,.12)!important}
[data-testid="stDialog"]>div{background:linear-gradient(145deg,#FFFFFF,#F3F8FA)!important;border-color:rgba(184,132,0,.24)!important;box-shadow:0 24px 64px rgba(31,67,86,.18)!important}
[data-testid="stDialog"] [data-testid="stChatMessage"]{background:rgba(239,247,250,.88)!important;border-color:rgba(0,127,184,.11)!important}
[data-testid="stDialog"] [data-testid="stChatMessage"] p{color:#294A5C!important}
[data-testid="stChatInput"] textarea{background:#FFFFFF!important;color:#17364A!important;-webkit-text-fill-color:#17364A!important}
[data-testid="stSidebarCollapseButton"] button,[data-testid="stSidebarCollapsedControl"] button,[data-testid="collapsedControl"] button{
  background:linear-gradient(145deg,#FFFFFF,#EAF4F9)!important;color:#8A6500!important;border-color:rgba(184,132,0,.40)!important;box-shadow:0 7px 18px rgba(31,67,86,.10)!important;
}
[data-testid="stSidebarCollapseButton"] svg,[data-testid="stSidebarCollapsedControl"] svg,[data-testid="collapsedControl"] svg{color:#8A6500!important;fill:#8A6500!important;stroke:#8A6500!important}
[data-testid="stAppViewContainer"]:after{opacity:.12!important}
"""


def _inject_css(mode: str) -> None:
    light = _light_css_body()
    if mode == "light":
        css = f"<style>html{{color-scheme:light}}{light}</style>"
    elif mode == "dark":
        css = "<style>html{color-scheme:dark}</style>"
    else:
        css = f"<style>html{{color-scheme:light dark}}@media (prefers-color-scheme: light){{{light}}}</style>"
    st.markdown(css, unsafe_allow_html=True)


def apply_display_mode() -> None:
    mode = current_theme_mode()
    pio.templates["renova_financas_light"] = _light_plotly_template()
    if mode == "light":
        pio.templates.default = "renova_financas_light"
    else:
        pio.templates.default = "renova_financas"
    _inject_css(mode)


def render_appearance_selector() -> None:
    user = current_user()
    if not user:
        return

    mode = current_theme_mode()
    labels = list(THEME_OPTIONS.keys())
    current_label = THEME_LABELS.get(mode, "Automático")

    st.caption("APARÊNCIA")
    selected = st.selectbox(
        "Tema da interface",
        labels,
        index=labels.index(current_label),
        key="renova_theme_selector",
        label_visibility="collapsed",
        help="Automático acompanha o tema claro/escuro do seu dispositivo.",
    )
    selected_mode = THEME_OPTIONS[selected]
    if selected_mode != mode:
        try:
            save_theme_mode(selected_mode)
            st.toast(f"Aparência alterada para {selected.lower()}.", icon="🎨")
            st.rerun()
        except Exception:
            st.session_state.renova_theme_mode = mode
            st.error("Não foi possível salvar sua preferência de aparência agora.")
