from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from src.data import brl
from src.repository import (
    create_financial_goal,
    create_recurring_transaction,
    create_transaction,
    log_ai_action,
    upsert_budget,
    update_transaction_status,
)


@dataclass
class AIReply:
    text: str
    executed: bool = False
    pending_confirmation: dict[str, Any] | None = None


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", value.lower()).strip()


def _extract_amount(text: str) -> float | None:
    matches = re.findall(r"(?:r\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)", text, flags=re.I)
    if not matches:
        return None
    raw = matches[0].replace(".", "").replace(",", ".")
    try:
        value = float(raw)
        return value if value > 0 else None
    except ValueError:
        return None


def _extract_date(text: str) -> date:
    normalized = _norm(text)
    if "amanha" in normalized:
        return date.today() + timedelta(days=1)
    if "ontem" in normalized:
        return date.today() - timedelta(days=1)

    m = re.search(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b", text)
    if m:
        day, month = int(m.group(1)), int(m.group(2))
        year = int(m.group(3)) if m.group(3) else date.today().year
        if year < 100:
            year += 2000
        try:
            return date(year, month, day)
        except ValueError:
            pass
    return date.today()


def _infer_category(message: str, categories) -> tuple[str | None, str]:
    normalized = _norm(message)
    if categories is None or categories.empty:
        return None, "Sem categoria"

    mapping = {
        "Alimentação": ["mercado", "supermercado", "comida", "alimentacao", "restaurante", "lanche"],
        "Transporte": ["combustivel", "gasolina", "uber", "onibus", "transporte", "bicicleta"],
        "Moradia": ["aluguel", "casa", "energia", "luz", "agua", "condominio"],
        "Saúde": ["saude", "farmacia", "remedio", "medico"],
        "Educação": ["curso", "livro", "escola", "educacao"],
        "Família": ["familia", "pensao", "filho", "filha"],
        "Assinaturas": ["assinatura", "netflix", "internet", "spotify"],
        "Salário": ["salario", "pagamento", "holerite"],
        "Vendas": ["venda", "cliente"],
        "Serviços": ["servico", "freelance", "freela"],
    }

    names = {str(row["name"]): str(row["id"]) for _, row in categories.iterrows()}
    for name, words in mapping.items():
        if name in names and any(word in normalized for word in words):
            return names[name], name

    for _, row in categories.iterrows():
        name = str(row["name"])
        if _norm(name) in normalized:
            return str(row["id"]), name

    if "Outros" in names:
        return names["Outros"], "Outros"
    first = categories.iloc[0]
    return str(first["id"]), str(first["name"])


def _pick_account(accounts, message: str) -> tuple[str | None, str]:
    if accounts is None or accounts.empty:
        return None, "Conta principal"
    normalized = _norm(message)
    for _, row in accounts.iterrows():
        name = str(row["conta"])
        if _norm(name) in normalized:
            return str(row["id"]), name
    first = accounts.iloc[0]
    return str(first["id"]), str(first["conta"])


def _description(message: str, fallback: str) -> str:
    cleaned = re.sub(r"r\$\s*\d[\d.,]*", "", message, flags=re.I)
    cleaned = re.sub(r"\b\d[\d.,]*\b", "", cleaned)
    cleaned = re.sub(
        r"\b(lanca|lance|registrar|registre|gastei|paguei|recebi|ganhei|despesa|receita|hoje|ontem|amanha|de|do|da|no|na|um|uma)\b",
        " ",
        cleaned,
        flags=re.I,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .,-")
    return cleaned[:120] if cleaned else fallback


def _summary_reply(bundle: dict[str, Any]) -> str:
    tx = bundle["transactions"]
    accounts = bundle["accounts"]
    saldo = float(accounts["saldo"].sum()) if not accounts.empty else 0.0
    receitas = float(tx.loc[tx["tipo"] == "Receita", "valor"].sum()) if not tx.empty else 0.0
    despesas = float(tx.loc[tx["tipo"] == "Despesa", "valor"].sum()) if not tx.empty else 0.0
    resultado = receitas - despesas
    return (
        f"📊 **Resumo financeiro**\n\n"
        f"Saldo consolidado: **{brl(saldo)}**\n\n"
        f"Receitas: **{brl(receitas)}**\n\n"
        f"Despesas: **{brl(despesas)}**\n\n"
        f"Resultado: **{brl(resultado)}**"
    )


def process_message(user_id: str, message: str, bundle: dict[str, Any]) -> AIReply:
    normalized = _norm(message)
    accounts = bundle["accounts"]
    categories = bundle["categories"]
    tx = bundle["transactions"]

    if any(term in normalized for term in ["resumo", "situacao", "analisar", "analise", "como estao minhas financas", "saldo"]):
        text = _summary_reply(bundle)
        log_ai_action(user_id, message, "analysis_summary", {}, "analysis", text)
        return AIReply(text=text)

    if any(term in normalized for term in ["apagar", "excluir", "deletar"]):
        candidates = tx.sort_values("data", ascending=False).head(5) if not tx.empty else tx
        if candidates.empty:
            return AIReply("Não encontrei lançamentos para excluir.")
        target = candidates.iloc[0]
        payload = {"transaction_id": str(target["id"]), "new_status": "cancelado", "description": str(target["descricao"])}
        text = (
            f"⚠️ Encontrei o lançamento **{target['descricao']} — {brl(float(target['valor']))}**. "
            "Essa ação é sensível. Digite **CONFIRMAR** para cancelar esse lançamento."
        )
        log_ai_action(user_id, message, "cancel_transaction", payload, "pending_confirmation", text)
        return AIReply(text=text, pending_confirmation=payload)

    amount = _extract_amount(message)

    if "meta" in normalized or "juntar" in normalized or "economizar" in normalized:
        if not amount:
            return AIReply("Informe o valor da meta. Exemplo: **Crie uma meta de R$ 5.000 para reserva de emergência.**")
        name = _description(message, "Meta financeira")
        create_financial_goal(user_id, name, amount, None)
        text = f"🎯 Meta criada: **{name} — {brl(amount)}**."
        log_ai_action(user_id, message, "create_goal", {"name": name, "target_amount": amount}, "executed", text)
        return AIReply(text=text, executed=True)

    if "orcamento" in normalized or "limite mensal" in normalized:
        if not amount:
            return AIReply("Informe o valor do orçamento mensal.")
        category_id, category_name = _infer_category(message, categories)
        if not category_id:
            return AIReply("Não encontrei uma categoria para esse orçamento.")
        upsert_budget(user_id, category_id, date.today().replace(day=1), amount)
        text = f"✅ Orçamento de **{category_name}** definido em **{brl(amount)}** para este mês."
        log_ai_action(user_id, message, "upsert_budget", {"category_id": category_id, "amount": amount}, "executed", text)
        return AIReply(text=text, executed=True)

    recurring = any(term in normalized for term in ["recorrente", "todo mes", "mensalmente", "todo dia"])
    is_income = any(term in normalized for term in ["recebi", "ganhei", "receita", "entrada", "vendi"])
    is_expense = any(term in normalized for term in ["gastei", "paguei", "despesa", "saida", "comprei"])

    if recurring and (is_income or is_expense):
        if not amount:
            return AIReply("Informe o valor do lançamento recorrente.")
        account_id, account_name = _pick_account(accounts, message)
        category_id, category_name = _infer_category(message, categories)
        if not account_id:
            return AIReply("Cadastre uma conta antes de criar lançamentos.")
        kind = "receita" if is_income and not is_expense else "despesa"
        description = _description(message, "Receita recorrente" if kind == "receita" else "Despesa recorrente")
        create_recurring_transaction(
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
            kind=kind,
            description=description,
            amount=amount,
            frequency="mensal",
            next_due_date=_extract_date(message),
        )
        text = (
            f"🔁 Lançamento recorrente criado: **{description} — {brl(amount)}** "
            f"em **{account_name}**, categoria **{category_name}**."
        )
        log_ai_action(user_id, message, "create_recurring", {"description": description, "amount": amount, "kind": kind}, "executed", text)
        return AIReply(text=text, executed=True)

    if is_income or is_expense:
        if not amount:
            return AIReply("Informe o valor. Exemplo: **Gastei R$ 85 no mercado hoje.**")
        account_id, account_name = _pick_account(accounts, message)
        category_id, category_name = _infer_category(message, categories)
        if not account_id:
            return AIReply("Cadastre uma conta antes de criar lançamentos.")
        kind = "receita" if is_income and not is_expense else "despesa"
        description = _description(message, "Receita" if kind == "receita" else "Despesa")
        occurred_on = _extract_date(message)
        create_transaction(user_id, account_id, category_id, kind, description, amount, occurred_on)
        icon = "💰" if kind == "receita" else "💸"
        text = (
            f"{icon} Lançamento registrado: **{description} — {brl(amount)}**\n\n"
            f"Conta: **{account_name}** · Categoria: **{category_name}** · Data: **{occurred_on.strftime('%d/%m/%Y')}**"
        )
        log_ai_action(
            user_id,
            message,
            "create_transaction",
            {"description": description, "amount": amount, "kind": kind, "account_id": account_id, "category_id": category_id},
            "executed",
            text,
        )
        return AIReply(text=text, executed=True)

    return AIReply(
        "Posso executar sua gestão financeira por aqui. Tente algo como: "
        "**“Gastei R$ 85 no mercado hoje”**, **“Recebi R$ 1.500 de um freelance”**, "
        "**“Crie uma meta de R$ 5.000”**, **“Defina orçamento de R$ 600 para alimentação”** "
        "ou **“Faça um resumo das minhas finanças”**."
    )


def confirm_pending_action(user_id: str, original_command: str, pending: dict[str, Any]) -> AIReply:
    transaction_id = str(pending.get("transaction_id") or "")
    if not transaction_id:
        return AIReply("Não há ação pendente válida para confirmar.")
    update_transaction_status(user_id, transaction_id, str(pending.get("new_status") or "cancelado"))
    text = f"✅ Ação confirmada. O lançamento **{pending.get('description', 'selecionado')}** foi cancelado."
    log_ai_action(user_id, original_command, "cancel_transaction", pending, "confirmed", text)
    return AIReply(text=text, executed=True)
