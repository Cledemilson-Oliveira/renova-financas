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
    """Evita sobreposição de ações e padroniza os modais do sistema."""
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

        /* ================================================================
           RENOVA IA • CHAT EM ESTILO WHATSAPP COM ALTO CONTRASTE
           Aplica somente em dialogs que realmente possuem st.chat_input.
           ================================================================ */
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) > div{
          width:min(780px,94vw)!important;
          max-width:780px!important;
          max-height:90vh!important;
          overflow:hidden!important;
          border:1px solid rgba(53,208,127,.52)!important;
          border-radius:22px!important;
          background:
            radial-gradient(circle at 14% 16%,rgba(0,174,239,.08),transparent 28%),
            linear-gradient(145deg,#08141B 0%,#0B141A 48%,#061018 100%)!important;
          box-shadow:0 30px 90px rgba(0,0,0,.70),0 0 34px rgba(53,208,127,.10),0 0 28px rgba(0,174,239,.10)!important;
        }

        /* Cabeçalho de conversa: usa o título nativo do dialog como contato. */
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) h2{
          position:relative!important;
          margin:0!important;
          padding:8px 10px 11px 54px!important;
          color:#FFFFFF!important;
          font-size:1.02rem!important;
          font-weight:950!important;
          line-height:1.15!important;
        }
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) h2::before{
          content:"🤖";
          position:absolute;
          left:7px;top:50%;transform:translateY(-50%);
          width:37px;height:37px;border-radius:50%;
          display:flex;align-items:center;justify-content:center;
          background:linear-gradient(145deg,#073454,#0A2435)!important;
          border:2px solid #35D07F!important;
          box-shadow:0 0 18px rgba(53,208,127,.22),0 0 14px rgba(0,174,239,.16)!important;
          font-size:1.05rem!important;
        }
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) h2::after{
          content:"● online • Assistente Financeiro RENOVA";
          display:block;
          margin-top:4px;
          color:#72E4A5!important;
          font-size:.64rem!important;
          font-weight:800!important;
          letter-spacing:.02em!important;
        }

        /* Fundo da área de conversa, inspirado no WhatsApp dark. */
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stVerticalBlock"]{
          background-image:
            radial-gradient(circle at 18px 18px,rgba(255,255,255,.018) 2px,transparent 2px),
            radial-gradient(circle at 46px 44px,rgba(53,208,127,.022) 2px,transparent 2px)!important;
          background-size:64px 64px!important;
        }

        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"]{
          width:fit-content!important;
          max-width:84%!important;
          min-width:120px!important;
          margin:8px 0!important;
          padding:11px 13px!important;
          border-radius:17px!important;
          background:#102432!important;
          border:1px solid rgba(0,174,239,.34)!important;
          box-shadow:0 8px 20px rgba(0,0,0,.25)!important;
        }

        /* Mensagem do usuário: lado direito e verde WhatsApp. */
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"]:has([data-testid*="user" i]),
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"]:has([aria-label*="user" i]),
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"]:has([aria-label*="usuário" i]){
          margin-left:auto!important;
          margin-right:2px!important;
          border-radius:17px 17px 4px 17px!important;
          background:linear-gradient(145deg,#075E54,#005C4B)!important;
          border-color:rgba(53,208,127,.65)!important;
          box-shadow:0 8px 20px rgba(0,0,0,.28),0 0 12px rgba(53,208,127,.06)!important;
        }

        /* Mensagem da IA: lado esquerdo e azul RENOVA. */
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"]:has([data-testid*="assistant" i]),
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"]:has([aria-label*="assistant" i]),
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"]:has([aria-label*="assistente" i]){
          margin-left:2px!important;
          margin-right:auto!important;
          border-radius:17px 17px 17px 4px!important;
          background:linear-gradient(145deg,#0A2638,#0B1F2D)!important;
          border-color:rgba(0,174,239,.52)!important;
        }

        /* Texto sempre legível, inclusive markdown e links. */
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"] p,
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"] li,
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"] span,
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"] strong{
          color:#F7FBFF!important;
          -webkit-text-fill-color:#F7FBFF!important;
          line-height:1.5!important;
        }
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"] a{
          color:#9FE7FF!important;
          text-decoration:underline!important;
          font-weight:850!important;
        }

        /* Avatar compacto para não roubar espaço dos balões. */
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"] [data-testid*="Avatar"],
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"] [data-testid*="avatar"]{
          filter:drop-shadow(0 0 8px rgba(0,174,239,.20))!important;
        }

        /* Alertas dentro da conversa ficam claros e sem baixo contraste. */
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stAlert"]{
          background:#12252D!important;
          border:1px solid rgba(255,215,90,.42)!important;
          color:#FFFFFF!important;
        }
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stAlert"] *{
          color:#F7FBFF!important;
          -webkit-text-fill-color:#F7FBFF!important;
        }

        /* Campo de envio estilo WhatsApp, grande e visível. */
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatInput"]{
          position:sticky!important;
          bottom:0!important;
          z-index:30!important;
          margin-top:10px!important;
          padding:8px!important;
          border:1px solid rgba(53,208,127,.34)!important;
          border-radius:17px!important;
          background:#071117!important;
          box-shadow:0 -8px 26px rgba(0,0,0,.25)!important;
        }
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatInput"] textarea{
          min-height:48px!important;
          color:#FFFFFF!important;
          -webkit-text-fill-color:#FFFFFF!important;
          caret-color:#35D07F!important;
          background:#17252D!important;
          border:1px solid rgba(255,255,255,.13)!important;
          border-radius:14px!important;
          font-size:.94rem!important;
          font-weight:650!important;
        }
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatInput"] textarea::placeholder{
          color:#B8C9D3!important;
          -webkit-text-fill-color:#B8C9D3!important;
          opacity:1!important;
        }
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatInput"] button{
          min-width:44px!important;
          min-height:44px!important;
          border-radius:50%!important;
          background:linear-gradient(145deg,#35D07F,#1D9B62)!important;
          border:1px solid #7BE6AB!important;
          color:#04110B!important;
          box-shadow:0 0 16px rgba(53,208,127,.18)!important;
        }
        [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatInput"] button svg{
          color:#04110B!important;
          fill:#04110B!important;
          stroke:#04110B!important;
        }

        /* Conteúdo extra usado pelo modal global nas páginas separadas. */
        .renova-ai-chat-status{
          display:flex;align-items:center;gap:8px;
          margin:0 0 10px;padding:8px 11px;border-radius:12px;
          background:rgba(53,208,127,.075);
          border:1px solid rgba(53,208,127,.22);
          color:#C9FFE0!important;font-size:.72rem;font-weight:850;
        }
        .renova-ai-chat-status .dot{
          width:8px;height:8px;border-radius:50%;background:#35D07F;
          box-shadow:0 0 10px rgba(53,208,127,.75);
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

          [data-testid="stDialog"]:has([data-testid="stChatInput"]) > div{
            width:calc(100vw - 12px)!important;
            max-width:none!important;
            height:calc(100vh - 18px)!important;
            max-height:calc(100vh - 18px)!important;
            border-radius:18px!important;
          }
          [data-testid="stDialog"]:has([data-testid="stChatInput"]) h2{
            padding-left:50px!important;
            font-size:.94rem!important;
          }
          [data-testid="stDialog"]:has([data-testid="stChatInput"]) h2::after{
            font-size:.58rem!important;
          }
          [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"]{
            max-width:90%!important;
            padding:10px 11px!important;
          }
          [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"] p,
          [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatMessage"] li{
            font-size:.91rem!important;
          }
          [data-testid="stDialog"]:has([data-testid="stChatInput"]) [data-testid="stChatInput"] textarea{
            font-size:16px!important;
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
