from __future__ import annotations

import calendar
import re
from datetime import date
from typing import Any

from src.cash_projection import build_cash_projection, projection_insights
from src.data import brl
from src.recurring_finance import (
    SCHEDULE_FIXED,
    SCHEDULE_INSTALLMENTS,
    create_recurring_plan,
)


_NUMBER_WORDS = {
    "um": 1,
    "uma": 1,
    "dois": 2,
    "duas": 2,
    "tres": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "oito": 8,
    "nove": 9,
    "dez": 10,
    "onze": 11,
    "doze": 12,
    "treze": 13,
    "quatorze": 14,
    "catorze": 14,
    "quinze": 15,
    "dezesseis": 16,
    "dezessete": 17,
    "dezoito": 18,
    "dezenove": 19,
    "vinte": 20,
    "trinta": 30,
    "quarenta": 40,
    "cinquenta": 50,
    "sessenta": 60,
}


def _parse_pt_number(value: str) -> int | None:
    token = value.strip().lower().replace("ê", "e")
    if token.isdigit():
        return int(token)
    if token in _NUMBER_WORDS:
        return _NUMBER_WORDS[token]
    parts = [part.strip() for part in token.split(" e ") if part.strip()]
    if len(parts) == 2 and all(part in _NUMBER_WORDS for part in parts):
        result = _NUMBER_WORDS[parts[0]] + _NUMBER_WORDS[parts[1]]
        return result if 1 <= result <= 360 else None
    return None


def _extract_count(normalized: str) -> int | None:
    word = r"(?:\d{1,3}|um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|treze|quatorze|catorze|quinze|dezesseis|dezessete|dezoito|dezenove|vinte(?:\s+e\s+(?:um|dois|tres|quatro|cinco|seis|sete|oito|nove))?|trinta(?:\s+e\s+(?:um|dois|tres|quatro|cinco|seis|sete|oito|nove))?|quarenta(?:\s+e\s+(?:um|dois|tres|quatro|cinco|seis|sete|oito|nove))?|cinquenta(?:\s+e\s+(?:um|dois|tres|quatro|cinco|seis|sete|oito|nove))?|sessenta)"
    patterns = [
        rf"\bem\s+({word})\s*(?:x|vezes|parcelas?)\b",
        rf"\b({word})\s*(?:x|vezes|parcelas?)\b",
        rf"\bdurante\s+({word})\s+mes(?:es)?\b",
        rf"\bpor\s+({word})\s+mes(?:es)?\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            parsed = _parse_pt_number(match.group(1))
            if parsed and 1 <= parsed <= 360:
                return parsed
    return None


def _money_values(text: str) -> list[float]:
    values: list[float] = []
    for raw in re.findall(r"(?:r\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)", text, flags=re.I):
        try:
            value = float(raw.replace(".", "").replace(",", "."))
        except ValueError:
            continue
        if value > 0:
            values.append(value)
    return values


def _extract_financial_amount(text: str, normalized: str, count: int | None) -> tuple[float | None, bool]:
    """Retorna valor e se ele representa valor por parcela/mês."""
    # Padrões explícitos "10 parcelas de 500" / "R$ 900 por mês" têm prioridade.
    per_cycle_patterns = [
        r"(?:parcelas?|vezes)\s+de\s+(?:r\$\s*)?(\d[\d.,]*)",
        r"(?:r\$\s*)?(\d[\d.,]*)\s+(?:por|ao)\s+m[eê]s",
        r"(?:r\$\s*)?(\d[\d.,]*)\s+mensais?",
    ]
    for pattern in per_cycle_patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            raw = match.group(1)
            try:
                return float(raw.replace(".", "").replace(",", ".")), True
            except ValueError:
                pass

    values = _money_values(text)
    if not values:
        return None, False

    # Evita interpretar quantidade de parcelas/dia como dinheiro quando houver R$ explícito.
    explicit_money = re.findall(r"r\$\s*(\d[\d.,]*)", text, flags=re.I)
    if explicit_money:
        try:
            return float(explicit_money[0].replace(".", "").replace(",", ".")), False
        except ValueError:
            pass

    return values[0], False


def _next_monthly_date(normalized: str, original: str) -> date:
    today = date.today()

    # Data completa informada: respeita exatamente a data do usuário.
    full = re.search(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b", original)
    if full:
        day = int(full.group(1))
        month = int(full.group(2))
        year = int(full.group(3)) if full.group(3) else today.year
        if year < 100:
            year += 2000
        try:
            return date(year, month, day)
        except ValueError:
            pass

    if "amanha" in normalized:
        from datetime import timedelta
        return today + timedelta(days=1)
    if "hoje" in normalized:
        return today

    match = re.search(r"\bdia\s+(\d{1,2})\b", normalized)
    if not match:
        return today

    preferred_day = min(max(int(match.group(1)), 1), 31)
    current_day = min(preferred_day, calendar.monthrange(today.year, today.month)[1])
    candidate = date(today.year, today.month, current_day)
    if candidate >= today:
        return candidate

    absolute = today.year * 12 + today.month
    year = absolute // 12
    month = absolute % 12 + 1
    day = min(preferred_day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _is_income(normalized: str) -> bool:
    income_terms = [
        "receber", "vou receber", "receita", "entrada", "salario", "salário",
        "aluguel recebido", "cliente vai pagar", "pagamento do cliente", "venda parcelada",
        "faturamento", "comissao", "comissão",
    ]
    expense_terms = [
        "pagar", "conta", "despesa", "comprei", "compra", "aluguel", "pensao", "pensão",
        "internet", "energia", "parcela", "financiamento", "emprestimo", "empréstimo",
    ]
    income_score = sum(term in normalized for term in income_terms)
    expense_score = sum(term in normalized for term in expense_terms)
    if "receita" in normalized or "vou receber" in normalized or "receber" in normalized:
        return True
    return income_score > expense_score


def _looks_recurring(normalized: str) -> bool:
    terms = [
        "todo mes", "todo mês", "mensal", "mensalmente", "todo dia", "fixa mensal",
        "conta fixa", "receita fixa", "parcelad", "parcelas", " vezes", "x de ",
        "durante", "por mes", "por mês",
    ]
    return any(term in normalized for term in terms)


def _is_installment(normalized: str) -> bool:
    return bool(
        re.search(r"\b\d{1,3}\s*x\b", normalized)
        or any(term in normalized for term in ["parcelad", "parcelas", " vezes", "durante"])
    )


def _projection_horizon(normalized: str) -> int:
    match = re.search(r"(?:proximos?|pr[oó]ximos?|por|em)\s+(\d{1,2})\s+mes", normalized)
    if match:
        return max(1, min(int(match.group(1)), 60))
    count = _extract_count(normalized)
    if count:
        return max(1, min(count, 60))
    return 12


def _projection_requested(normalized: str) -> bool:
    return any(term in normalized for term in [
        "projecao de caixa", "projeção de caixa", "projetar caixa", "projete meu caixa",
        "como fica meu caixa", "caixa nos proximos", "caixa nos próximos", "previsao de caixa",
        "previsão de caixa", "saldo futuro", "saldo projetado",
    ])


def _recurring_reply(ai_module, user_id: str, message: str, bundle: dict[str, Any]):
    normalized = ai_module._norm(message)
    if not _looks_recurring(normalized):
        return None

    accounts = bundle.get("accounts")
    categories = bundle.get("categories")
    if accounts is None or accounts.empty:
        return ai_module.AIReply("Cadastre uma conta financeira antes de criar uma conta ou receita automática.")

    preferences = ai_module._preference_map(user_id)
    account_id, account_name = ai_module._pick_preferred_account(accounts, message, preferences)
    if not account_id:
        return ai_module.AIReply("Não encontrei uma conta disponível para este lançamento.")

    kind = "receita" if _is_income(normalized) else "despesa"
    category_id, category_name = ai_module._infer_preferred_category(message, categories, preferences)

    installment = _is_installment(normalized)
    count = _extract_count(normalized) if installment else None
    value, value_is_per_cycle = _extract_financial_amount(message, normalized, count)

    if value is None:
        return ai_module._ask_for_missing(
            "Qual é o valor? Pode informar, por exemplo, **R$ 630 por mês** ou **R$ 2.400 em 12 vezes**.",
            message,
            "recurring_finance",
        )

    if installment and not count:
        return ai_module._ask_for_missing(
            "Em quantas parcelas ou por quantos meses?",
            message,
            "recurring_finance",
        )

    first_due = _next_monthly_date(normalized, message)
    fallback = "Receita automática" if kind == "receita" else "Conta automática"
    description = ai_module._description(message, fallback)

    if installment:
        assert count is not None
        total_amount = value * count if value_is_per_cycle else value
        created = create_recurring_plan(
            user_id,
            account_id=account_id,
            category_id=category_id,
            kind=kind,
            description=description,
            schedule_type=SCHEDULE_INSTALLMENTS,
            first_due_date=first_due,
            total_amount=total_amount,
            total_installments=count,
        )
        monthly = float(created.get("amount") or (total_amount / count))
        icon = "📥" if kind == "receita" else "🧾"
        verb = "a receber" if kind == "receita" else "a pagar"
        text = (
            f"{icon} **{description}** cadastrada como {kind} parcelada.\n\n"
            f"Total: **{brl(total_amount)}** · {count} parcela(s) de aproximadamente **{brl(monthly)}**\n\n"
            f"Primeira parcela: **{first_due.strftime('%d/%m/%Y')}** · Conta: **{account_name}** · "
            f"Categoria: **{category_name}**.\n\n"
            f"Vou considerar automaticamente as parcelas {verb} na projeção de caixa e encerrar após a última."
        )
        payload = {
            "description": description,
            "kind": kind,
            "schedule_type": SCHEDULE_INSTALLMENTS,
            "total_amount": total_amount,
            "total_installments": count,
            "first_due_date": first_due.isoformat(),
            "account_id": account_id,
            "category_id": category_id,
        }
    else:
        created = create_recurring_plan(
            user_id,
            account_id=account_id,
            category_id=category_id,
            kind=kind,
            description=description,
            schedule_type=SCHEDULE_FIXED,
            first_due_date=first_due,
            monthly_amount=value,
        )
        icon = "💰" if kind == "receita" else "🔁"
        action = "receber" if kind == "receita" else "pagar"
        text = (
            f"{icon} **{description}** cadastrada como {kind} fixa mensal de **{brl(value)}**.\n\n"
            f"Próximo dia para {action}: **{first_due.strftime('%d/%m/%Y')}** · Conta: **{account_name}** · "
            f"Categoria: **{category_name}**.\n\n"
            "Ela continuará entrando automaticamente no planejamento mensal até você pedir para pausar."
        )
        payload = {
            "description": description,
            "kind": kind,
            "schedule_type": SCHEDULE_FIXED,
            "monthly_amount": value,
            "first_due_date": first_due.isoformat(),
            "account_id": account_id,
            "category_id": category_id,
        }

    ai_module.log_ai_action(user_id, message, "create_recurring_plan", payload, "executed", text)
    return ai_module.AIReply(text=text, executed=True)


def _projection_reply(ai_module, user_id: str, message: str, bundle: dict[str, Any]):
    normalized = ai_module._norm(message)
    if not _projection_requested(normalized):
        return None

    months = _projection_horizon(normalized)
    projection, summary = build_cash_projection(
        accounts=bundle.get("accounts"),
        transactions=bundle.get("transactions"),
        recurring=bundle.get("recurring"),
        months=months,
    )
    insights = projection_insights(summary)

    level = str(summary.get("nivel_risco") or "estável")
    first_negative = summary.get("primeiro_mes_negativo")
    risk_text = (
        f"Primeiro mês negativo: **{first_negative}**."
        if first_negative
        else "Nenhum mês negativo foi projetado nesse período."
    )

    text = (
        f"📈 **Projeção de caixa — {months} meses**\n\n"
        f"Saldo atual: **{brl(float(summary.get('saldo_atual') or 0))}**\n\n"
        f"Receitas previstas: **{brl(float(summary.get('receitas_previstas') or 0))}**\n\n"
        f"Despesas previstas: **{brl(float(summary.get('despesas_previstas') or 0))}**\n\n"
        f"Saldo projetado ao final: **{brl(float(summary.get('saldo_final') or 0))}**\n\n"
        f"Nível de risco: **{level.upper()}** · {risk_text}"
    )

    if insights:
        top = insights[0]
        text += (
            f"\n\n🧭 **{top.get('title', 'Análise automática')}**\n"
            f"{top.get('message', '')}\n\n"
            f"**Ação recomendada:** {top.get('action', '')}"
        )

    ai_module.log_ai_action(
        user_id,
        message,
        "cash_projection_analysis",
        {"months": months},
        "analysis",
        text,
    )
    return ai_module.AIReply(text=text)


def install_recurring_ai_runtime(ai_module) -> None:
    """Adiciona contas/receitas recorrentes e projeção ao chat sem quebrar o motor legado."""
    if getattr(ai_module, "_renova_recurring_ai_runtime_installed", False):
        return

    original_process_message = ai_module.process_message

    def process_message_with_recurring(user_id: str, message: str, bundle: dict[str, Any]):
        projection = _projection_reply(ai_module, user_id, message, bundle)
        if projection is not None:
            return projection

        recurring = _recurring_reply(ai_module, user_id, message, bundle)
        if recurring is not None:
            return recurring

        return original_process_message(user_id, message, bundle)

    ai_module.process_message = process_message_with_recurring
    ai_module._renova_recurring_ai_runtime_installed = True
