from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

import pandas as pd

from src.supabase_client import get_supabase


MONEY = Decimal("0.01")
SCHEDULE_FIXED = "mensal_fixa"
SCHEDULE_INSTALLMENTS = "parcelada"


def _client():
    client = get_supabase()
    if client is None:
        raise RuntimeError("Supabase não configurado.")
    return client


def _as_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def _money(value: float | Decimal | str) -> Decimal:
    return Decimal(str(value)).quantize(MONEY, rounding=ROUND_HALF_UP)


def month_end(value: date) -> date:
    return date(value.year, value.month, calendar.monthrange(value.year, value.month)[1])


def add_months(value: date, months: int = 1, *, due_day: int | None = None) -> date:
    absolute = value.year * 12 + (value.month - 1) + months
    year = absolute // 12
    month = absolute % 12 + 1
    preferred_day = int(due_day or value.day)
    day = min(preferred_day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def installment_amount(total_amount: float | Decimal | str, installments: int) -> Decimal:
    if installments < 1:
        raise ValueError("A quantidade de parcelas deve ser maior que zero.")
    return (_money(total_amount) / Decimal(installments)).quantize(MONEY, rounding=ROUND_HALF_UP)


def _occurrence_amount(plan: dict[str, Any], installment_number: int | None = None) -> Decimal:
    base = _money(plan.get("amount") or 0)
    if str(plan.get("schedule_type") or SCHEDULE_FIXED) != SCHEDULE_INSTALLMENTS:
        return base

    total_installments = int(plan.get("total_installments") or 0)
    total_amount_raw = plan.get("total_amount")
    if not total_installments or total_amount_raw in (None, ""):
        return base

    if installment_number == total_installments:
        total = _money(total_amount_raw)
        # A última parcela fecha exatamente o valor total do parcelamento.
        # Isso continua correto mesmo quando o usuário edita valor/quantidade
        # depois de algumas parcelas já terem sido geradas.
        previous = Decimal("0.00")
        recurring_id = str(plan.get("id") or "").strip()
        user_id = str(plan.get("user_id") or "").strip()
        if recurring_id and user_id:
            rows = (
                _client().table("transactions")
                .select("amount")
                .eq("user_id", user_id)
                .eq("recurring_id", recurring_id)
                .execute()
                .data
                or []
            )
            previous = sum((_money(row.get("amount") or 0) for row in rows), Decimal("0.00"))
        else:
            previous = base * Decimal(max(total_installments - 1, 0))
        last = (total - previous).quantize(MONEY, rounding=ROUND_HALF_UP)
        if last <= 0:
            raise ValueError("O valor restante do parcelamento ficou inválido após a edição.")
        return last
    return base


def create_recurring_plan(
    user_id: str,
    *,
    account_id: str,
    category_id: str | None,
    kind: str,
    description: str,
    schedule_type: str,
    first_due_date: date,
    monthly_amount: float | None = None,
    total_amount: float | None = None,
    total_installments: int | None = None,
    notes: str = "",
) -> dict[str, Any]:
    if kind not in {"receita", "despesa"}:
        raise ValueError("Tipo deve ser receita ou despesa.")
    if schedule_type not in {SCHEDULE_FIXED, SCHEDULE_INSTALLMENTS}:
        raise ValueError("Modalidade recorrente inválida.")
    if not description.strip():
        raise ValueError("Informe uma descrição.")

    due_day = int(first_due_date.day)
    payload: dict[str, Any] = {
        "user_id": user_id,
        "account_id": account_id,
        "category_id": category_id,
        "kind": kind,
        "description": description.strip(),
        "frequency": "mensal",
        "schedule_type": schedule_type,
        "start_date": first_due_date.isoformat(),
        "next_due_date": first_due_date.isoformat(),
        "due_day": due_day,
        "generated_installments": 0,
        "is_active": True,
        "notes": notes.strip() or None,
    }

    if schedule_type == SCHEDULE_FIXED:
        amount = _money(monthly_amount or 0)
        if amount <= 0:
            raise ValueError("Informe um valor mensal maior que zero.")
        payload["amount"] = float(amount)
        payload["total_amount"] = None
        payload["total_installments"] = None
        payload["end_date"] = None
    else:
        installments = int(total_installments or 0)
        total = _money(total_amount or 0)
        if installments < 1 or installments > 360:
            raise ValueError("Informe entre 1 e 360 parcelas.")
        if total <= 0:
            raise ValueError("Informe o valor total do parcelamento.")
        parcel = installment_amount(total, installments)
        payload["amount"] = float(parcel)
        payload["total_amount"] = float(total)
        payload["total_installments"] = installments
        payload["end_date"] = add_months(first_due_date, installments - 1, due_day=due_day).isoformat()

    response = _client().table("recurring_transactions").insert(payload).execute()
    rows = response.data or []
    created = rows[0] if rows else payload

    # Se o primeiro vencimento pertence ao mês atual (ou ficou para trás),
    # o compromisso já nasce em Lançamentos como previsto.
    materialize_due_recurring(user_id, horizon=month_end(date.today()))
    return created


def materialize_due_recurring(user_id: str, *, horizon: date | None = None) -> int:
    """Transforma recorrências vencidas/atuais em lançamentos previstos, sem duplicar."""
    client = _client()
    horizon = horizon or month_end(date.today())
    plans = (
        client.table("recurring_transactions")
        .select(
            "id,user_id,account_id,category_id,kind,description,amount,frequency,next_due_date,is_active,"
            "schedule_type,start_date,due_day,total_amount,total_installments,generated_installments,end_date,notes"
        )
        .eq("user_id", user_id)
        .eq("is_active", True)
        .order("next_due_date")
        .execute()
        .data
        or []
    )

    created_count = 0
    for plan in plans:
        next_due = _as_date(plan.get("next_due_date"))
        if next_due is None:
            continue

        due_day = int(plan.get("due_day") or next_due.day)
        schedule_type = str(plan.get("schedule_type") or SCHEDULE_FIXED)
        generated = int(plan.get("generated_installments") or 0)
        total_installments = int(plan.get("total_installments") or 0) if plan.get("total_installments") else None
        active = bool(plan.get("is_active"))

        while active and next_due <= horizon:
            installment_number: int | None = None
            installment_total: int | None = None

            if schedule_type == SCHEDULE_INSTALLMENTS:
                if total_installments is None or generated >= total_installments:
                    active = False
                    break
                installment_number = generated + 1
                installment_total = total_installments

            existing = (
                client.table("transactions")
                .select("id")
                .eq("user_id", user_id)
                .eq("recurring_id", str(plan["id"]))
                .eq("due_date", next_due.isoformat())
                .limit(1)
                .execute()
                .data
                or []
            )

            if not existing:
                amount = _occurrence_amount(plan, installment_number)
                description = str(plan.get("description") or "Lançamento recorrente")
                if installment_number and installment_total:
                    description = f"{description} • {installment_number}/{installment_total}"

                payload = {
                    "user_id": user_id,
                    "account_id": plan["account_id"],
                    "category_id": plan.get("category_id"),
                    "kind": plan["kind"],
                    "description": description,
                    "amount": float(amount),
                    "occurred_on": next_due.isoformat(),
                    "due_date": next_due.isoformat(),
                    "status": "previsto",
                    "notes": "Gerado automaticamente por recorrência RENOVA.",
                    "recurring_id": plan["id"],
                    "installment_number": installment_number,
                    "installment_total": installment_total,
                }
                client.table("transactions").insert(payload).execute()
                created_count += 1

            if schedule_type == SCHEDULE_INSTALLMENTS:
                generated += 1
                if total_installments is not None and generated >= total_installments:
                    active = False

            next_due = add_months(next_due, 1, due_day=due_day)

        update_payload: dict[str, Any] = {
            "next_due_date": next_due.isoformat(),
            "is_active": active,
        }
        if schedule_type == SCHEDULE_INSTALLMENTS:
            update_payload["generated_installments"] = generated

        client.table("recurring_transactions").update(update_payload).eq("id", str(plan["id"])).eq(
            "user_id", user_id
        ).execute()

    return created_count


def list_recurring_plans(user_id: str, *, include_inactive: bool = True) -> pd.DataFrame:
    client = _client()
    query = (
        client.table("recurring_transactions")
        .select(
            "id,account_id,category_id,kind,description,amount,frequency,next_due_date,is_active,"
            "schedule_type,start_date,due_day,total_amount,total_installments,generated_installments,end_date,notes"
        )
        .eq("user_id", user_id)
        .order("created_at", desc=True)
    )
    if not include_inactive:
        query = query.eq("is_active", True)
    rows = query.execute().data or []

    accounts = (
        client.table("accounts").select("id,name").eq("user_id", user_id).execute().data or []
    )
    categories = (
        client.table("categories").select("id,name").eq("user_id", user_id).execute().data or []
    )
    account_names = {str(row["id"]): str(row["name"]) for row in accounts}
    category_names = {str(row["id"]): str(row["name"]) for row in categories}

    normalized: list[dict[str, Any]] = []
    for row in rows:
        total_installments = int(row.get("total_installments") or 0) if row.get("total_installments") else None
        generated = int(row.get("generated_installments") or 0)
        remaining = max((total_installments or 0) - generated, 0) if total_installments else None
        normalized.append(
            {
                **row,
                "tipo": "Receita" if row.get("kind") == "receita" else "Despesa",
                "modalidade": "Fixa mensal" if row.get("schedule_type") == SCHEDULE_FIXED else "Parcelada",
                "conta": account_names.get(str(row.get("account_id")), "Conta"),
                "categoria": category_names.get(str(row.get("category_id")), "Sem categoria"),
                "valor_ciclo": float(row.get("amount") or 0),
                "valor_total": float(row.get("total_amount") or 0) if row.get("total_amount") is not None else None,
                "parcelas_total": total_installments,
                "parcelas_geradas": generated,
                "parcelas_restantes": remaining,
                "proximo_vencimento": _as_date(row.get("next_due_date")),
                "termino": _as_date(row.get("end_date")),
                "ativo": bool(row.get("is_active")),
            }
        )

    frame = pd.DataFrame(normalized)
    if frame.empty:
        frame = pd.DataFrame(
            columns=[
                "id",
                "kind",
                "tipo",
                "schedule_type",
                "modalidade",
                "description",
                "valor_ciclo",
                "valor_total",
                "parcelas_total",
                "parcelas_geradas",
                "parcelas_restantes",
                "proximo_vencimento",
                "termino",
                "conta",
                "categoria",
                "ativo",
            ]
        )
    return frame


def _generated_amount_total(user_id: str, recurring_id: str) -> Decimal:
    rows = (
        _client().table("transactions")
        .select("amount")
        .eq("user_id", user_id)
        .eq("recurring_id", recurring_id)
        .execute()
        .data
        or []
    )
    return sum((_money(row.get("amount") or 0) for row in rows), Decimal("0.00"))


def update_recurring_plan(
    user_id: str,
    recurring_id: str,
    *,
    account_id: str,
    category_id: str | None,
    description: str,
    next_due_date: date,
    notes: str = "",
    monthly_amount: float | None = None,
    total_amount: float | None = None,
    total_installments: int | None = None,
) -> dict[str, Any]:
    """Edita somente a configuração futura de uma recorrência do próprio usuário.

    Lançamentos já materializados permanecem intactos. Para parcelamentos já
    iniciados, o valor das parcelas futuras é recalculado sobre o saldo que
    ainda falta gerar, preservando o total informado pelo usuário.
    """
    if not description.strip():
        raise ValueError("Informe uma descrição.")

    client = _client()
    rows = (
        client.table("recurring_transactions")
        .select(
            "id,user_id,account_id,category_id,kind,description,amount,frequency,next_due_date,is_active,"
            "schedule_type,start_date,due_day,total_amount,total_installments,generated_installments,end_date,notes"
        )
        .eq("id", recurring_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
        .data
        or []
    )
    if not rows:
        raise ValueError("Recorrência não encontrada.")

    plan = rows[0]
    schedule_type = str(plan.get("schedule_type") or SCHEDULE_FIXED)
    generated = int(plan.get("generated_installments") or 0)
    due_day = int(next_due_date.day)

    payload: dict[str, Any] = {
        "account_id": account_id,
        "category_id": category_id,
        "description": description.strip(),
        "next_due_date": next_due_date.isoformat(),
        "due_day": due_day,
        "notes": notes.strip() or None,
    }

    if schedule_type == SCHEDULE_FIXED:
        amount = _money(monthly_amount or 0)
        if amount <= 0:
            raise ValueError("Informe um valor mensal maior que zero.")
        payload.update(
            {
                "amount": float(amount),
                "total_amount": None,
                "total_installments": None,
                "end_date": None,
            }
        )
    elif schedule_type == SCHEDULE_INSTALLMENTS:
        installments = int(total_installments or 0)
        current_total_installments = int(plan.get("total_installments") or 0)
        completed = current_total_installments > 0 and generated >= current_total_installments

        if completed:
            # Parcelamento concluído: somente dados descritivos podem ser corrigidos.
            payload.update(
                {
                    "amount": float(_money(plan.get("amount") or 0)),
                    "total_amount": float(_money(plan.get("total_amount") or 0)),
                    "total_installments": current_total_installments,
                    "end_date": plan.get("end_date"),
                }
            )
        else:
            if installments < max(generated + 1, 1) or installments > 360:
                raise ValueError(
                    f"Informe entre {max(generated + 1, 1)} e 360 parcelas; "
                    f"{generated} já foram geradas."
                )
            total = _money(total_amount or 0)
            if total <= 0:
                raise ValueError("Informe o valor total do parcelamento.")

            already_generated = _generated_amount_total(user_id, recurring_id)
            remaining_count = installments - generated
            remaining_total = (total - already_generated).quantize(MONEY, rounding=ROUND_HALF_UP)
            if remaining_total <= 0:
                raise ValueError(
                    "O novo valor total precisa ser maior que o valor das parcelas já geradas."
                )
            parcel = (remaining_total / Decimal(remaining_count)).quantize(MONEY, rounding=ROUND_HALF_UP)
            if parcel <= 0:
                raise ValueError("O valor das próximas parcelas ficou inválido.")

            payload.update(
                {
                    "amount": float(parcel),
                    "total_amount": float(total),
                    "total_installments": installments,
                    "end_date": add_months(
                        next_due_date,
                        remaining_count - 1,
                        due_day=due_day,
                    ).isoformat(),
                }
            )
    else:
        raise ValueError("Modalidade recorrente inválida.")

    response = (
        client.table("recurring_transactions")
        .update(payload)
        .eq("id", recurring_id)
        .eq("user_id", user_id)
        .execute()
    )
    updated_rows = response.data or []
    return updated_rows[0] if updated_rows else {**plan, **payload}


def set_recurring_active(user_id: str, recurring_id: str, active: bool) -> None:
    client = _client()
    row = (
        client.table("recurring_transactions")
        .select("schedule_type,total_installments,generated_installments")
        .eq("id", recurring_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
        .data
        or []
    )
    if not row:
        raise ValueError("Recorrência não encontrada.")
    plan = row[0]
    if active and plan.get("schedule_type") == SCHEDULE_INSTALLMENTS:
        total = int(plan.get("total_installments") or 0)
        generated = int(plan.get("generated_installments") or 0)
        if total and generated >= total:
            raise ValueError("Este parcelamento já foi concluído.")

    client.table("recurring_transactions").update({"is_active": bool(active)}).eq("id", recurring_id).eq(
        "user_id", user_id
    ).execute()
