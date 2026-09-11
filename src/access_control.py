from __future__ import annotations

from typing import Any

import pandas as pd

from src.supabase_client import get_supabase


def _client():
    client = get_supabase()
    if client is None:
        raise RuntimeError("Supabase não configurado.")
    return client


def get_my_access(user_id: str) -> dict[str, Any] | None:
    response = (
        _client()
        .table("user_access")
        .select("user_id,email,role,status,created_at,updated_at")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def list_user_access() -> pd.DataFrame:
    """List users visible to the current session.

    RLS returns all rows only to the owner. A normal user can only see their
    own record, so authorization remains enforced in Postgres rather than in UI.
    """
    rows = (
        _client()
        .table("user_access")
        .select("user_id,email,role,status,created_at,updated_at")
        .order("created_at")
        .execute()
        .data
        or []
    )
    return pd.DataFrame(rows)


def update_user_access(user_id: str, role: str, status: str) -> None:
    if role not in {"admin", "usuario"}:
        raise ValueError("O papel de dono não pode ser atribuído por esta tela.")
    if status not in {"ativo", "suspenso"}:
        raise ValueError("Status inválido.")

    response = (
        _client()
        .table("user_access")
        .update({"role": role, "status": status})
        .eq("user_id", user_id)
        .execute()
    )
    if not response.data:
        raise PermissionError("Acesso não autorizado ou usuário não encontrado.")
