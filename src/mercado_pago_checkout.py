from __future__ import annotations

from typing import Any

import httpx
import streamlit as st

from .supabase_client import _secret


TRANSPARENT_PAYMENT_FUNCTION = "mercado-pago-create-subscription"


def _access_token() -> str:
    session = st.session_state.get("auth_session")
    return str(getattr(session, "access_token", "") or "")


def _functions_base_url() -> str:
    supabase_url = str(_secret("SUPABASE_URL") or "").strip().rstrip("/")
    if not supabase_url:
        raise RuntimeError("Supabase não configurado neste ambiente.")
    return f"{supabase_url}/functions/v1"


def transparent_function_url() -> str:
    return f"{_functions_base_url()}/{TRANSPARENT_PAYMENT_FUNCTION}"


def transparent_auth_token() -> str:
    token = _access_token()
    if not token:
        raise RuntimeError("Sua sessão expirou. Entre novamente para continuar.")
    return token


def _call_transparent(payload: dict[str, Any]) -> dict[str, Any]:
    token = transparent_auth_token()
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            transparent_function_url(),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    try:
        data = response.json()
    except Exception:
        data = {}

    if response.status_code >= 400:
        error = str(data.get("error") or "checkout_error")
        message = str(data.get("message") or "Não foi possível processar o pagamento.")
        if error == "mercado_pago_not_configured":
            raise RuntimeError("O Access Token do Mercado Pago ainda não foi configurado no backend.")
        if error == "public_key_not_configured":
            raise RuntimeError("A Public Key do Mercado Pago ainda não foi configurada no backend.")
        raise RuntimeError(message)

    return dict(data)


def get_transparent_checkout_config(plan_code: str = "renova_ia") -> dict[str, Any]:
    return _call_transparent({"action": "config", "plan_code": plan_code})


def create_pix_payment(*, payer_name: str, cpf: str, plan_code: str = "renova_ia") -> dict[str, Any]:
    return _call_transparent(
        {
            "action": "pix",
            "plan_code": plan_code,
            "payer": {"name": payer_name, "cpf": cpf},
        }
    )


def create_boleto_payment(
    *,
    payer_name: str,
    cpf: str,
    zip_code: str,
    street_name: str,
    street_number: str,
    neighborhood: str,
    city: str,
    state: str,
    plan_code: str = "renova_ia",
) -> dict[str, Any]:
    return _call_transparent(
        {
            "action": "boleto",
            "plan_code": plan_code,
            "payer": {
                "name": payer_name,
                "cpf": cpf,
                "address": {
                    "zip_code": zip_code,
                    "street_name": street_name,
                    "street_number": street_number,
                    "neighborhood": neighborhood,
                    "city": city,
                    "state": state,
                },
            },
        }
    )


# Compatibilidade temporária: nenhum fluxo novo deve usar URL externa.
def create_subscription_checkout(plan_code: str = "renova_ia") -> dict[str, Any]:
    return get_transparent_checkout_config(plan_code)
