from __future__ import annotations

from datetime import date, datetime
from html import escape
from typing import Any, Callable

import pandas as pd
import streamlit as st

from src.theme_modes import current_theme_mode


_BASE_CSS = r"""
/* RENOVA Finanças — camada exclusiva MOBILE */
[data-testid="stMainBlockContainer"]{
  padding:1rem .85rem 7rem!important;
  max-width:100%!important;
}
.renova-hero{padding:21px 16px 18px!important;border-radius:18px!important}
.renova-hero h1{font-size:1.68rem!important;line-height:1.08!important}
.renova-hero p{font-size:.88rem!important;line-height:1.5!important}
.metric-card{min-height:96px!important;padding:13px!important;border-radius:16px!important}
.metric-card .value{font-size:1.28rem!important}
[data-testid="stMetric"]{min-height:90px!important}

/* Ações de lançamento deixam de flutuar sobre o conteúdo no celular. */
html body .stApp .st-key-launch_actions{
  position:static!important;
  inset:auto!important;
  width:100%!important;
  margin:12px 0 18px!important;
  padding:8px!important;
  border-radius:17px!important;
  z-index:auto!important;
}
html body .stApp .st-key-launch_actions [data-testid="stHorizontalBlock"]{gap:7px!important}

/* Assistente vira botão compacto e não cobre formulário/tabela. */
html body .stApp .st-key-renova_ai_fab{
  right:12px!important;
  bottom:78px!important;
  width:54px!important;
  max-width:54px!important;
}
html body .stApp .st-key-renova_ai_fab [data-testid="stButton"]{width:54px!important}
html body .stApp .st-key-renova_ai_fab button{
  width:54px!important;
  min-width:54px!important;
  height:54px!important;
  min-height:54px!important;
  padding:0!important;
  border-radius:50%!important;
  font-size:0!important;
  overflow:hidden!important;
}
html body .stApp .st-key-renova_ai_fab button::after{
  content:"🤖";
  font-size:1.35rem!important;
  line-height:1!important;
}
html body .stApp .st-key-renova_ai_fab button p,
html body .stApp .st-key-renova_ai_fab button span{font-size:0!important}

/* Menu lateral: amplia o alvo real do Streamlit 1.63 e mantém legível. */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"]{
  position:fixed!important;
  top:10px!important;
  left:10px!important;
  z-index:100000!important;
}
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button,
button[aria-label*="open sidebar" i],
button[aria-label*="abrir barra lateral" i],
button[aria-label*="sidebar" i][data-testid="stBaseButton-headerNoPadding"]{
  min-width:86px!important;
  min-height:46px!important;
  padding:0 12px!important;
  border-radius:14px!important;
  border:2px solid #FFD75A!important;
  background:linear-gradient(135deg,#073454,#0A6B9A)!important;
  box-shadow:0 9px 24px rgba(0,0,0,.28),0 0 0 3px rgba(255,255,255,.78)!important;
  opacity:1!important;
}
[data-testid="stSidebarCollapsedControl"] button::after,
[data-testid="collapsedControl"] button::after,
button[aria-label*="open sidebar" i]::after,
button[aria-label*="abrir barra lateral" i]::after{
  content:"Menu";
  color:#FFFFFF!important;
  -webkit-text-fill-color:#FFFFFF!important;
  font-size:.76rem!important;
  font-weight:950!important;
  margin-left:5px!important;
}
[data-testid="stSidebarCollapseButton"] button,
button[aria-label*="close sidebar" i],
button[aria-label*="fechar barra lateral" i]{
  min-width:86px!important;
  min-height:44px!important;
  border-radius:14px!important;
  border:2px solid #FFD75A!important;
}
[data-testid="stSidebarCollapseButton"] button::after,
button[aria-label*="close sidebar" i]::after,
button[aria-label*="fechar barra lateral" i]::after{
  content:"Fechar";
  font-size:.74rem!important;
  font-weight:950!important;
  margin-left:5px!important;
}

/* Popovers, calendário e menus cabem na largura do aparelho. */
[data-baseweb="popover"]{max-width:calc(100vw - 20px)!important}
[data-baseweb="popover"]>div{max-width:calc(100vw - 20px)!important}
[data-baseweb="calendar"]{max-width:calc(100vw - 24px)!important;overflow:hidden!important}
[data-baseweb="calendar"] button{min-width:36px!important;min-height:36px!important}

/* Mais espaço para toque e leitura. */
.stApp input,.stApp textarea,.stApp [role="combobox"]{font-size:16px!important}
[data-baseweb="select"]>div,[data-baseweb="input"]>div,[data-baseweb="textarea"]>div{
  min-height:48px!important;
  border-radius:13px!important;
}
[data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button{
  min-height:48px!important;
  border-radius:14px!important;
}
[data-baseweb="tab-list"]{overflow-x:auto!important;flex-wrap:nowrap!important}
[data-baseweb="tab"]{min-width:max-content!important;padding:0 12px!important}

/* Gráficos mobile: remove toolbar que ocupa área útil. */
.modebar{display:none!important}
[data-testid="stPlotlyChart"]{border-radius:18px!important;overflow:hidden!important}

/* Cards de dados usados pelo runtime mobile. */
.renova-mobile-list{display:grid;gap:10px;margin:8px 0 16px}
.renova-mobile-row{
  border:1px solid rgba(0,174,239,.18);border-radius:16px;padding:13px 14px;
  background:linear-gradient(145deg,rgba(6,25,40,.96),rgba(2,10,17,.98));
  box-shadow:0 8px 22px rgba(0,0,0,.18);
}
.renova-mobile-row-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.renova-mobile-row-title{font-weight:950;font-size:.95rem;line-height:1.25;color:#F5FBFF}
.renova-mobile-row-value{font-weight:950;font-size:.95rem;color:#FFE477;white-space:nowrap}
.renova-mobile-row-meta{display:flex;flex-wrap:wrap;gap:6px;margin-top:9px}
.renova-mobile-pill{font-size:.68rem;font-weight:800;padding:5px 8px;border-radius:999px;background:rgba(0,174,239,.08);border:1px solid rgba(0,174,239,.18);color:#BDEEFF}
.renova-mobile-pill.gold{color:#FFE477;border-color:rgba(255,215,90,.22);background:rgba(255,215,90,.06)}
.renova-mobile-pill.alert{color:#FFBBC1;border-color:rgba(255,87,102,.28);background:rgba(255,87,102,.07)}
"""

_LIGHT_CSS = r"""
/* MOBILE CLARO */
html body .stApp .renova-mobile-row{
  background:linear-gradient(145deg,#FFFFFF,#F2F8FB)!important;
  border-color:rgba(0,127,184,.18)!important;
  box-shadow:0 8px 22px rgba(31,67,86,.10)!important;
}
html body .stApp .renova-mobile-row-title{color:#17364A!important}
html body .stApp .renova-mobile-row-value{color:#8A6500!important}
html body .stApp .renova-mobile-pill{color:#006E9D!important;background:rgba(0,127,184,.07)!important;border-color:rgba(0,127,184,.16)!important}
html body .stApp .renova-mobile-pill.gold{color:#745600!important;background:rgba(184,132,0,.08)!important;border-color:rgba(184,132,0,.20)!important}
html body .stApp .renova-mobile-pill.alert{color:#A02E3A!important;background:rgba(216,67,79,.07)!important;border-color:rgba(216,67,79,.20)!important}

/* BaseWeb completo em claro — inclusive multi-select e calendário. */
html body .stApp [data-baseweb="select"]>div,
html body .stApp [data-baseweb="input"]>div,
html body .stApp [data-baseweb="textarea"]>div,
html body .stApp [data-baseweb="select"] [role="combobox"],
html body .stApp [data-baseweb="select"] input,
html body .stApp input:not([type="checkbox"]):not([type="radio"]):not([type="file"]),
html body .stApp textarea{
  background:#FFFFFF!important;
  color:#17364A!important;
  -webkit-text-fill-color:#17364A!important;
}
html body .stApp [data-baseweb="select"] svg,
html body .stApp [data-baseweb="input"] svg{color:#17364A!important;fill:#17364A!important;stroke:#17364A!important}
html body .stApp [data-baseweb="tag"]{
  background:#FFD75A!important;color:#17364A!important;-webkit-text-fill-color:#17364A!important;border-radius:10px!important;
}
html body .stApp [data-baseweb="tag"] *{color:#17364A!important;-webkit-text-fill-color:#17364A!important}
html body [data-baseweb="popover"]>div,
html body [data-baseweb="calendar"],
html body [role="listbox"]{
  background:#FFFFFF!important;color:#17364A!important;
}
html body [data-baseweb="calendar"] *,html body [role="listbox"] *{color:#17364A!important;-webkit-text-fill-color:#17364A!important}
html body [data-baseweb="calendar"] [aria-selected="true"]{
  background:#FFD75A!important;color:#17364A!important;border-radius:10px!important;
}
"""

_DARK_CSS = r"""
/* MOBILE ESCURO */
html body .stApp [data-baseweb="select"]>div,
html body .stApp [data-baseweb="input"]>div,
html body .stApp [data-baseweb="textarea"]>div,
html body .stApp [data-baseweb="select"] [role="combobox"],
html body .stApp [data-baseweb="select"] input,
html body .stApp input:not([type="checkbox"]):not([type="radio"]):not([type="file"]),
html body .stApp textarea{
  background:#071A2B!important;color:#F7FBFF!important;-webkit-text-fill-color:#F7FBFF!important;
}
html body [data-baseweb="popover"]>div,
html body [data-baseweb="calendar"],
html body [role="listbox"]{background:#05131F!important;color:#F7FBFF!important}
html body [data-baseweb="calendar"] *,html body [role="listbox"] *{color:#F7FBFF!important;-webkit-text-fill-color:#F7FBFF!important}
html body [data-baseweb="calendar"] [aria-selected="true"]{background:#FFD75A!important;color:#102D3E!important;border-radius:10px!important}
"""


def apply_mobile_styles() -> None:
    mode = current_theme_mode()
    if mode == "light":
        css = f"<style>{_BASE_CSS}{_LIGHT_CSS}</style>"
    elif mode == "dark":
        css = f"<style>{_BASE_CSS}{_DARK_CSS}</style>"
    else:
        css = f"<style>{_BASE_CSS}{_DARK_CSS}@media (prefers-color-scheme:light){{{_LIGHT_CSS}}}</style>"
    st.markdown(css, unsafe_allow_html=True)


def _date_text(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if isinstance(value, pd.Timestamp):
        value = value.date()
    if isinstance(value, (date, datetime)):
        return value.strftime("%d/%m/%Y")
    text = str(value)
    try:
        return pd.to_datetime(text).strftime("%d/%m/%Y")
    except Exception:
        return text


def _money_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    try:
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(value)


def _transaction_cards(df: pd.DataFrame) -> None:
    cards: list[str] = []
    for _, row in df.iterrows():
        kind = str(row.get("tipo") or "")
        icon = "💰" if kind == "Receita" else "💸" if kind == "Despesa" else "🔄"
        description = escape(str(row.get("descricao") or "Lançamento"))
        value = escape(_money_text(row.get("valor")))
        when = _date_text(row.get("data"))
        due = _date_text(row.get("vencimento"))
        category = escape(str(row.get("categoria") or "Sem categoria"))
        account = escape(str(row.get("conta") or ""))
        status = escape(str(row.get("status") or ""))
        due_pill = f'<span class="renova-mobile-pill gold">📅 vence {escape(due)}</span>' if due else ""
        status_class = " alert" if status.lower() in {"atrasado", "previsto", "pendente"} else ""
        cards.append(
            f"""
            <article class="renova-mobile-row">
              <div class="renova-mobile-row-top">
                <div class="renova-mobile-row-title">{icon} {description}</div>
                <div class="renova-mobile-row-value">{value}</div>
              </div>
              <div class="renova-mobile-row-meta">
                <span class="renova-mobile-pill">📆 {escape(when)}</span>
                <span class="renova-mobile-pill">🏷️ {category}</span>
                {f'<span class="renova-mobile-pill">🏦 {account}</span>' if account else ''}
                {due_pill}
                {f'<span class="renova-mobile-pill{status_class}">{status}</span>' if status else ''}
              </div>
            </article>
            """
        )
    st.markdown('<div class="renova-mobile-list">' + "".join(cards) + "</div>", unsafe_allow_html=True)


def _account_cards(df: pd.DataFrame) -> None:
    cards: list[str] = []
    for _, row in df.iterrows():
        name = escape(str(row.get("conta") or "Conta"))
        value = escape(_money_text(row.get("saldo")))
        kind = escape(str(row.get("tipo") or ""))
        cards.append(
            f'<article class="renova-mobile-row"><div class="renova-mobile-row-top">'
            f'<div class="renova-mobile-row-title">🏦 {name}</div><div class="renova-mobile-row-value">{value}</div>'
            f'</div><div class="renova-mobile-row-meta"><span class="renova-mobile-pill">{kind}</span></div></article>'
        )
    st.markdown('<div class="renova-mobile-list">' + "".join(cards) + "</div>", unsafe_allow_html=True)


def render_dataframe_mobile(
    original: Callable[..., Any],
    data: Any,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Troca tabelas financeiras largas por cards somente no celular."""
    if not isinstance(data, pd.DataFrame) or data.empty:
        return original(data, *args, **kwargs)

    columns = set(map(str, data.columns))
    if {"descricao", "valor", "tipo"}.issubset(columns):
        _transaction_cards(data)
        return None
    if {"conta", "saldo"}.issubset(columns):
        _account_cards(data)
        return None
    return original(data, *args, **kwargs)


def tune_plotly_mobile(fig: Any) -> Any:
    """Adapta eixos/legendas para telas estreitas sem alterar os dados."""
    try:
        title = str(getattr(getattr(fig.layout, "xaxis", None).title, "text", "") or "").lower()
        if "data" in title or "date" in title:
            fig.update_xaxes(tickformat="%d/%m", nticks=4, tickangle=0, automargin=True)
        fig.update_layout(
            margin=dict(l=8, r=8, t=18, b=48),
            autosize=True,
            height=min(int(getattr(fig.layout, "height", None) or 340), 340),
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font=dict(size=10)),
        )
    except Exception:
        pass
    return fig


def mobile_plotly_config(existing: dict[str, Any] | None = None) -> dict[str, Any]:
    config = dict(existing or {})
    config.update({"displayModeBar": False, "responsive": True})
    return config
