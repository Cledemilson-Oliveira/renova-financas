from __future__ import annotations

import re
import unicodedata
import uuid
from datetime import datetime, timezone
from typing import Any

from src.repository import deactivate_ai_preference, upsert_ai_preference
from src.supabase_client import get_supabase


AREAS = {
    "Geral": "geral",
    "Vida pessoal": "pessoal",
    "Negócio": "negocio",
    "Financeiro": "financeiro",
    "Rotina": "rotina",
    "Vendas": "vendas",
    "Clientes": "clientes",
    "Preferências": "preferencias",
    "Regras": "regras",
}

KINDS = {
    "Conhecimento": "conhecimento",
    "Regra": "regra",
    "Preferência": "preferencia",
    "Vocabulário": "vocabulario",
    "Objetivo": "objetivo",
}

APPLICATION_MODES = {
    "Sempre considerar": "sempre",
    "Aplicar quando for relevante": "quando_relevante",
    "Usar somente em consultas/análises": "somente_consulta",
}


def _client():
    client = get_supabase()
    if client is None:
        raise RuntimeError("Supabase não configurado.")
    return client


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", value.lower()).strip()


def parse_keywords(raw: str) -> list[str]:
    values = []
    seen = set()
    for part in re.split(r"[,;\n]+", raw or ""):
        item = part.strip()
        key = _norm(item)
        if item and key and key not in seen:
            seen.add(key)
            values.append(item[:60])
    return values[:30]


def infer_structured_rule(content: str) -> dict[str, Any]:
    """Converte ensinamentos simples em regras operacionais já entendidas pela IA atual."""
    text = (content or "").strip()
    normalized = _norm(text)

    m = re.search(
        r"quando eu disser\s+(.+?)\s+(?:use|coloque|considere)\s+(?:a\s+)?categoria\s+(.+)$",
        text,
        flags=re.I,
    )
    if m:
        return {
            "rule_type": "category_alias",
            "trigger": m.group(1).strip(" .,:;-"),
            "category": m.group(2).strip(" .,:;-"),
        }

    m = re.search(
        r"quando eu disser\s+(.+?)\s+(?:considere|trate|registre)\s+(?:como\s+)?(receita|despesa)",
        text,
        flags=re.I,
    )
    if m:
        return {
            "rule_type": "type_alias",
            "trigger": m.group(1).strip(" .,:;-"),
            "kind": _norm(m.group(2)),
        }

    m = re.search(r"(?:use|utilize)\s+sempre\s+(?:a\s+)?conta\s+(.+)$", text, flags=re.I)
    if m:
        return {
            "rule_type": "default_account",
            "account": m.group(1).strip(" .,:;-"),
        }

    if any(token in normalized for token in ("aprenda que", "lembre que", "prefiro que", "sempre quero que")):
        return {"rule_type": "instruction", "text": text}

    return {"rule_type": "knowledge", "text": text}


def _preference_value(rule: dict[str, Any], content: str) -> dict[str, Any] | None:
    rule_type = str(rule.get("rule_type") or "")
    if rule_type == "category_alias":
        return {
            "type": "category_alias",
            "trigger": str(rule.get("trigger") or "").strip(),
            "category": str(rule.get("category") or "").strip(),
        }
    if rule_type == "type_alias":
        return {
            "type": "type_alias",
            "trigger": str(rule.get("trigger") or "").strip(),
            "kind": str(rule.get("kind") or "").strip(),
        }
    if rule_type == "default_account":
        return {"type": "default_account", "account": str(rule.get("account") or "").strip()}
    if rule_type in {"instruction", "knowledge"}:
        return {"type": "instruction", "text": str(rule.get("text") or content).strip()}
    return None


def create_training_item(
    user_id: str,
    *,
    title: str,
    area: str,
    kind: str,
    content: str,
    application_mode: str = "quando_relevante",
    keywords: list[str] | None = None,
    priority: int = 50,
    structured_rule: dict[str, Any] | None = None,
) -> str:
    title = (title or "").strip()
    content = (content or "").strip()
    if not title:
        raise ValueError("Informe um título para o treinamento.")
    if not content:
        raise ValueError("Escreva o que a IA deve aprender.")

    item_id = str(uuid.uuid4())
    rule = dict(structured_rule or infer_structured_rule(content))
    preference_key = f"training:{item_id}"
    rule["preference_key"] = preference_key

    _client().table("ai_training_items").insert(
        {
            "id": item_id,
            "user_id": user_id,
            "title": title[:120],
            "area": area,
            "kind": kind,
            "content": content[:10000],
            "application_mode": application_mode,
            "keywords": list(keywords or [])[:30],
            "structured_rule": rule,
            "priority": max(0, min(int(priority), 100)),
            "is_active": True,
        }
    ).execute()

    pref = _preference_value(rule, content)
    if pref:
        upsert_ai_preference(user_id, preference_key, pref, content)
    return item_id


def list_training_items(user_id: str, *, active_only: bool = False) -> list[dict[str, Any]]:
    query = (
        _client()
        .table("ai_training_items")
        .select(
            "id,title,area,kind,content,application_mode,keywords,structured_rule,priority,is_active,created_at,updated_at"
        )
        .eq("user_id", user_id)
    )
    if active_only:
        query = query.eq("is_active", True)
    response = query.order("priority", desc=True).order("updated_at", desc=True).execute()
    return response.data or []


def set_training_item_active(user_id: str, item_id: str, active: bool) -> None:
    rows = (
        _client()
        .table("ai_training_items")
        .select("content,structured_rule")
        .eq("id", item_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
        .data
        or []
    )
    if not rows:
        raise ValueError("Treinamento não encontrado.")
    row = rows[0]
    rule = row.get("structured_rule") or {}
    key = str(rule.get("preference_key") or f"training:{item_id}")

    (
        _client()
        .table("ai_training_items")
        .update({"is_active": bool(active), "updated_at": datetime.now(timezone.utc).isoformat()})
        .eq("id", item_id)
        .eq("user_id", user_id)
        .execute()
    )

    if active:
        pref = _preference_value(rule, str(row.get("content") or ""))
        if pref:
            upsert_ai_preference(user_id, key, pref, str(row.get("content") or ""))
    else:
        deactivate_ai_preference(user_id, key)


def delete_training_item(user_id: str, item_id: str) -> None:
    rows = (
        _client()
        .table("ai_training_items")
        .select("structured_rule")
        .eq("id", item_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
        .data
        or []
    )
    if rows:
        rule = rows[0].get("structured_rule") or {}
        key = str(rule.get("preference_key") or f"training:{item_id}")
        deactivate_ai_preference(user_id, key)

    (
        _client()
        .table("ai_training_items")
        .delete()
        .eq("id", item_id)
        .eq("user_id", user_id)
        .execute()
    )


def relevant_training_items(user_id: str, message: str, limit: int = 6) -> list[dict[str, Any]]:
    """Recuperação lexical simples para o contexto personalizado do usuário."""
    items = list_training_items(user_id, active_only=True)
    if not items:
        return []

    message_tokens = {token for token in re.findall(r"[a-zA-ZÀ-ÿ0-9]{3,}", _norm(message))}
    scored: list[tuple[float, dict[str, Any]]] = []
    for item in items:
        haystack = " ".join(
            [
                str(item.get("title") or ""),
                str(item.get("content") or ""),
                " ".join(item.get("keywords") or []),
            ]
        )
        item_tokens = {token for token in re.findall(r"[a-zA-ZÀ-ÿ0-9]{3,}", _norm(haystack))}
        overlap = len(message_tokens.intersection(item_tokens))
        priority = float(item.get("priority") or 50) / 100.0
        always_bonus = 2.0 if item.get("application_mode") == "sempre" else 0.0
        score = overlap + priority + always_bonus
        if overlap > 0 or always_bonus > 0:
            scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[: max(1, min(int(limit), 12))]]
