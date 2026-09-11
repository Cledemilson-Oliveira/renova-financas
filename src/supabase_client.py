from __future__ import annotations

import os
from typing import Optional

import streamlit as st
from supabase import Client, create_client


def _secret(name: str) -> Optional[str]:
    try:
        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name)


@st.cache_resource(show_spinner=False)
def get_supabase() -> Optional[Client]:
    """Create a Supabase client using only the publishable key.

    The app must never receive a service-role/secret key. Authorization is
    enforced by Supabase Auth + RLS policies in the database.
    """
    url = _secret("SUPABASE_URL")
    key = _secret("SUPABASE_PUBLISHABLE_KEY") or _secret("SUPABASE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def is_configured() -> bool:
    return get_supabase() is not None


def sign_in(email: str, password: str):
    client = get_supabase()
    if client is None:
        raise RuntimeError("Supabase ainda não configurado.")
    return client.auth.sign_in_with_password({"email": email, "password": password})


def sign_up(email: str, password: str):
    client = get_supabase()
    if client is None:
        raise RuntimeError("Supabase ainda não configurado.")
    return client.auth.sign_up({"email": email, "password": password})


def sign_out() -> None:
    client = get_supabase()
    if client is not None:
        client.auth.sign_out()
