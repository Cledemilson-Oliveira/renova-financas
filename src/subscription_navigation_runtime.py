from __future__ import annotations

from functools import wraps
from typing import Any
from urllib.parse import urlparse

import streamlit as st


_INSTALLED = False
_ORIGINAL_LINK_BUTTON = None


def _is_internal_checkout(url: str) -> bool:
    try:
        parsed = urlparse(str(url))
        return parsed.path.rstrip("/").endswith("/Checkout_Assinatura")
    except Exception:
        return False


def install_subscription_navigation_runtime() -> None:
    """Mantém o CTA de assinatura dentro da mesma aba do Streamlit."""
    global _INSTALLED, _ORIGINAL_LINK_BUTTON
    if _INSTALLED:
        return

    _ORIGINAL_LINK_BUTTON = st.link_button

    @wraps(_ORIGINAL_LINK_BUTTON)
    def routed_link_button(label: str, url: str, *args: Any, **kwargs: Any) -> Any:
        if _is_internal_checkout(url):
            return st.page_link(
                "pages/Checkout_Assinatura.py",
                label=label,
                icon="💳",
                use_container_width=bool(kwargs.get("use_container_width", False)),
            )
        return _ORIGINAL_LINK_BUTTON(label, url, *args, **kwargs)

    st.link_button = routed_link_button
    _INSTALLED = True
