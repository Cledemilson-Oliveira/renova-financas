from __future__ import annotations

import os
from typing import Optional

import streamlit as st
from supabase import Client, create_client


DEFAULT_PUBLIC_APP_URL = "https://minhas-financas-renova.streamlit.app"


def _secret(name: str) -> Optional[str]:
    try:
        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name)


def public_app_url() -> str:
    """URL pública canônica usada por confirmação de e-mail e recuperação."""
    value = _secret("PUBLIC_APP_URL") or DEFAULT_PUBLIC_APP_URL
    return str(value).strip().rstrip("/")


def is_configured() -> bool:
    url = _secret("SUPABASE_URL")
    key = _secret("SUPABASE_PUBLISHABLE_KEY") or _secret("SUPABASE_KEY")
    return bool(url and key)


def get_supabase() -> Optional[Client]:
    """Return one Supabase client per Streamlit user session.

    Important: authenticated Supabase clients must not be cached globally with
    st.cache_resource, because auth state is mutable. Keeping the client in
    st.session_state prevents one visitor's auth session from being reused by
    another visitor in the same Streamlit process.
    """
    if not is_configured():
        return None

    if "supabase_client" not in st.session_state:
        url = _secret("SUPABASE_URL")
        key = _secret("SUPABASE_PUBLISHABLE_KEY") or _secret("SUPABASE_KEY")
        st.session_state.supabase_client = create_client(str(url), str(key))

    return st.session_state.supabase_client


def sign_in(email: str, password: str):
    client = get_supabase()
    if client is None:
        raise RuntimeError("Supabase ainda não configurado.")

    response = client.auth.sign_in_with_password(
        {"email": email.strip().lower(), "password": password}
    )
    st.session_state.auth_user = response.user
    st.session_state.auth_session = response.session
    return response


def sign_up(email: str, password: str, full_name: str = "", phone: str = ""):
    client = get_supabase()
    if client is None:
        raise RuntimeError("Supabase ainda não configurado.")

    metadata = {}
    if full_name.strip():
        metadata["full_name"] = full_name.strip()
    if phone.strip():
        metadata["phone"] = phone.strip()

    payload = {
        "email": email.strip().lower(),
        "password": password,
        "options": {
            "email_redirect_to": public_app_url(),
            "data": metadata,
        },
    }

    response = client.auth.sign_up(payload)
    if response.session is not None:
        st.session_state.auth_user = response.user
        st.session_state.auth_session = response.session
    return response


def request_password_reset(email: str) -> None:
    """Solicita ao Supabase um e-mail seguro de recuperação de senha."""
    client = get_supabase()
    if client is None:
        raise RuntimeError("Supabase ainda não configurado.")
    client.auth.reset_password_for_email(
        email.strip().lower(),
        {"redirect_to": public_app_url()},
    )


def current_user():
    return st.session_state.get("auth_user")


def is_authenticated() -> bool:
    user = current_user()
    return bool(user and getattr(user, "id", None))


def sign_out() -> None:
    client = get_supabase()
    if client is not None:
        try:
            client.auth.sign_out()
        except Exception:
            pass

    for key in (
        "auth_user",
        "auth_session",
        "supabase_client",
        "bootstrap_user_id",
    ):
        st.session_state.pop(key, None)
