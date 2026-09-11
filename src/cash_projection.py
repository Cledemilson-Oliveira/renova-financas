from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal
from typing import Any

import pandas as pd

from src.recurring_finance import SCHEDULE_FIXED, SCHEDULE_INSTALLMENTS, add_months


def _month_start(value: date) -> date:
    return value.replace(day=1)


def _month_end(value: date) -> date:
    return date(value.year, value.month, calendar.monthrange(value.year, value.month)[1])


def _as_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def _month_label(value: date) -> str:
    months = [
        "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
        "Jul", "Ago", "Set", "Out", "Nov", "Dez",
    ]
    return f"{months[value.month - 1]}/{str(value.year)[2:]}"


def _last_installment_amount(row: pd.Series, installment_number: int) -> float:
    base = Decimal(str(row.get("valor_ciclo") or row.get("amount") or 0))
    total_installments = int(row.get("parcelas_total") or row.get("total_installments") or 0)
    total_amount = row.get("valor_total")
    if total_amount is None or pd.isna(total_amount) or not total_installments:
        return float(base)
    if installment_number != total_installments:
        return float(base)
    total = Decimal(str(total_amount))
    last = total - base * Decimal(max(total_installments - 1, 0))
    return float(last if last > 0 else base)


def build_cash_projection(
    *,
    accounts: pd.DataFrame,
    transactions: pd.DataFrame,
    recurring: pd.DataFrame,
    months: int = 12,
    today: date | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Projeta caixa futuro usando saldo pago + compromissos previstos + recorrências."""
    today = today or date.today()
    months = max(1, min(int(months), 60))
    first_month = _month_start(today)
    month_keys = [add_months(first_month, index, due_day=1) for index in range(months)]
    last_day = _month_end(month_keys[-1])

    rows: dict[date, dict[str, Any]] = {
        month: {
            "mes": month,
            "periodo": _month_label(month),
            "receitas_previstas": 0.0,
            "despesas_previstas": 0.0,
            "avulsas_previstas": 0.0,
            "recorrentes_previstas": 0.0,
        }
        for month in month_keys
    }

    starting_balance = 0.0
    if accounts is not None and not accounts.empty and "saldo" in accounts.columns:
        starting_balance = float(pd.to_numeric(accounts["saldo"], errors="coerce").fillna(0).sum())

    # O saldo atual já considera lançamentos pagos. Portanto, só entram na
    # projeção os lançamentos ainda previstos/atrasados.
    if transactions is not None and not transactions.empty:
        for _, tx in transactions.iterrows():
            status = str(tx.get("status_db") or tx.get("status") or "").lower()
            if status in {"pago", "cancelado", "cancelada"}:
                continue
            kind = str(tx.get("tipo") or "").lower()
            if kind not in {"receita", "despesa"}:
                continue
            target_date = _as_date(tx.get("vencimento")) or _as_date(tx.get("data"))
            if target_date is None:
                continue
            if target_date < today:
                target_month = first_month
            else:
                target_month = _month_start(target_date)
            if target_month not in rows:
                continue
            value = float(tx.get("valor") or 0)
            if kind == "receita":
                rows[target_month]["receitas_previstas"] += value
            else:
                rows[target_month]["despesas_previstas"] += value
            rows[target_month]["avulsas_previstas"] += value

    fixed_monthly_expenses = 0.0
    fixed_monthly_income = 0.0
    installment_expense_remaining = 0.0
    installment_income_remaining = 0.0

    if recurring is not None and not recurring.empty:
        for _, plan in recurring.iterrows():
            if not bool(plan.get("ativo", plan.get("is_active", False))):
                continue
            kind = str(plan.get("kind") or "")
            if kind not in {"receita", "despesa"}:
                continue
            schedule_type = str(plan.get("schedule_type") or SCHEDULE_FIXED)
            due = _as_date(plan.get("proximo_vencimento")) or _as_date(plan.get("next_due_date"))
            if due is None:
                continue
            due_day = int(plan.get("due_day") or due.day)
            base_amount = float(plan.get("valor_ciclo") or plan.get("amount") or 0)

            if schedule_type == SCHEDULE_FIXED:
                if kind == "despesa":
                    fixed_monthly_expenses += base_amount
                else:
                    fixed_monthly_income += base_amount

                cursor = due
                while cursor <= last_day:
                    target_month = _month_start(cursor)
                    if target_month in rows:
                        if kind == "receita":
                            rows[target_month]["receitas_previstas"] += base_amount
                        else:
                            rows[target_month]["despesas_previstas"] += base_amount
                        rows[target_month]["recorrentes_previstas"] += base_amount
                    cursor = add_months(cursor, 1, due_day=due_day)
                continue

            total_installments = int(plan.get("parcelas_total") or plan.get("total_installments") or 0)
            generated = int(plan.get("parcelas_geradas") or plan.get("generated_installments") or 0)
            remaining = max(total_installments - generated, 0)
            if remaining <= 0:
                continue

            remaining_total = 0.0
            cursor = due
            for offset in range(remaining):
                installment_number = generated + offset + 1
                amount = _last_installment_amount(plan, installment_number)
                remaining_total += amount
                if cursor <= last_day:
                    target_month = _month_start(cursor)
                    if target_month in rows:
                        if kind == "receita":
                            rows[target_month]["receitas_previstas"] += amount
                        else:
                            rows[target_month]["despesas_previstas"] += amount
                        rows[target_month]["recorrentes_previstas"] += amount
                cursor = add_months(cursor, 1, due_day=due_day)

            if kind == "despesa":
                installment_expense_remaining += remaining_total
            else:
                installment_income_remaining += remaining_total

    cumulative = starting_balance
    output: list[dict[str, Any]] = []
    first_negative: date | None = None
    minimum_balance = starting_balance

    for month in month_keys:
        item = rows[month]
        income = float(item["receitas_previstas"])
        expense = float(item["despesas_previstas"])
        net = income - expense
        cumulative += net
        minimum_balance = min(minimum_balance, cumulative)
        if cumulative < 0 and first_negative is None:
            first_negative = month
        output.append(
            {
                **item,
                "resultado_previsto": net,
                "saldo_projetado": cumulative,
            }
        )

    frame = pd.DataFrame(output)
    total_income = float(frame["receitas_previstas"].sum()) if not frame.empty else 0.0
    total_expense = float(frame["despesas_previstas"].sum()) if not frame.empty else 0.0
    final_balance = float(frame.iloc[-1]["saldo_projetado"]) if not frame.empty else starting_balance
    negative_months = int((frame["saldo_projetado"] < 0).sum()) if not frame.empty else 0

    if first_negative:
        risk_level = "crítico"
    elif final_balance < starting_balance and total_expense > total_income:
        risk_level = "atenção"
    else:
        risk_level = "estável"

    summary = {
        "saldo_atual": starting_balance,
        "receitas_previstas": total_income,
        "despesas_previstas": total_expense,
        "saldo_final": final_balance,
        "saldo_minimo": minimum_balance,
        "primeiro_mes_negativo": first_negative,
        "meses_negativos": negative_months,
        "nivel_risco": risk_level,
        "despesas_fixas_mensais": fixed_monthly_expenses,
        "receitas_fixas_mensais": fixed_monthly_income,
        "parcelamentos_a_pagar": installment_expense_remaining,
        "parcelamentos_a_receber": installment_income_remaining,
    }
    return frame, summary


def projection_insights(summary: dict[str, Any]) -> list[dict[str, str]]:
    insights: list[dict[str, str]] = []
    first_negative = summary.get("primeiro_mes_negativo")
    if first_negative:
        insights.append(
            {
                "severity": "critica",
                "title": "Risco de caixa negativo",
                "message": f"A projeção indica saldo abaixo de zero a partir de {_month_label(first_negative)}.",
                "action": "Revise despesas, renegocie parcelas ou antecipe receitas antes desse mês.",
            }
        )
    else:
        insights.append(
            {
                "severity": "ok",
                "title": "Caixa permanece positivo",
                "message": "Com os compromissos cadastrados, o saldo projetado não fica negativo no horizonte analisado.",
                "action": "Continue cadastrando contas e receitas recorrentes para manter a projeção confiável.",
            }
        )

    fixed_expenses = float(summary.get("despesas_fixas_mensais") or 0)
    fixed_income = float(summary.get("receitas_fixas_mensais") or 0)
    if fixed_expenses > 0:
        coverage = (fixed_income / fixed_expenses * 100) if fixed_expenses else 0
        insights.append(
            {
                "severity": "info" if coverage >= 100 else "atencao",
                "title": "Cobertura das despesas fixas",
                "message": f"Receitas fixas cadastradas cobrem {coverage:.0f}% das despesas fixas mensais.",
                "action": "Use este indicador para definir a renda mínima necessária para manter o mês equilibrado.",
            }
        )

    installment_debt = float(summary.get("parcelamentos_a_pagar") or 0)
    if installment_debt > 0:
        insights.append(
            {
                "severity": "info",
                "title": "Parcelamentos futuros",
                "message": f"Ainda existem R$ {installment_debt:,.2f} comprometidos em parcelas futuras.".replace(",", "X").replace(".", ",").replace("X", "."),
                "action": "Evite assumir novas parcelas sem comparar com o saldo mínimo projetado.",
            }
        )
    return insights
