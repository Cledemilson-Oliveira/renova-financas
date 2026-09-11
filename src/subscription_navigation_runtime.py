from __future__ import annotations

from functools import wraps
from typing import Any
from urllib.parse import urlparse

import streamlit as st


_INSTALLED = False
_ORIGINAL_LINK_BUTTON = None
_CHECKOUT_SESSION_KEY = "renova_mp_checkout_url"


def _is_internal_checkout(url: str) -> bool:
    try:
        parsed = urlparse(str(url))
        return parsed.path.rstrip("/").endswith("/Checkout_Assinatura")
    except Exception:
        return False


def install_subscription_navigation_runtime() -> None:
    """Inicia a assinatura sem sair da sessão autenticada do app.

    O antigo fluxo navegava primeiro para uma página multipage. Em alguns
    navegadores isso recriava a sessão do Streamlit e o checkout não chegava a
    ser criado. Agora o CTA principal chama a Edge Function ainda na sessão
    autenticada atual e, somente depois de receber o ``init_point`` seguro do
    Mercado Pago, exibe o botão externo de pagamento.
    """
    global _INSTALLED, _ORIGINAL_LINK_BUTTON
    if _INSTALLED:
        return

    _ORIGINAL_LINK_BUTTON = st.link_button

    @wraps(_ORIGINAL_LINK_BUTTON)
    def routed_link_button(label: str, url: str, *args: Any, **kwargs: Any) -> Any:
        if not _is_internal_checkout(url):
            return _ORIGINAL_LINK_BUTTON(label, url, *args, **kwargs)

        use_container_width = bool(kwargs.get("use_container_width", False))

        if st.button(
            label,
            key="renova_start_mp_subscription",
            type="primary",
            use_container_width=use_container_width,
        ):
            st.session_state.pop(_CHECKOUT_SESSION_KEY, None)
            try:
                from .mercado_pago_checkout import create_subscription_checkout

                with st.spinner("Preparando checkout seguro no Mercado Pago..."):
                    checkout = create_subscription_checkout("renova_ia")

                if checkout.get("already_active"):
                    st.success("✅ Sua RENOVA IA Personalizada já está ativa.")
                else:
                    checkout_url = str(checkout.get("checkout_url") or "").strip()
                    if not checkout_url:
                        st.error("O Mercado Pago não devolveu o endereço do checkout.")
                    else:
                        st.session_state[_CHECKOUT_SESSION_KEY] = checkout_url
            except Exception as exc:
                st.error(f"Não foi possível abrir o checkout agora: {exc}")

        checkout_url = str(st.session_state.get(_CHECKOUT_SESSION_KEY) or "").strip()
        if checkout_url:
            st.success("Checkout criado. Agora abra o Mercado Pago para concluir a assinatura.")
            return _ORIGINAL_LINK_BUTTON(
                "ABRIR CHECKOUT SEGURO NO MERCADO PAGO →",
                checkout_url,
                use_container_width=True,
            )

        return None

    st.link_button = routed_link_button
    _INSTALLED = True
