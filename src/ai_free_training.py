from __future__ import annotations

import re
from calendar import monthrange
from datetime import date, timedelta
from typing import Any

from src.data import brl
from src.repository import (
    create_financial_goal,
    create_recurring_transaction,
    create_transaction,
    create_transfer,
    log_ai_action,
    update_transaction,
    update_transaction_status,
    upsert_budget,
)
from src.urgencies import analyze_financial_urgencies


STANDARD_TRAINING_VERSION = "2026.09.11.1"

STANDARD_CAPABILITIES = (
    "registrar receitas",
    "registrar despesas pagas ou pendentes",
    "entender data de vencimento",
    "consultar saldo, receitas, despesas e resultado",
    "analisar urgências financeiras",
    "marcar contas como pagas",
    "corrigir lançamentos",
    "cancelar lançamentos com confirmação",
    "criar transferências entre contas",
    "criar metas e orçamentos",
    "criar lançamentos recorrentes",
)

_LEARNING_TERMS = (
    "quando eu disser",
    "aprenda que",
    "lembre que",
    "prefiro que",
    "sempre quero que",
    "use sempre a conta",
    "utilize sempre a conta",
    "memorize",
    "guarde como regra",
)

_ANALYSIS_TERMS = (
    "resumo",
    "situacao",
    "analisar",
    "analise",
    "como estao minhas financas",
    "saldo",
    "quanto tenho",
    "quanto gastei",
    "quanto recebi",
    "urgencia",
    "urgencias",
    "o que preciso pagar",
    "o que esta atrasado",
    "o que vence",
)


def standard_training_summary() -> str:
    return " · ".join(STANDARD_CAPABILITIES)


def _premium_training_reply(reply_type: Any) -> Any:
    return reply_type(
        text=(
            "🧠 A **IA Padrão gratuita** já sabe executar sua gestão financeira, mas não salva "
            "regras pessoais permanentes. O **Treinamento Personalizado** — preferências, "
            "vocabulário, regras próprias, PDFs e YouTube — é um recurso da assinatura RENOVA IA."
        )
    )


def _extract_standard_amount(message: str, norm_fn: Any) -> float | None:
    """Extrai valor financeiro sem confundir vencimento/data com dinheiro."""
    normalized = norm_fn(message)

    money_patterns = [
        r"r\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)",
        r"\bvalor\s+(?:de\s+)?(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)",
        r"\b(?:gastei|paguei|recebi|ganhei|faturei|vendi|comprei)\s+(?:r\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)",
        r"\b(?:despesa|receita|entrada|saida|cobranca)\s+(?:de\s+)?(?:r\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)",
    ]
    for pattern in money_patterns:
        match = re.search(pattern, normalized, flags=re.I)
        if match:
            try:
                value = float(match.group(1).replace(".", "").replace(",", "."))
                if value > 0:
                    return value
            except ValueError:
                pass

    # Fallback: ignora números que fazem parte de datas ou aparecem depois de "dia".
    date_spans = [m.span() for m in re.finditer(r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b", normalized)]
    for match in re.finditer(r"\b\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?|\b\d+(?:[.,]\d{1,2})?", normalized):
        if any(start <= match.start() < end for start, end in date_spans):
            continue
        before = normalized[max(0, match.start() - 18) : match.start()]
        if re.search(r"(?:dia|vence|vencimento|fechamento)\s*$", before):
            continue
        try:
            value = float(match.group(0).replace(".", "").replace(",", "."))
        except ValueError:
            continue
        if value > 0:
            return value
    return None


def _build_day_date(day: int, reference: date | None = None) -> date | None:
    today = reference or date.today()
    if not 1 <= day <= 31:
        return None

    def safe(year: int, month: int) -> date:
        return date(year, month, min(day, monthrange(year, month)[1]))

    candidate = safe(today.year, today.month)
    if candidate >= today:
        return candidate
    if today.month == 12:
        return safe(today.year + 1, 1)
    return safe(today.year, today.month + 1)


def _extract_due_date(message: str, norm_fn: Any) -> date | None:
    normalized = norm_fn(message)
    has_due_context = any(
        term in normalized
        for term in ("vence", "vencimento", "a pagar", "pagar ate", "pagar dia", "pendente")
    )
    if not has_due_context:
        return None

    if "vence hoje" in normalized or "vencimento hoje" in normalized:
        return date.today()
    if "vence amanha" in normalized or "vencimento amanha" in normalized:
        return date.today() + timedelta(days=1)

    explicit = re.search(
        r"(?:vence|vencimento|pagar(?:\s+ate)?|a pagar).*?\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b",
        normalized,
    )
    if explicit:
        day = int(explicit.group(1))
        month = int(explicit.group(2))
        year = int(explicit.group(3)) if explicit.group(3) else date.today().year
        if year < 100:
            year += 2000
        try:
            candidate = date(year, month, day)
            if not explicit.group(3) and candidate < date.today():
                candidate = date(year + 1, month, day)
            return candidate
        except ValueError:
            return None

    day_match = re.search(
        r"(?:vence|vencimento|pagar|a pagar)(?:\s+no)?(?:\s+dia)?\s+(\d{1,2})\b",
        normalized,
    )
    if day_match:
        return _build_day_date(int(day_match.group(1)))
    return None


def _clean_description(message: str, fallback: str, description_fn: Any) -> str:
    description = description_fn(message, fallback)
    description = re.sub(
        r"\b(?:vence|vencimento|pendente|previsto|a pagar|pagar ate|pagar dia|dia)\b",
        " ",
        description,
        flags=re.I,
    )
    description = re.sub(r"\s+", " ", description).strip(" .,-")
    return description[:120] or fallback


def _urgency_context(bundle: dict[str, Any]) -> str:
    alerts = analyze_financial_urgencies(
        transactions=bundle.get("transactions"),
        accounts=bundle.get("accounts"),
        budgets=bundle.get("budgets"),
        cards=bundle.get("cards"),
    )
    if not alerts:
        return "\n\n✅ Nenhuma urgência relevante foi detectada agora."

    lines = []
    for alert in alerts[:3]:
        lines.append(
            f"- {alert.get('icon', '🔎')} **{alert.get('title', 'Alerta')}**: "
            f"{alert.get('message', '')}"
        )
    return "\n\n**Prioridades detectadas**\n" + "\n".join(lines)


def process_standard_message(
    ai_finance_module: Any,
    user_id: str,
    message: str,
    bundle: dict[str, Any],
) -> Any:
    """Treinamento operacional fixo usado por contas gratuitas.

    Esta camada executa apenas regras padrão do produto e nunca lê/escreve memória
    personalizada do usuário. Treinamentos próprios continuam exclusivos do Premium.
    """
    reply_type = ai_finance_module.AIReply
    normalized = ai_finance_module._norm(message)
    accounts = bundle.get("accounts")
    categories = bundle.get("categories")
    goals = bundle.get("goals")
    tx = bundle.get("transactions")
    amount = _extract_standard_amount(message, ai_finance_module._norm)

    if any(term in normalized for term in _LEARNING_TERMS):
        return _premium_training_reply(reply_type)

    if any(term in normalized for term in _ANALYSIS_TERMS):
        text = ai_finance_module._summary_reply(bundle) + _urgency_context(bundle)
        log_ai_action(
            user_id,
            message,
            "standard_analysis",
            {"training_version": STANDARD_TRAINING_VERSION},
            "analysis",
            text,
        )
        return reply_type(text=text)

    # Cancelamentos/exclusões continuam exigindo confirmação explícita.
    if any(
        term in normalized
        for term in ("apagar", "excluir", "deletar", "remover lancamento", "cancelar lancamento", "cancele o lancamento")
    ):
        if tx is None or tx.empty:
            return reply_type("Não encontrei lançamentos para cancelar.")
        target = ai_finance_module._find_transaction_target(tx, message)
        if target is None:
            return ai_finance_module._ask_for_missing(
                "Qual lançamento você quer cancelar? Informe a descrição ou diga **último lançamento**.",
                message,
                "cancel_transaction",
            )
        payload = {
            "transaction_id": str(target["id"]),
            "new_status": "cancelado",
            "description": str(target["descricao"]),
        }
        text = (
            f"⚠️ Vou cancelar **{target['descricao']} — {brl(float(target['valor']))}**. "
            "Digite **CONFIRMAR** para executar ou **CANCELAR** para desistir."
        )
        log_ai_action(user_id, message, "standard_cancel_transaction", payload, "pending_confirmation", text)
        return reply_type(text=text, pending_confirmation=payload)

    if any(term in normalized for term in ("marcar como pago", "marque como pago", "dar baixa", "baixar conta", "ja paguei", "já paguei")):
        if tx is None or tx.empty:
            return reply_type("Não encontrei lançamentos para dar baixa.")
        target = ai_finance_module._find_transaction_target(tx, message)
        if target is None:
            return ai_finance_module._ask_for_missing(
                "Qual lançamento você quer marcar como pago?",
                message,
                "mark_paid",
            )
        update_transaction_status(user_id, str(target["id"]), "pago")
        text = f"✅ **{target['descricao']}** foi marcado como pago."
        log_ai_action(user_id, message, "standard_mark_paid", {"transaction_id": str(target["id"])}, "executed", text)
        return reply_type(text=text, executed=True)

    # Edições essenciais no plano gratuito.
    edit_terms = (
        "mudar o valor", "mude o valor", "alterar o valor", "altere o valor", "corrigir o valor",
        "mudar a data", "mude a data", "alterar a data", "altere a data",
        "mudar a categoria", "mude a categoria", "alterar a categoria", "altere a categoria",
        "mudar a conta", "mude a conta", "alterar a conta", "altere a conta",
        "mudar a descricao", "mude a descricao", "alterar a descricao", "altere a descricao",
        "mudar o vencimento", "mude o vencimento", "alterar o vencimento", "altere o vencimento",
    )
    if any(term in normalized for term in edit_terms):
        if tx is None or tx.empty:
            return reply_type("Não encontrei lançamentos para alterar.")
        target = ai_finance_module._find_transaction_target(tx, message)
        if target is None:
            return ai_finance_module._ask_for_missing(
                "Qual lançamento você quer alterar? Informe parte da descrição ou diga **último lançamento**.",
                message,
                "edit_transaction",
            )

        updates: dict[str, Any] = {}
        changes: list[str] = []
        if any(term in normalized for term in ("valor",)) and any(term in normalized for term in ("mudar", "mude", "alterar", "altere", "corrigir")):
            if amount is None:
                return ai_finance_module._ask_for_missing("Qual é o novo valor?", message, "edit_transaction")
            updates["amount"] = amount
            changes.append(f"valor → **{brl(amount)}**")

        if "vencimento" in normalized:
            due = _extract_due_date(message, ai_finance_module._norm)
            if due is None:
                return ai_finance_module._ask_for_missing(
                    "Qual é a nova data de vencimento? Ex.: **15/09/2026**.",
                    message,
                    "edit_transaction",
                )
            updates["due_date"] = due
            updates["status"] = "previsto"
            changes.append(f"vencimento → **{due.strftime('%d/%m/%Y')}**")
        elif "data" in normalized:
            occurred = ai_finance_module._extract_explicit_date(message)
            if occurred is None:
                return ai_finance_module._ask_for_missing("Qual é a nova data?", message, "edit_transaction")
            updates["occurred_on"] = occurred
            changes.append(f"data → **{occurred.strftime('%d/%m/%Y')}**")

        if "categoria" in normalized:
            category = ai_finance_module._find_explicit_category(categories, message)
            if category is None:
                return ai_finance_module._ask_for_missing(
                    "Qual é a nova categoria? Informe uma categoria cadastrada.",
                    message,
                    "edit_transaction",
                )
            updates["category_id"] = str(category["id"])
            changes.append(f"categoria → **{category['name']}**")

        if "conta" in normalized and not any(term in normalized for term in ("baixar conta", "conta atrasada")):
            account = ai_finance_module._find_explicit_account(accounts, message)
            if account is not None:
                updates["account_id"] = str(account["id"])
                changes.append(f"conta → **{account['conta']}**")

        if "descricao" in normalized:
            match = re.search(r"(?:descricao).*?(?:para|como)\s+(.+)$", normalized)
            if not match:
                return ai_finance_module._ask_for_missing("Qual é a nova descrição?", message, "edit_transaction")
            new_description = match.group(1).strip(" .,:;-")
            updates["description"] = new_description[:120]
            changes.append(f"descrição → **{new_description[:120]}**")

        if not updates:
            return ai_finance_module._ask_for_missing(
                "O que deseja alterar: **valor, data, vencimento, categoria, conta ou descrição**?",
                message,
                "edit_transaction",
            )
        update_transaction(user_id, str(target["id"]), **updates)
        text = f"✅ Lançamento **{target['descricao']}** atualizado.\n\n" + " · ".join(changes)
        log_ai_action(user_id, message, "standard_update_transaction", {"transaction_id": str(target["id"])}, "executed", text)
        return reply_type(text=text, executed=True)

    # Transferências.
    if any(term in normalized for term in ("transferir", "transferencia", "mover dinheiro", "mova dinheiro")):
        if amount is None:
            return ai_finance_module._ask_for_missing("Informe o valor da transferência.", message, "transfer")
        source, destination = ai_finance_module._pick_two_accounts(accounts, message)
        if source is None or destination is None:
            return reply_type("Cadastre pelo menos duas contas para fazer transferências.")
        occurred_on = ai_finance_module._extract_date(message)
        create_transfer(
            user_id,
            str(source["id"]),
            str(destination["id"]),
            _clean_description(message, "Transferência", ai_finance_module._description),
            amount,
            occurred_on,
        )
        text = f"🔄 Transferência de **{brl(amount)}** registrada de **{source['conta']}** para **{destination['conta']}**."
        log_ai_action(user_id, message, "standard_create_transfer", {"amount": amount}, "executed", text)
        return reply_type(text=text, executed=True)

    # Metas e orçamentos fazem parte da gestão essencial.
    if "orcamento" in normalized or "limite mensal" in normalized:
        if amount is None:
            return ai_finance_module._ask_for_missing("Informe o valor do orçamento mensal.", message, "budget")
        category_id, category_name = ai_finance_module._infer_category(message, categories)
        if not category_id:
            return reply_type("Não encontrei uma categoria para esse orçamento.")
        upsert_budget(user_id, category_id, date.today().replace(day=1), amount)
        text = f"✅ Orçamento de **{category_name}** definido em **{brl(amount)}** para este mês."
        log_ai_action(user_id, message, "standard_upsert_budget", {"category_id": category_id, "amount": amount}, "executed", text)
        return reply_type(text=text, executed=True)

    if "meta" in normalized or "juntar" in normalized or "economizar" in normalized:
        if amount is None:
            return ai_finance_module._ask_for_missing("Informe o valor da meta.", message, "goal_create")
        name = _clean_description(message, "Meta financeira", ai_finance_module._description)
        create_financial_goal(user_id, name, amount, None)
        text = f"🎯 Meta criada: **{name} — {brl(amount)}**."
        log_ai_action(user_id, message, "standard_create_goal", {"name": name, "target_amount": amount}, "executed", text)
        return reply_type(text=text, executed=True)

    recurring = any(term in normalized for term in ("recorrente", "todo mes", "mensalmente", "todo ano", "anualmente", "semanalmente"))
    is_income = any(term in normalized for term in ("recebi", "ganhei", "receita", "entrada", "vendi", "faturei", "salario"))
    is_expense = any(term in normalized for term in ("gastei", "paguei", "despesa", "saida", "comprei", "cobranca", "conta de"))

    if recurring and (is_income or is_expense):
        if amount is None:
            return ai_finance_module._ask_for_missing("Informe o valor do lançamento recorrente.", message, "recurring_transaction")
        account_id, account_name = ai_finance_module._pick_account(accounts, message)
        category_id, category_name = ai_finance_module._infer_category(message, categories)
        if not account_id:
            return reply_type("Cadastre uma conta antes de criar lançamentos.")
        kind = "receita" if is_income and not is_expense else "despesa"
        description = _clean_description(message, "Receita recorrente" if kind == "receita" else "Despesa recorrente", ai_finance_module._description)
        frequency = "anual" if "anual" in normalized or "todo ano" in normalized else "semanal" if "seman" in normalized else "quinzenal" if "quinzen" in normalized else "mensal"
        create_recurring_transaction(
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
            kind=kind,
            description=description,
            amount=amount,
            frequency=frequency,
            next_due_date=_extract_due_date(message, ai_finance_module._norm) or ai_finance_module._extract_date(message),
        )
        text = f"🔁 Lançamento recorrente criado: **{description} — {brl(amount)}** em **{account_name}**, categoria **{category_name}**."
        log_ai_action(user_id, message, "standard_create_recurring", {"description": description, "amount": amount, "kind": kind}, "executed", text)
        return reply_type(text=text, executed=True)

    # Receitas e despesas do dia a dia.
    if is_income or is_expense:
        if amount is None:
            return ai_finance_module._ask_for_missing("Qual é o valor?", message, "transaction")
        account_id, account_name = ai_finance_module._pick_account(accounts, message)
        category_id, category_name = ai_finance_module._infer_category(message, categories)
        if not account_id:
            return reply_type("Cadastre uma conta antes de criar lançamentos.")

        kind = "receita" if is_income and not is_expense else "despesa"
        description = _clean_description(message, "Receita" if kind == "receita" else "Despesa", ai_finance_module._description)
        occurred_on = ai_finance_module._extract_date(message)
        due_date = _extract_due_date(message, ai_finance_module._norm) if kind == "despesa" else None
        pending = kind == "despesa" and (
            due_date is not None
            or any(term in normalized for term in ("pendente", "a pagar", "previsto", "vou pagar", "preciso pagar"))
        )
        status = "previsto" if pending else "pago"

        create_transaction(
            user_id,
            account_id,
            category_id,
            kind,
            description,
            amount,
            occurred_on,
            due_date=due_date,
            status=status,
        )
        icon = "💰" if kind == "receita" else "💸"
        status_text = "Pendente" if status == "previsto" else "Pago"
        due_text = f" · Vencimento: **{due_date.strftime('%d/%m/%Y')}**" if due_date else ""
        text = (
            f"{icon} Lançamento registrado: **{description} — {brl(amount)}**\n\n"
            f"Conta: **{account_name}** · Categoria: **{category_name}** · "
            f"Situação: **{status_text}**{due_text}"
        )
        log_ai_action(
            user_id,
            message,
            "standard_create_transaction",
            {
                "description": description,
                "amount": amount,
                "kind": kind,
                "account_id": account_id,
                "category_id": category_id,
                "due_date": due_date.isoformat() if due_date else None,
                "status": status,
                "training_version": STANDARD_TRAINING_VERSION,
            },
            "executed",
            text,
        )
        return reply_type(text=text, executed=True)

    if tx is not None and not tx.empty:
        target = ai_finance_module._find_transaction_target(tx, message)
        if target is not None:
            return reply_type(
                text=(
                    f"Encontrei **{target['descricao']} — {brl(float(target['valor']))}**. "
                    "Você pode pedir para **marcar como pago, alterar, cancelar ou consultar suas finanças**."
                )
            )

    return reply_type(
        text=(
            "Posso cuidar da sua gestão financeira padrão. Você pode dizer, por exemplo: "
            "**‘gastei R$ 85 no mercado’**, **‘conta de luz R$ 180 vence dia 15’**, "
            "**‘recebi R$ 1.500’**, **‘marque a energia como paga’** ou **‘analise minhas finanças’**."
        )
    )
