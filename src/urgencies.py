from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta
from typing import Any

import pandas as pd


SEVERITY_META = {
    "critica": {"label": "CRÍTICA", "icon": "🚨", "score": 100},
    "alta": {"label": "ALTA", "icon": "⚠️", "score": 70},
    "media": {"label": "MÉDIA", "icon": "🟡", "score": 40},
    "info": {"label": "INFO", "icon": "🔎", "score": 10},
}


def _money(value: float) -> str:
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _as_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if value is None or value is pd.NaT:
        return None
    try:
        parsed = pd.to_datetime(value)
        if pd.isna(parsed):
            return None
        return parsed.date()
    except Exception:
        return None


def _next_due_date(reference: date, due_day: int) -> date:
    due_day = max(1, min(int(due_day or 1), 31))

    def build(year: int, month: int) -> date:
        last_day = monthrange(year, month)[1]
        return date(year, month, min(due_day, last_day))

    candidate = build(reference.year, reference.month)
    if candidate >= reference:
        return candidate

    if reference.month == 12:
        return build(reference.year + 1, 1)
    return build(reference.year, reference.month + 1)


def _alert(
    key: str,
    severity: str,
    title: str,
    message: str,
    action: str,
    *,
    source: str,
    amount: float | None = None,
    due_date: date | None = None,
    extra_score: int = 0,
) -> dict[str, Any]:
    meta = SEVERITY_META[severity]
    return {
        "key": key,
        "severity": severity,
        "severity_label": meta["label"],
        "icon": meta["icon"],
        "score": int(meta["score"]) + int(extra_score),
        "title": title,
        "message": message,
        "action": action,
        "source": source,
        "amount": amount,
        "due_date": due_date,
    }


def analyze_financial_urgencies(
    *,
    transactions: pd.DataFrame | None,
    accounts: pd.DataFrame | None,
    budgets: pd.DataFrame | None,
    cards: pd.DataFrame | None,
    reference_date: date | None = None,
) -> list[dict[str, Any]]:
    """Analisa sinais financeiros operacionais e devolve alertas priorizados."""
    today = reference_date or date.today()
    tx = transactions.copy() if transactions is not None else pd.DataFrame()
    acc = accounts.copy() if accounts is not None else pd.DataFrame()
    bgt = budgets.copy() if budgets is not None else pd.DataFrame()
    crd = cards.copy() if cards is not None else pd.DataFrame()
    alerts: list[dict[str, Any]] = []

    # 1. Saldos negativos por conta e saldo consolidado.
    if not acc.empty and "saldo" in acc.columns:
        acc["_saldo"] = pd.to_numeric(acc["saldo"], errors="coerce").fillna(0.0)
        for _, row in acc[acc["_saldo"] < 0].iterrows():
            balance = float(row["_saldo"])
            name = str(row.get("conta") or "Conta")
            alerts.append(
                _alert(
                    f"negative-account:{row.get('id', name)}",
                    "critica",
                    f"Saldo negativo em {name}",
                    f"A conta está em {_money(balance)}.",
                    "Priorize entradas nessa conta ou reduza despesas imediatas.",
                    source="conta",
                    amount=abs(balance),
                    extra_score=min(30, int(abs(balance) // 100)),
                )
            )

        total_balance = float(acc["_saldo"].sum())
        if total_balance < 0:
            alerts.append(
                _alert(
                    "negative-total-balance",
                    "critica",
                    "Saldo consolidado negativo",
                    f"O saldo total das contas está em {_money(total_balance)}.",
                    "Revise despesas abertas e concentre recursos nas obrigações essenciais.",
                    source="saldo",
                    amount=abs(total_balance),
                    extra_score=25,
                )
            )
    else:
        total_balance = 0.0

    # 2. Contas vencidas e vencimentos nos próximos 7 dias.
    upcoming_total = 0.0
    required = {"tipo", "data", "status", "valor"}
    if not tx.empty and required.issubset(tx.columns):
        tx["_data"] = tx["data"].map(_as_date)
        if "vencimento" in tx.columns:
            tx["_vencimento"] = tx["vencimento"].map(_as_date)
        else:
            tx["_vencimento"] = None
        tx["_status"] = tx["status"].astype(str).str.lower().str.strip()
        tx["_valor"] = pd.to_numeric(tx["valor"], errors="coerce").fillna(0.0)
        expenses = tx[tx["tipo"].astype(str).str.lower().eq("despesa")].copy()
        open_expenses = expenses[~expenses["_status"].isin(["pago", "cancelado", "cancelada"])].copy()

        for _, row in open_expenses.iterrows():
            due = row.get("_vencimento")
            # Só usamos a data do lançamento como fallback quando o registro já
            # foi explicitamente marcado como atrasado. Para uma despesa apenas
            # prevista sem vencimento, não inventamos uma data de cobrança.
            if not isinstance(due, date) and row.get("_status") == "atrasado":
                due = row.get("_data")
            if not isinstance(due, date):
                continue

            amount = float(row["_valor"])
            description = str(row.get("descricao") or "Despesa")
            days = (due - today).days

            if days < 0 or row.get("_status") == "atrasado":
                overdue_days = max(1, abs(days))
                alerts.append(
                    _alert(
                        f"overdue:{row.get('id', description)}",
                        "critica",
                        f"Conta atrasada: {description}",
                        f"{_money(amount)} está pendente há {overdue_days} dia(s).",
                        "Quite, renegocie ou atualize o status deste lançamento.",
                        source="lancamento",
                        amount=amount,
                        due_date=due,
                        extra_score=min(35, overdue_days),
                    )
                )
            elif 0 <= days <= 7:
                upcoming_total += amount
                severity = "alta" if days <= 2 else "media"
                when = "vence hoje" if days == 0 else f"vence em {days} dia(s)"
                alerts.append(
                    _alert(
                        f"due-soon:{row.get('id', description)}",
                        severity,
                        f"Vencimento próximo: {description}",
                        f"{_money(amount)} {when}.",
                        "Reserve saldo para o pagamento e marque como pago após a quitação.",
                        source="lancamento",
                        amount=amount,
                        due_date=due,
                        extra_score=max(0, 8 - days),
                    )
                )

        # 3. Crescimento anormal de despesas contra o mês anterior.
        paid_or_open = expenses[~expenses["_status"].isin(["cancelado", "cancelada"])].copy()
        if not paid_or_open.empty:
            current_start = today.replace(day=1)
            previous_end = current_start - timedelta(days=1)
            previous_start = previous_end.replace(day=1)

            current_total = float(
                paid_or_open.loc[
                    paid_or_open["_data"].map(lambda d: isinstance(d, date) and current_start <= d <= today),
                    "_valor",
                ].sum()
            )
            previous_total = float(
                paid_or_open.loc[
                    paid_or_open["_data"].map(
                        lambda d: isinstance(d, date) and previous_start <= d <= previous_end
                    ),
                    "_valor",
                ].sum()
            )
            if previous_total >= 100 and current_total >= previous_total * 1.35 and (current_total - previous_total) >= 100:
                growth = ((current_total / previous_total) - 1) * 100
                alerts.append(
                    _alert(
                        "expense-growth",
                        "media",
                        "Despesas cresceram acima do padrão",
                        f"Neste mês já foram {_money(current_total)}, cerca de {growth:.0f}% acima do mês anterior.",
                        "Revise as maiores categorias antes de assumir novas despesas.",
                        source="analise",
                        amount=current_total - previous_total,
                    )
                )

    # 4. Cobertura de caixa para vencimentos próximos.
    if upcoming_total > 0 and upcoming_total > max(total_balance, 0.0):
        shortfall = upcoming_total - max(total_balance, 0.0)
        alerts.append(
            _alert(
                "cash-coverage",
                "critica",
                "Saldo pode não cobrir os próximos vencimentos",
                f"Há {_money(upcoming_total)} vencendo em até 7 dias e uma diferença estimada de {_money(shortfall)}.",
                "Planeje uma entrada, renegociação ou corte antes dos vencimentos.",
                source="fluxo_caixa",
                amount=shortfall,
                extra_score=20,
            )
        )

    # 5. Orçamentos próximos/acima do limite.
    if not bgt.empty and {"orcamento", "realizado"}.issubset(bgt.columns):
        for _, row in bgt.iterrows():
            planned = _safe_float(row.get("orcamento"))
            spent = _safe_float(row.get("realizado"))
            if planned <= 0:
                continue
            usage = (spent / planned) * 100
            category = str(row.get("categoria") or "Categoria")
            if usage >= 100:
                alerts.append(
                    _alert(
                        f"budget-over:{row.get('id', category)}",
                        "alta",
                        f"Orçamento estourado: {category}",
                        f"Uso de {usage:.0f}% — {_money(spent)} de {_money(planned)}.",
                        "Suspenda gastos não essenciais nessa categoria ou ajuste o orçamento conscientemente.",
                        source="orcamento",
                        amount=max(0.0, spent - planned),
                        extra_score=min(20, int(usage - 100)),
                    )
                )
            elif usage >= 85:
                alerts.append(
                    _alert(
                        f"budget-near:{row.get('id', category)}",
                        "media",
                        f"Orçamento quase no limite: {category}",
                        f"Você já utilizou {usage:.0f}% — {_money(spent)} de {_money(planned)}.",
                        "Reduza novas despesas nessa categoria até o fechamento do mês.",
                        source="orcamento",
                    )
                )

    # 6. Cartões: utilização de limite e vencimento da fatura.
    if not crd.empty:
        for _, row in crd.iterrows():
            name = str(row.get("cartao") or "Cartão")
            limit_value = _safe_float(row.get("limite"))
            invoice = _safe_float(row.get("fatura"))
            card_id = row.get("id", name)

            if limit_value > 0 and invoice > 0:
                usage = (invoice / limit_value) * 100
                if usage >= 90:
                    alerts.append(
                        _alert(
                            f"card-limit-high:{card_id}",
                            "alta",
                            f"Limite do cartão {name} em atenção",
                            f"A fatura usa {usage:.0f}% do limite ({_money(invoice)} de {_money(limit_value)}).",
                            "Evite novas compras até reduzir a utilização do limite.",
                            source="cartao",
                            amount=invoice,
                            extra_score=min(15, int(max(0, usage - 90))),
                        )
                    )
                elif usage >= 75:
                    alerts.append(
                        _alert(
                            f"card-limit-medium:{card_id}",
                            "media",
                            f"Cartão {name} acima de 75% do limite",
                            f"Utilização atual: {usage:.0f}% ({_money(invoice)}).",
                            "Acompanhe novas compras para não pressionar o próximo fechamento.",
                            source="cartao",
                            amount=invoice,
                        )
                    )

            if invoice > 0 and row.get("vencimento"):
                due = _next_due_date(today, int(row.get("vencimento") or 1))
                days = (due - today).days
                if days <= 5:
                    severity = "alta" if days <= 2 else "media"
                    when = "vence hoje" if days == 0 else f"vence em {days} dia(s)"
                    alerts.append(
                        _alert(
                            f"card-due:{card_id}:{due.isoformat()}",
                            severity,
                            f"Fatura próxima do vencimento: {name}",
                            f"A fatura de {_money(invoice)} {when}.",
                            "Garanta saldo disponível para pagar a fatura no vencimento.",
                            source="cartao",
                            amount=invoice,
                            due_date=due,
                            extra_score=max(0, 6 - days),
                        )
                    )

    alerts.sort(
        key=lambda item: (
            -int(item.get("score") or 0),
            item.get("due_date") or date.max,
            -float(item.get("amount") or 0),
            str(item.get("title") or ""),
        )
    )
    return alerts


def urgency_summary(alerts: list[dict[str, Any]]) -> dict[str, int]:
    summary = {"total": len(alerts), "critica": 0, "alta": 0, "media": 0, "info": 0}
    for item in alerts:
        severity = str(item.get("severity") or "info")
        if severity in summary:
            summary[severity] += 1
    return summary
