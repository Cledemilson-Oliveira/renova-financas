from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from src.supabase_client import get_supabase


DEFAULT_CATEGORIES = [
    {"name": "Salário", "kind": "receita", "icon": "💼"},
    {"name": "Vendas", "kind": "receita", "icon": "💰"},
    {"name": "Serviços", "kind": "receita", "icon": "🧾"},
    {"name": "Moradia", "kind": "despesa", "icon": "🏠"},
    {"name": "Alimentação", "kind": "despesa", "icon": "🛒"},
    {"name": "Transporte", "kind": "despesa", "icon": "🚲"},
    {"name": "Saúde", "kind": "despesa", "icon": "❤️"},
    {"name": "Educação", "kind": "despesa", "icon": "📚"},
    {"name": "Família", "kind": "despesa", "icon": "👨‍👩‍👧‍👦"},
    {"name": "Lazer", "kind": "despesa", "icon": "🎯"},
    {"name": "Assinaturas", "kind": "despesa", "icon": "🔁"},
    {"name": "Outros", "kind": "ambos", "icon": "📌"},
]


def _client():
    client = get_supabase()
    if client is None:
        raise RuntimeError("Supabase não configurado.")
    return client


def bootstrap_user(user: Any) -> None:
    """Create the user's basic profile, account and categories once."""
    user_id = str(user.id)
    client = _client()

    metadata = getattr(user, "user_metadata", {}) or {}
    full_name = str(metadata.get("full_name") or "").strip()
    if not full_name:
        email = str(getattr(user, "email", "") or "")
        full_name = email.split("@")[0] if email else "Usuário RENOVA"

    profile = (
        client.table("profiles")
        .select("id")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    if not profile.data:
        client.table("profiles").insert(
            {"id": user_id, "full_name": full_name}
        ).execute()

    accounts = (
        client.table("accounts")
        .select("id")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not accounts.data:
        client.table("accounts").insert(
            {
                "user_id": user_id,
                "name": "Conta principal",
                "account_type": "conta",
                "currency": "BRL",
                "initial_balance": 0,
            }
        ).execute()

    categories = (
        client.table("categories")
        .select("id")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not categories.data:
        rows = [{"user_id": user_id, **category} for category in DEFAULT_CATEGORIES]
        client.table("categories").insert(rows).execute()


def fetch_financial_data(user_id: str) -> dict[str, pd.DataFrame]:
    client = _client()

    accounts_raw = (
        client.table("accounts")
        .select("id,name,account_type,initial_balance,is_active")
        .eq("user_id", user_id)
        .order("created_at")
        .execute()
        .data
        or []
    )
    categories_raw = (
        client.table("categories")
        .select("id,name,kind,icon,is_active")
        .eq("user_id", user_id)
        .order("name")
        .execute()
        .data
        or []
    )
    transactions_raw = (
        client.table("transactions")
        .select(
            "id,account_id,destination_account_id,category_id,kind,description,amount,occurred_on,status,notes"
        )
        .eq("user_id", user_id)
        .order("occurred_on", desc=True)
        .execute()
        .data
        or []
    )
    cards_raw = (
        client.table("cards")
        .select("id,account_id,name,credit_limit,closing_day,due_day,is_active")
        .eq("user_id", user_id)
        .order("created_at")
        .execute()
        .data
        or []
    )
    card_expenses_raw = (
        client.table("card_expenses")
        .select("id,card_id,category_id,description,amount,purchase_date,status")
        .eq("user_id", user_id)
        .order("purchase_date", desc=True)
        .execute()
        .data
        or []
    )
    budgets_raw = (
        client.table("budgets")
        .select("id,category_id,month,planned_amount")
        .eq("user_id", user_id)
        .order("month", desc=True)
        .execute()
        .data
        or []
    )
    goals_raw = (
        client.table("financial_goals")
        .select("id,name,target_amount,current_amount,target_date,status")
        .eq("user_id", user_id)
        .order("created_at")
        .execute()
        .data
        or []
    )

    account_names = {row["id"]: row["name"] for row in accounts_raw}
    category_names = {row["id"]: row["name"] for row in categories_raw}

    transactions = []
    for row in transactions_raw:
        kind_map = {
            "receita": "Receita",
            "despesa": "Despesa",
            "transferencia": "Transferência",
        }
        transactions.append(
            {
                "id": row["id"],
                "data": pd.to_datetime(row["occurred_on"]).date(),
                "tipo": kind_map.get(row["kind"], row["kind"].title()),
                "categoria": category_names.get(row.get("category_id"), "Sem categoria"),
                "categoria_id": row.get("category_id"),
                "descricao": row["description"],
                "valor": float(row["amount"]),
                "conta": account_names.get(row["account_id"], "Conta"),
                "conta_id": row["account_id"],
                "destino_id": row.get("destination_account_id"),
                "status": row["status"],
            }
        )
    tx_df = pd.DataFrame(transactions)
    if tx_df.empty:
        tx_df = pd.DataFrame(
            columns=[
                "id",
                "data",
                "tipo",
                "categoria",
                "categoria_id",
                "descricao",
                "valor",
                "conta",
                "conta_id",
                "destino_id",
                "status",
            ]
        )

    balances = {row["id"]: float(row["initial_balance"]) for row in accounts_raw}
    for row in transactions_raw:
        if row["status"] != "pago":
            continue
        amount = float(row["amount"])
        if row["kind"] == "receita":
            balances[row["account_id"]] = balances.get(row["account_id"], 0) + amount
        elif row["kind"] == "despesa":
            balances[row["account_id"]] = balances.get(row["account_id"], 0) - amount
        elif row["kind"] == "transferencia":
            balances[row["account_id"]] = balances.get(row["account_id"], 0) - amount
            destination_id = row.get("destination_account_id")
            if destination_id:
                balances[destination_id] = balances.get(destination_id, 0) + amount

    accounts = [
        {
            "id": row["id"],
            "conta": row["name"],
            "tipo": row["account_type"],
            "saldo": balances.get(row["id"], float(row["initial_balance"])),
            "ativo": bool(row["is_active"]),
        }
        for row in accounts_raw
    ]
    accounts_df = pd.DataFrame(accounts)
    if accounts_df.empty:
        accounts_df = pd.DataFrame(columns=["id", "conta", "tipo", "saldo", "ativo"])

    open_card_amounts: dict[str, float] = {}
    for row in card_expenses_raw:
        if row["status"] == "cancelada":
            continue
        open_card_amounts[row["card_id"]] = open_card_amounts.get(row["card_id"], 0) + float(row["amount"])

    cards = [
        {
            "id": row["id"],
            "cartao": row["name"],
            "limite": float(row["credit_limit"]),
            "fatura": open_card_amounts.get(row["id"], 0.0),
            "fechamento": row.get("closing_day") or 1,
            "vencimento": row.get("due_day") or 1,
            "ativo": bool(row["is_active"]),
        }
        for row in cards_raw
    ]
    cards_df = pd.DataFrame(cards)
    if cards_df.empty:
        cards_df = pd.DataFrame(
            columns=["id", "cartao", "limite", "fatura", "fechamento", "vencimento", "ativo"]
        )

    current_month = date.today().replace(day=1)
    month_expenses: dict[str, float] = {}
    for row in transactions_raw:
        if row["kind"] != "despesa" or row["status"] == "cancelado" or not row.get("category_id"):
            continue
        occurred = pd.to_datetime(row["occurred_on"]).date()
        if occurred.year == current_month.year and occurred.month == current_month.month:
            cid = row["category_id"]
            month_expenses[cid] = month_expenses.get(cid, 0) + float(row["amount"])

    budgets = []
    for row in budgets_raw:
        month_value = pd.to_datetime(row["month"]).date()
        if month_value.year == current_month.year and month_value.month == current_month.month:
            budgets.append(
                {
                    "id": row["id"],
                    "categoria_id": row["category_id"],
                    "categoria": category_names.get(row["category_id"], "Categoria"),
                    "orcamento": float(row["planned_amount"]),
                    "realizado": month_expenses.get(row["category_id"], 0.0),
                }
            )
    budgets_df = pd.DataFrame(budgets)
    if budgets_df.empty:
        budgets_df = pd.DataFrame(
            columns=["id", "categoria_id", "categoria", "orcamento", "realizado"]
        )

    categories_df = pd.DataFrame(categories_raw)
    if categories_df.empty:
        categories_df = pd.DataFrame(columns=["id", "name", "kind", "icon", "is_active"])

    goals_df = pd.DataFrame(goals_raw)
    if goals_df.empty:
        goals_df = pd.DataFrame(
            columns=["id", "name", "target_amount", "current_amount", "target_date", "status"]
        )

    return {
        "transactions": tx_df,
        "accounts": accounts_df,
        "cards": cards_df,
        "budgets": budgets_df,
        "categories": categories_df,
        "goals": goals_df,
    }


def create_transaction(
    user_id: str,
    account_id: str,
    category_id: str | None,
    kind: str,
    description: str,
    amount: float,
    occurred_on: date,
) -> None:
    payload = {
        "user_id": user_id,
        "account_id": account_id,
        "category_id": category_id,
        "kind": kind,
        "description": description.strip(),
        "amount": float(amount),
        "occurred_on": occurred_on.isoformat(),
        "status": "pago",
    }
    _client().table("transactions").insert(payload).execute()


def create_account(
    user_id: str,
    name: str,
    account_type: str,
    initial_balance: float,
) -> None:
    _client().table("accounts").insert(
        {
            "user_id": user_id,
            "name": name.strip(),
            "account_type": account_type,
            "currency": "BRL",
            "initial_balance": float(initial_balance),
        }
    ).execute()


def create_card(
    user_id: str,
    name: str,
    credit_limit: float,
    closing_day: int,
    due_day: int,
    account_id: str | None = None,
) -> None:
    _client().table("cards").insert(
        {
            "user_id": user_id,
            "account_id": account_id,
            "name": name.strip(),
            "credit_limit": float(credit_limit),
            "closing_day": int(closing_day),
            "due_day": int(due_day),
        }
    ).execute()


def upsert_budget(
    user_id: str,
    category_id: str,
    month: date,
    planned_amount: float,
) -> None:
    normalized_month = month.replace(day=1).isoformat()
    _client().table("budgets").upsert(
        {
            "user_id": user_id,
            "category_id": category_id,
            "month": normalized_month,
            "planned_amount": float(planned_amount),
        },
        on_conflict="user_id,category_id,month",
    ).execute()
