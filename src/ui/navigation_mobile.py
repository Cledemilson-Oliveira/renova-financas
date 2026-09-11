from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import streamlit as st

from .navigation_desktop import NAV_ICONS, NAV_LABELS


_CONTROL_KEY = "_renova_mobile_nav_control"


def _sync_page_from_mobile_control() -> None:
    target = str(st.session_state.get(_CONTROL_KEY) or "")
    if target:
        st.session_state["nav_page"] = target
        st.session_state["_last_nav_page"] = target


def render_mobile_navigation(
    original_radio: Callable[..., Any],
    options: Sequence[str],
    current: str,
    *,
    label: str = "Navegação",
    label_visibility: str = "collapsed",
) -> str:
    """Navegação mobile independente do shell desktop.

    ``nav_page`` permanece um estado de aplicação e nunca é usado como chave de
    widget. Assim, botões do dashboard e da RENOVA IA podem trocar de módulo sem
    provocar conflito com widgets já instanciados.
    """
    available = list(options)
    if not available:
        return current

    if current not in available:
        current = available[0]
        st.session_state["nav_page"] = current

    # A sincronização ocorre antes da criação do widget neste rerun.
    if st.session_state.get(_CONTROL_KEY) != current:
        st.session_state[_CONTROL_KEY] = current

    original_radio(
        label,
        available,
        key=_CONTROL_KEY,
        label_visibility=label_visibility,
        format_func=lambda page: f"{NAV_ICONS.get(page, '•')}  {NAV_LABELS.get(page, page)}",
        on_change=_sync_page_from_mobile_control,
    )

    return str(st.session_state.get("nav_page") or current)
