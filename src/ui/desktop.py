from __future__ import annotations

from typing import Any

import streamlit as st


_DESKTOP_CSS = r"""
/* RENOVA Finanças — camada exclusiva DESKTOP */
[data-testid="stMainBlockContainer"]{max-width:1480px!important;margin:0 auto!important}
.st-key-renova_ai_fab{right:24px!important;bottom:24px!important}
.st-key-launch_actions{max-width:430px!important}
[data-testid="stSidebar"]{min-width:290px!important}
[data-testid="stSidebar"]>div:first-child{padding-left:10px!important;padding-right:10px!important}
"""


def apply_desktop_styles() -> None:
    st.markdown(f"<style>{_DESKTOP_CSS}</style>", unsafe_allow_html=True)


def tune_plotly_desktop(fig: Any) -> Any:
    try:
        title = str(getattr(getattr(fig.layout, "xaxis", None).title, "text", "") or "").lower()
        if "data" in title or "date" in title:
            fig.update_xaxes(tickformat="%d/%m/%Y", nticks=9, tickangle=0, automargin=True)
    except Exception:
        pass
    return fig
