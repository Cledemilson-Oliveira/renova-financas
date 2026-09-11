from __future__ import annotations

from typing import Any

import httpx
import streamlit as st

from .supabase_client import _secret


CREATE_SUBSCRIPTION_FUNCTION = "mercado-pago-create-subscription"


def _access_token() -> str:
    session = st.session_state.get("auth_session")
    return str(getattr(session, "access_token", "") or "")


def _functions_base_url() -> str:
    supabase_url = str(_secret("SUPABASE_URL") or "").strip().rstrip("/")
    if not supabase_url:
        raise RuntimeError("Supabase não configurado neste ambiente.")
    return f"{supabase_url}/functions/v1"


def create_subscription_checkout(plan_code: str = "renova_ia") -> dict[str, Any]:
    """Cria ou reutiliza um checkout Mercado Pago para o usuário autenticado."""
    token = _access_token()
    if not token:
        raise RuntimeError("Sua sessão expirou. Entre novamente para continuar.")

    url = f"{_functions_base_url()}/{CREATE_SUBSCRIPTION_FUNCTION}"
    with httpx.Client(timeout=25.0) as client:
        response = client.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={"plan_code": plan_code},
        )

    try:
        payload = response.json()
    except Exception:
        payload = {}

    if response.status_code >= 400:
        error = str(payload.get("error") or "checkout_error")
        message = str(payload.get("message") or "Não foi possível iniciar o checkout.")
        if error == "mercado_pago_not_configured":
            raise RuntimeError(
                "O checkout está instalado, mas o Access Token do Mercado Pago ainda não foi configurado no backend."
            )
        raise RuntimeError(message)

    return dict(payload)
