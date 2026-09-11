from __future__ import annotations

from typing import Any

from src.supabase_client import get_supabase


ROLE_LABELS = {
    "dono": "Dono",
    "admin": "Administrador",
    "usuario": "Usuário",
}

STATUS_LABELS = {
    "ativo": "Ativo",
    "suspenso": "Suspenso",
}


def _client():
    client = get_supabase()
    if client is None:
        raise RuntimeError("Supabase não configurado.")
    return client


def get_current_access(user_id: str) -> dict[str, Any] | None:
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


def is_owner(user_id: str) -> bool:
    access = get_current_access(user_id)
    return bool(access and access.get("role") == "dono" and access.get("status") == "ativo")


def is_active(user_id: str) -> bool:
    access = get_current_access(user_id)
    return bool(access and access.get("status") == "ativo")


def list_user_access() -> list[dict[str, Any]]:
    """Owner-only through RLS: returns all access records for the authenticated owner."""
    response = (
        _client()
        .table("user_access")
        .select("user_id,email,role,status,created_at,updated_at")
        .order("created_at", desc=False)
        .execute()
    )
    return response.data or []


def update_user_access(user_id: str, role: str, status: str) -> None:
    if role not in {"admin", "usuario"}:
        raise ValueError("O papel do dono não pode ser atribuído manualmente.")
    if status not in {"ativo", "suspenso"}:
        raise ValueError("Status inválido.")

    (
        _client()
        .table("user_access")
        .update({"role": role, "status": status})
        .eq("user_id", user_id)
        .execute()
    )
