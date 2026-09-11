from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

from src.supabase_client import get_supabase, request_password_reset


PLAN_CODE = "renova_ia"


def _client():
    client = get_supabase()
    if client is None:
        raise RuntimeError("Supabase não configurado.")
    return client


def normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if not digits:
        return ""
    if len(digits) in {10, 11}:
        digits = "55" + digits
    return "+" + digits


def whatsapp_url(phone: str, full_name: str = "") -> str:
    digits = re.sub(r"\D", "", normalize_phone(phone))
    if not digits:
        return ""
    first_name = (full_name or "").strip().split(" ")[0] if full_name else ""
    greeting = f"Olá, {first_name}! " if first_name else "Olá! "
    text = quote(greeting + "Aqui é o suporte do RENOVA Finanças. Como posso te ajudar?")
    return f"https://wa.me/{digits}?text={text}"


def list_owner_users() -> list[dict[str, Any]]:
    client = _client()

    access_rows = (
        client.table("user_access")
        .select("user_id,email,role,status,created_at,updated_at")
        .order("created_at")
        .execute()
        .data
        or []
    )
    profile_rows = (
        client.table("profiles")
        .select("id,full_name,phone,created_at,updated_at")
        .execute()
        .data
        or []
    )
    subscription_rows = (
        client.table("ai_subscriptions")
        .select(
            "user_id,plan_code,status,provider,locked_price,current_period_end,"
            "started_at,cancelled_at,updated_at"
        )
        .eq("plan_code", PLAN_CODE)
        .execute()
        .data
        or []
    )

    profiles = {str(row["id"]): row for row in profile_rows}
    subscriptions = {str(row["user_id"]): row for row in subscription_rows}

    merged: list[dict[str, Any]] = []
    for access in access_rows:
        uid = str(access["user_id"])
        profile = profiles.get(uid, {})
        subscription = subscriptions.get(uid, {})
        premium = subscription.get("status") == "active"
        merged.append(
            {
                **access,
                "full_name": str(profile.get("full_name") or "").strip(),
                "phone": str(profile.get("phone") or "").strip(),
                "plan": "RENOVA IA Personal" if premium else "Gratuito",
                "subscription_status": str(subscription.get("status") or "inactive"),
                "locked_price": subscription.get("locked_price"),
                "provider": subscription.get("provider"),
                "current_period_end": subscription.get("current_period_end"),
            }
        )
    return merged


def update_user_profile(user_id: str, full_name: str, phone: str) -> None:
    normalized_phone = normalize_phone(phone)
    (
        _client()
        .table("profiles")
        .upsert(
            {
                "id": user_id,
                "full_name": " ".join((full_name or "").split()).strip(),
                "phone": normalized_phone or None,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            on_conflict="id",
        )
        .execute()
    )


def set_user_plan(user_id: str, plan: str) -> None:
    client = _client()
    normalized = plan.strip().lower()

    if normalized == "gratuito":
        existing = (
            client.table("ai_subscriptions")
            .select("id")
            .eq("user_id", user_id)
            .eq("plan_code", PLAN_CODE)
            .limit(1)
            .execute()
            .data
            or []
        )
        if existing:
            (
                client.table("ai_subscriptions")
                .update(
                    {
                        "status": "cancelled",
                        "cancelled_at": datetime.now(timezone.utc).isoformat(),
                        "metadata": {"source": "owner_manual"},
                    }
                )
                .eq("id", existing[0]["id"])
                .execute()
            )
        return

    if normalized != "renova ia personal":
        raise ValueError("Plano inválido.")

    plan_row = (
        client.table("ai_subscription_plans")
        .select("price")
        .eq("code", PLAN_CODE)
        .limit(1)
        .execute()
        .data
        or []
    )
    current_price = float(plan_row[0]["price"]) if plan_row else 9.90
    now = datetime.now(timezone.utc).isoformat()
    client.table("ai_subscriptions").upsert(
        {
            "user_id": user_id,
            "plan_code": PLAN_CODE,
            "status": "active",
            "provider": "owner_manual",
            "locked_price": current_price,
            "started_at": now,
            "cancelled_at": None,
            "metadata": {
                "source": "owner_manual",
                "price_lock": "while_active",
            },
            "updated_at": now,
        },
        on_conflict="user_id,plan_code",
    ).execute()


def send_password_reset(email: str) -> None:
    request_password_reset(email)
