from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

RENOVA_LOGO_URL = (
    "https://nnjvxomaermffqnmwtzr.supabase.co/storage/v1/object/public/"
    "branding-renova/LOGO%20OFICIAL%20RENOVA.png"
)

COLORS = {
    "bg": "#02070D",
    "panel": "#06131F",
    "panel_2": "#081C2B",
    "blue": "#00AEEF",
    "blue_2": "#0077FF",
    "gold": "#FFD75A",
    "gold_2": "#D9A520",
    "green": "#35D07F",
    "red": "#FF5E6C",
    "white": "#F7FBFF",
    "muted": "#AFC3D2",
}

_DATE_COLUMNS = {
    "data",
    "vencimento",
    "due_date",
    "target_date",
    "purchase_date",
    "occurred_on",
    "next_due_date",
    "data do lançamento",
    "data de vencimento",
    "próxima cobrança",
    "proxima cobranca",
}


def _format_date_br(value: Any) -> Any:
    """Formata valores de data apenas para apresentação, preservando os dados reais."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass

    if isinstance(value, pd.Timestamp):
        return value.strftime("%d/%m/%Y")
    if isinstance(value, (datetime, date)):
        return value.strftime("%d/%m/%Y")
    return value


def _format_dataframe_dates(data: Any) -> Any:
    if not isinstance(data, pd.DataFrame):
        return data

    frame = data.copy()
    for column in frame.columns:
        normalized = str(column).strip().lower()
        if normalized in _DATE_COLUMNS:
            frame[column] = frame[column].map(_format_date_br)
    return frame


def _install_brazilian_date_ui() -> None:
    """Padroniza datas visíveis do RENOVA Finanças como DD/MM/AAAA.

    O patch atua somente na camada de apresentação. Datas continuam sendo
    armazenadas no Supabase no formato ISO, que é o formato correto para o banco.
    """
    if getattr(st, "_renova_br_dates_installed", False):
        return

    original_date_input = st.date_input
    original_dataframe = st.dataframe

    def date_input_br(*args: Any, **kwargs: Any):
        kwargs.setdefault("format", "DD/MM/YYYY")
        return original_date_input(*args, **kwargs)

    def dataframe_br(data: Any = None, *args: Any, **kwargs: Any):
        return original_dataframe(_format_dataframe_dates(data), *args, **kwargs)

    st.date_input = date_input_br  # type: ignore[assignment]
    st.dataframe = dataframe_br  # type: ignore[assignment]
    setattr(st, "_renova_br_dates_installed", True)


def _install_layout_safety_css() -> None:
    """Evita sobreposição de ações e deixa uma saída clara nos modais."""
    st.markdown(
        """
        <style>
        /* Ações de lançamento ficam no fluxo da página, nunca sobre os registros. */
        body .st-key-launch_actions{
          position:relative!important;
          left:auto!important;
          right:auto!important;
          top:auto!important;
          bottom:auto!important;
          width:100%!important;
          max-width:none!important;
          margin:0 0 16px!important;
          z-index:5!important;
        }

        /* Reserva espaço para o único botão realmente flutuante: RENOVA IA. */
        body [data-testid="stMainBlockContainer"]{
          padding-bottom:8.5rem!important;
        }

        /*
         * O botão nativo de fechar do st.dialog passa a ser uma ação explícita.
         * Assim o usuário sempre enxerga como voltar ao painel sem salvar.
         */
        [data-testid="stDialog"] button[aria-label="Close"],
        [data-testid="stDialog"] button[aria-label="Fechar"],
        [data-testid="stDialog"] button[kind="header"]{
          width:auto!important;
          min-width:188px!important;
          min-height:40px!important;
          padding:0 14px!important;
          border-radius:11px!important;
          border:1px solid rgba(0,174,239,.50)!important;
          background:linear-gradient(135deg,#071C2D,#0A2A48)!important;
          color:#EAF7FF!important;
          box-shadow:0 8px 22px rgba(0,0,0,.30),0 0 15px rgba(0,174,239,.12)!important;
          font-size:0!important;
        }
        [data-testid="stDialog"] button[aria-label="Close"] svg,
        [data-testid="stDialog"] button[aria-label="Fechar"] svg,
        [data-testid="stDialog"] button[kind="header"] svg{
          display:none!important;
        }
        [data-testid="stDialog"] button[aria-label="Close"]::after,
        [data-testid="stDialog"] button[aria-label="Fechar"]::after,
        [data-testid="stDialog"] button[kind="header"]::after{
          content:"← Voltar para o painel";
          color:#EAF7FF!important;
          font-size:.82rem!important;
          font-weight:900!important;
          letter-spacing:.01em!important;
          white-space:nowrap!important;
        }
        [data-testid="stDialog"] button[aria-label="Close"]:hover,
        [data-testid="stDialog"] button[aria-label="Fechar"]:hover,
        [data-testid="stDialog"] button[kind="header"]:hover{
          border-color:#FFD75A!important;
          background:linear-gradient(135deg,#0A2A48,#0B3A63)!important;
          box-shadow:0 10px 26px rgba(0,0,0,.36),0 0 18px rgba(255,215,90,.12)!important;
        }

        @media(max-width:768px){
          body .st-key-launch_actions{
            left:auto!important;
            right:auto!important;
            bottom:auto!important;
            width:100%!important;
            margin:0 0 14px!important;
          }
          body [data-testid="stMainBlockContainer"]{
            padding-bottom:10rem!important;
          }
          [data-testid="stDialog"] button[aria-label="Close"],
          [data-testid="stDialog"] button[aria-label="Fechar"],
          [data-testid="stDialog"] button[kind="header"]{
            min-width:154px!important;
            min-height:38px!important;
            padding:0 11px!important;
          }
          [data-testid="stDialog"] button[aria-label="Close"]::after,
          [data-testid="stDialog"] button[aria-label="Fechar"]::after,
          [data-testid="stDialog"] button[kind="header"]::after{
            font-size:.74rem!important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def configure_plotly() -> None:
    _install_brazilian_date_ui()
    _install_layout_safety_css()

    template = go.layout.Template(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": COLORS["white"], "family": "Inter, Arial, sans-serif"},
            colorway=[
                COLORS["blue"],
                COLORS["gold"],
                COLORS["green"],
                COLORS["red"],
                "#7B8CFF",
                "#19D3F3",
                "#FF9F40",
            ],
            xaxis={
                "gridcolor": "rgba(0,174,239,.10)",
                "linecolor": "rgba(255,215,90,.18)",
                "zerolinecolor": "rgba(255,255,255,.08)",
                "tickfont": {"color": COLORS["muted"]},
                "title": {"font": {"color": COLORS["muted"]}},
            },
            yaxis={
                "gridcolor": "rgba(0,174,239,.10)",
                "linecolor": "rgba(255,215,90,.18)",
                "zerolinecolor": "rgba(255,255,255,.08)",
                "tickfont": {"color": COLORS["muted"]},
                "title": {"font": {"color": COLORS["muted"]}},
            },
            legend={
                "font": {"color": COLORS["muted"]},
                "bgcolor": "rgba(2,7,13,.35)",
            },
            hoverlabel={
                "bgcolor": "#07131D",
                "bordercolor": COLORS["gold"],
                "font": {"color": COLORS["white"]},
            },
        )
    )
    pio.templates["renova_financas"] = template
    pio.templates.default = "renova_financas"
