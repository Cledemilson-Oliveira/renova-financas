from __future__ import annotations

from functools import wraps
from typing import Any

import streamlit as st


_INSTALLED = False
_ORIGINAL_MARKDOWN = None


def _should_render_as_html(body: Any, unsafe_allow_html: bool) -> bool:
    """Usa o renderer HTML nativo para blocos estruturados de página.

    O parser Markdown pode transformar HTML aninhado, separado por linhas em
    branco, em blocos de código. As páginas comerciais RENOVA usam HTML/CSS
    estruturado e devem ser renderizadas pelo renderer HTML do Streamlit.
    """
    if not unsafe_allow_html or not isinstance(body, str):
        return False

    markers = (
        "renova-sales-wrap",
        "renova-sales-hero",
        "renova-action-panel",
    )
    return any(marker in body for marker in markers)


def install_html_runtime() -> None:
    """Evita que HTML das páginas comerciais apareça como código na interface."""
    global _INSTALLED, _ORIGINAL_MARKDOWN
    if _INSTALLED:
        return

    _ORIGINAL_MARKDOWN = st.markdown

    @wraps(_ORIGINAL_MARKDOWN)
    def routed_markdown(body: Any, *args: Any, **kwargs: Any) -> Any:
        unsafe_allow_html = bool(kwargs.get("unsafe_allow_html", False))
        if _should_render_as_html(body, unsafe_allow_html):
            return st.html(str(body))
        return _ORIGINAL_MARKDOWN(body, *args, **kwargs)

    st.markdown = routed_markdown
    _INSTALLED = True
