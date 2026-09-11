from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from src.data import brl
from src.repository import (
    create_account,
    create_card,
    create_category,
    create_financial_goal,
    create_recurring_transaction,
    create_transaction,
    create_transfer,
    log_ai_action,
    upsert_budget,
    update_account,
    update_card,
    update_financial_goal,
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


def _find_named_row(df, name_column: str, message: str):
    if df is None or df.empty:
        return None
    normalized = _norm(message)
    best = None
    best_len = -1
    for _, row in df.iterrows():
        name = str(row[name_column])
        token = _norm(name)
        if token and token in normalized and len(token) > best_len:
            best = row
            best_len = len(token)
    return best


def _pick_two_accounts(accounts, message: str):
    if accounts is None or accounts.empty or len(accounts) < 2:
        return None, None
    normalized = _norm(message)
    matches = []
    for _, row in accounts.iterrows():
        name = str(row["conta"])
        if _norm(name) in normalized:
            matches.append(row)
    if len(matches) >= 2:
        return matches[0], matches[1]
    return accounts.iloc[0], accounts.iloc[1]


def _extract_integer_after(text: str, keywords: list[str]) -> int | None:
    normalized = _norm(text)
    for keyword in keywords:
        m = re.search(rf"{re.escape(keyword)}\s*(?:dia\s*)?(\d{{1,2}})", normalized)
        if m:
            return int(m.group(1))
    return None


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
    cards = bundle.get("cards")
    goals = bundle.get("goals")
    tx = bundle["transactions"]
    amount = _extract_amount(message)

    # Consultas e análises
    if any(term in normalized for term in [
        "resumo", "situacao", "analisar", "analise", "como estao minhas financas",
        "saldo", "quanto tenho", "quanto gastei", "quanto recebi"
    ]):
        text = _summary_reply(bundle)
        log_ai_action(user_id, message, "analysis_summary", {}, "analysis", text)
        return AIReply(text=text)

    # Operações destrutivas sempre exigem confirmação.
    if any(term in normalized for term in ["apagar", "excluir", "deletar", "remover lancamento"]):
        candidates = tx.sort_values("data", ascending=False).head(5) if not tx.empty else tx
        if candidates.empty:
            return AIReply("Não encontrei lançamentos para excluir.")
        target = _find_named_row(candidates, "descricao", message)
        if target is None:
            target = candidates.iloc[0]
        payload = {
            "transaction_id": str(target["id"]),
            "new_status": "cancelado",
            "description": str(target["descricao"]),
        }
        text = (
            f"⚠️ Vou cancelar o lançamento **{target['descricao']} — {brl(float(target['valor']))}**. "
            "Digite **CONFIRMAR** para executar ou **CANCELAR** para desistir."
        )
        log_ai_action(user_id, message, "cancel_transaction", payload, "pending_confirmation", text)
        return AIReply(text=text, pending_confirmation=payload)

    # Marcar lançamento como pago / previsto / atrasado.
    if any(term in normalized for term in ["marcar como pago", "marque como pago", "dar baixa", "baixar conta"]):
        if tx.empty:
            return AIReply("Não encontrei lançamentos para dar baixa.")
        target = _find_named_row(tx, "descricao", message)
        if target is None:
            target = tx.sort_values("data", ascending=False).iloc[0]
        update_transaction_status(user_id, str(target["id"]), "pago")
        text = f"✅ **{target['descricao']}** foi marcado como pago."
        log_ai_action(user_id, message, "mark_paid", {"transaction_id": str(target["id"])}, "executed", text)
        return AIReply(text=text, executed=True)

    # Transferência entre contas.
    if any(term in normalized for term in ["transferir", "transferencia", "mover dinheiro", "mova dinheiro"]):
        if not amount:
            return AIReply("Informe o valor da transferência.")
        source, destination = _pick_two_accounts(accounts, message)
        if source is None or destination is None:
            return AIReply("Cadastre pelo menos duas contas para fazer transferências.")
        occurred_on = _extract_date(message)
        create_transfer(
            user_id,
            str(source["id"]),
            str(destination["id"]),
            _description(message, "Transferência"),
            amount,
            occurred_on,
        )
        text = (
            f"🔄 Transferência registrada: **{brl(amount)}** de **{source['conta']}** "
            f"para **{destination['conta']}** em **{occurred_on.strftime('%d/%m/%Y')}**."
        )
        log_ai_action(user_id, message, "create_transfer", {"amount": amount}, "executed", text)
        return AIReply(text=text, executed=True)

    # Contas financeiras.
    if any(term in normalized for term in ["criar conta", "nova conta", "cadastre uma conta", "cadastrar conta"]):
        name = _description(message, "Nova conta")
        account_type = "poupanca" if "poupanca" in normalized else "investimento" if "investimento" in normalized else "carteira" if "carteira" in normalized else "conta"
        create_account(user_id, name, account_type, amount or 0.0)
        text = f"🏦 Conta **{name}** criada com saldo inicial de **{brl(amount or 0.0)}**."
        log_ai_action(user_id, message, "create_account", {"name": name, "type": account_type, "initial_balance": amount or 0}, "executed", text)
        return AIReply(text=text, executed=True)

    if any(term in normalized for term in ["renomear conta", "mudar nome da conta"]):
        target = _find_named_row(accounts, "conta", message)
        if target is None:
            return AIReply("Diga qual conta deseja renomear.")
        m = re.search(r"(?:para|como)\s+(.+)$", message, flags=re.I)
        if not m:
            return AIReply("Informe o novo nome da conta.")
        new_name = m.group(1).strip()
        update_account(user_id, str(target["id"]), name=new_name)
        text = f"✅ Conta renomeada para **{new_name}**."
        log_ai_action(user_id, message, "rename_account", {"account_id": str(target["id"]), "name": new_name}, "executed", text)
        return AIReply(text=text, executed=True)

    # Cartões.
    if any(term in normalized for term in ["criar cartao", "novo cartao", "cadastre um cartao", "cadastrar cartao"]):
        name = _description(message, "Novo cartão")
        closing_day = _extract_integer_after(message, ["fecha", "fechamento"]) or 10
        due_day = _extract_integer_after(message, ["vence", "vencimento"]) or 17
        account_id, _ = _pick_account(accounts, message)
        create_card(user_id, name, amount or 0.0, closing_day, due_day, account_id)
        text = f"💳 Cartão **{name}** criado com limite de **{brl(amount or 0.0)}**, fechamento dia {closing_day} e vencimento dia {due_day}."
        log_ai_action(user_id, message, "create_card", {"name": name, "limit": amount or 0}, "executed", text)
        return AIReply(text=text, executed=True)

    if any(term in normalized for term in ["alterar limite", "mudar limite", "aumentar limite", "reduzir limite"]):
        target = _find_named_row(cards, "cartao", message) if cards is not None else None
        if target is None:
            return AIReply("Diga qual cartão deseja alterar.")
        if not amount:
            return AIReply("Informe o novo limite do cartão.")
        update_card(user_id, str(target["id"]), credit_limit=amount)
        text = f"✅ Limite do cartão **{target['cartao']}** atualizado para **{brl(amount)}**."
        log_ai_action(user_id, message, "update_card_limit", {"card_id": str(target["id"]), "limit": amount}, "executed", text)
        return AIReply(text=text, executed=True)

    # Categorias.
    if any(term in normalized for term in ["criar categoria", "nova categoria", "cadastre uma categoria"]):
        kind = "receita" if "receita" in normalized else "despesa" if "despesa" in normalized else "ambos"
        name = _description(message, "Nova categoria")
        create_category(user_id, name, kind)
        text = f"🏷️ Categoria **{name}** criada para **{kind}**."
        log_ai_action(user_id, message, "create_category", {"name": name, "kind": kind}, "executed", text)
        return AIReply(text=text, executed=True)

    # Metas.
    if "meta" in normalized or "juntar" in normalized or "economizar" in normalized:
        if any(term in normalized for term in ["atualizar meta", "adicionar na meta", "guardar na meta", "colocar na meta"]) and goals is not None and not goals.empty:
            target = _find_named_row(goals, "name", message)
            if target is None:
                target = goals.iloc[0]
            if not amount:
                return AIReply("Informe o valor que deseja registrar na meta.")
            current = float(target.get("current_amount") or 0) + amount
            update_financial_goal(user_id, str(target["id"]), current_amount=current)
            text = f"🎯 Meta **{target['name']}** atualizada para **{brl(current)}** acumulados."
            log_ai_action(user_id, message, "update_goal", {"goal_id": str(target["id"]), "current_amount": current}, "executed", text)
            return AIReply(text=text, executed=True)

        if not amount:
            return AIReply("Informe o valor da meta. Exemplo: **Crie uma meta de R$ 5.000 para reserva de emergência.**")
        name = _description(message, "Meta financeira")
        create_financial_goal(user_id, name, amount, None)
        text = f"🎯 Meta criada: **{name} — {brl(amount)}**."
        log_ai_action(user_id, message, "create_goal", {"name": name, "target_amount": amount}, "executed", text)
        return AIReply(text=text, executed=True)

    # Orçamento.
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

    # Recorrências.
    recurring = any(term in normalized for term in ["recorrente", "todo mes", "mensalmente", "todo dia", "todo ano", "anualmente"])
    is_income = any(term in normalized for term in ["recebi", "ganhei", "receita", "entrada", "vendi", "faturei"])
    is_expense = any(term in normalized for term in ["gastei", "paguei", "despesa", "saida", "comprei", "cobrança", "cobranca"])

    if recurring and (is_income or is_expense):
        if not amount:
            return AIReply("Informe o valor do lançamento recorrente.")
        account_id, account_name = _pick_account(accounts, message)
        category_id, category_name = _infer_category(message, categories)
        if not account_id:
            return AIReply("Cadastre uma conta antes de criar lançamentos.")
        kind = "receita" if is_income and not is_expense else "despesa"
        description = _description(message, "Receita recorrente" if kind == "receita" else "Despesa recorrente")
        frequency = "anual" if "anual" in normalized or "todo ano" in normalized else "semanal" if "seman" in normalized else "quinzenal" if "quinzen" in normalized else "mensal"
        create_recurring_transaction(
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
            kind=kind,
            description=description,
            amount=amount,
            frequency=frequency,
            next_due_date=_extract_date(message),
        )
        text = f"🔁 Lançamento recorrente criado: **{description} — {brl(amount)}** em **{account_name}**, categoria **{category_name}**."
        log_ai_action(user_id, message, "create_recurring", {"description": description, "amount": amount, "kind": kind, "frequency": frequency}, "executed", text)
        return AIReply(text=text, executed=True)

    # Receitas e despesas comuns.
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
        log_ai_action(user_id, message, "create_transaction", {"description": description, "amount": amount, "kind": kind, "account_id": account_id, "category_id": category_id}, "executed", text)
        return AIReply(text=text, executed=True)

    text = (
        "Entendi o pedido, mas ainda não existe uma ferramenta interna compatível para executá-lo automaticamente. "
        "No **Modo Execução Total**, eu executo sem confirmação prévia todas as ações suportadas e permitidas pela conta. "
        "Para ações irreversíveis, exclusões, movimentações externas ou operações que possam gerar cobrança, "
        "mantenho uma confirmação final de segurança antes de concluir."
    )
    log_ai_action(user_id, message, "unsupported_or_incomplete", {}, "analysis", text)
    return AIReply(text)


def confirm_pending_action(user_id: str, original_command: str, pending: dict[str, Any]) -> AIReply:
    transaction_id = str(pending.get("transaction_id") or "")
    if not transaction_id:
        return AIReply("Não há ação pendente válida para confirmar.")
    update_transaction_status(user_id, transaction_id, str(pending.get("new_status") or "cancelado"))
    text = f"✅ Ação confirmada. O lançamento **{pending.get('description', 'selecionado')}** foi cancelado."
    log_ai_action(user_id, original_command, "cancel_transaction", pending, "confirmed", text)
    return AIReply(text=text, executed=True)
