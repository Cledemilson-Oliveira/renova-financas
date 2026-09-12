from __future__ import annotations

import re

import streamlit as st


MOBILE_TOKENS = (
    "android",
    "iphone",
    "ipod",
    "windows phone",
    "blackberry",
    "opera mini",
    "mobile",
)


def _query_override() -> str:
    try:
        value = str(st.query_params.get("layout") or "").strip().lower()
    except Exception:
        value = ""
    return value if value in {"mobile", "desktop"} else ""


def _user_agent() -> str:
    try:
        headers = st.context.headers
        return str(headers.get("User-Agent") or headers.get("user-agent") or "")
    except Exception:
        return ""


def current_device() -> str:
    """Retorna ``mobile`` ou ``desktop`` sem misturar lógica de negócio.

    ``?layout=mobile`` e ``?layout=desktop`` podem ser usados para teste manual.
    Em uso normal, a classificação é feita pelo User-Agent do navegador.
    """
    forced = _query_override()
    if forced:
        return forced

    ua = _user_agent().lower()
    compact_tablet = bool(re.search(r"ipad|tablet|kindle|silk", ua))

    # Recalcula a partir do User-Agent em cada rerun. Antes, uma classificação
    # equivocada ficava presa na sessão e o celular continuava recebendo o
    # runtime desktop até o usuário sair/limpar a sessão.
    if ua:
        mode = "mobile" if any(token in ua for token in MOBILE_TOKENS) or compact_tablet else "desktop"
        st.session_state.renova_device_mode = mode
        return mode

    # Se o proxy não expuser User-Agent, só então reutilizamos o último valor.
    cached = str(st.session_state.get("renova_device_mode") or "").strip().lower()
    if cached in {"mobile", "desktop"}:
        return cached

    return "desktop"


def is_mobile() -> bool:
    return current_device() == "mobile"
