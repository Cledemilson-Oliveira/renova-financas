from __future__ import annotations

from functools import wraps
from typing import Any

import streamlit as st

from .ui.device import current_device


_INSTALLED = False
_ORIGINAL_RADIO = None


def install_navigation_runtime() -> None:
    """Substitui somente o rádio principal por navegadores específicos.

    O app histórico usa ``key='nav_page'`` no ``st.radio`` e também altera
    ``st.session_state.nav_page`` em botões de atalho. O Streamlit proíbe essa
    alteração depois que um widget com a mesma chave é instanciado. Aqui
    ``nav_page`` deixa de ser chave de widget e volta a ser apenas estado de
    aplicação, eliminando o conflito sem reescrever as regras financeiras.

    A rota de assinatura é tratada separadamente para abrir a página comercial
    completa antes da criação do checkout Mercado Pago.
    """
    global _INSTALLED, _ORIGINAL_RADIO
    if _INSTALLED:
        return

    _ORIGINAL_RADIO = st.radio

    @wraps(_ORIGINAL_RADIO)
    def routed_radio(label: str, options: Any, *args: Any, **kwargs: Any) -> Any:
        key = kwargs.get("key")
        if key != "nav_page":
            return _ORIGINAL_RADIO(label, options, *args, **kwargs)

        available = list(options)
        if not available:
            return None

        current = str(st.session_state.get("nav_page") or available[0])
        if current not in available:
            current = available[0]
            st.session_state["nav_page"] = current

        # Toda entrada para a assinatura passa primeiro pela página de vendas.
        # Isso também cobre atalhos internos que apenas definem nav_page e fazem rerun.
        if current == "Assinar RENOVA IA":
            st.switch_page("pages/Assinar_RENOVA_IA.py")

        if current_device() == "mobile":
            from .ui.navigation_mobile import render_mobile_navigation

            return render_mobile_navigation(
                _ORIGINAL_RADIO,
                available,
                current,
                label=label,
                label_visibility=str(kwargs.get("label_visibility") or "collapsed"),
            )

        from .ui.navigation_desktop import render_desktop_navigation

        return render_desktop_navigation(available, current)

    st.radio = routed_radio
    _INSTALLED = True
