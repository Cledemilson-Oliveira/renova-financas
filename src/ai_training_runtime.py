from __future__ import annotations

import re
import unicodedata
from typing import Any

from src.ai_free_training import process_standard_message


_MEMORY_QUERY_TERMS = (
    "o que voce sabe",
    "o que você sabe",
    "o que aprendeu",
    "o que voce aprendeu",
    "minha memoria",
    "minha memória",
    "meus treinamentos",
    "minhas preferencias",
    "minhas preferências",
    "minha prioridade",
    "meu negocio",
    "meu negócio",
)

_ANALYSIS_TERMS = (
    "resumo",
    "situacao",
    "situação",
    "analisar",
    "analise",
    "análise",
    "como estao minhas financas",
    "como estão minhas finanças",
    "o que devo priorizar",
    "qual minha prioridade",
    "me ajude a decidir",
    "planejamento",
)

_SAFE_AUTOFILL_INTENTS = {
    "transaction",
    "recurring_transaction",
    "budget",
    "goal_create",
    "card_limit",
}


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", value.lower()).strip()


def _clip(text: str, limit: int = 320) -> str:
    clean = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"


def _is_memory_query(message: str) -> bool:
    normalized = _norm(message)
    return any(_norm(term) in normalized for term in _MEMORY_QUERY_TERMS)


def _is_analysis_request(message: str) -> bool:
    normalized = _norm(message)
    return any(_norm(term) in normalized for term in _ANALYSIS_TERMS)


def _context_block(items: list[dict[str, Any]], limit: int = 4) -> str:
    if not items:
        return ""
    lines = []
    for item in items[: max(1, min(int(limit), 6))]:
        title = str(item.get("title") or "Conhecimento")
        kind = str(item.get("kind") or "conhecimento").replace("_", " ")
        content = _clip(str(item.get("content") or ""), 260)
        lines.append(f"- **{title}** ({kind}): {content}")
    return "\n".join(lines)


def _memory_answer(items: list[dict[str, Any]]) -> str:
    if not items:
        return (
            "🧠 Ainda não encontrei treinamentos personalizados ativos relacionados a esse pedido. "
            "Você pode adicionar conhecimentos no módulo **Treinamento da IA**."
        )
    return (
        "🧠 **Memória personalizada que encontrei para este assunto**\n\n"
        + _context_block(items, limit=6)
        + "\n\nEsses conhecimentos pertencem somente à sua conta e não substituem as regras de segurança do sistema."
    )


def _matched_keywords(item: dict[str, Any], message: str) -> bool:
    normalized = _norm(message)
    keywords = [str(value) for value in (item.get("keywords") or []) if str(value).strip()]
    if keywords:
        return any(_norm(keyword) in normalized for keyword in keywords)

    title_tokens = [token for token in re.findall(r"[a-zA-ZÀ-ÿ0-9]{4,}", _norm(str(item.get("title") or "")))]
    return any(token in normalized for token in title_tokens)


def _money_from_item(item: dict[str, Any]) -> float | None:
    text = str(item.get("content") or "")
    matches = re.findall(
        r"(?:r\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})|\d+(?:[.,]\d{1,2})?)",
        text,
        flags=re.I,
    )
    if not matches:
        return None
    for raw in matches:
        try:
            value = float(raw.replace(".", "").replace(",", "."))
        except ValueError:
            continue
        if value > 0:
            return value
    return None


def _training_amount(items: list[dict[str, Any]], message: str) -> tuple[float | None, str | None]:
    for item in items:
        if str(item.get("application_mode") or "") == "somente_consulta":
            continue
        if int(item.get("priority") or 0) < 70:
            continue
        if not _matched_keywords(item, message):
            continue
        amount = _money_from_item(item)
        if amount is not None:
            return amount, str(item.get("title") or "Treinamento da IA")
    return None, None


def _structured_rule_titles(items: list[dict[str, Any]], message: str) -> list[str]:
    normalized = _norm(message)
    applied: list[str] = []
    for item in items:
        if str(item.get("application_mode") or "") == "somente_consulta":
            continue
        rule = item.get("structured_rule") or {}
        rule_type = str(rule.get("rule_type") or "")
        trigger = _norm(str(rule.get("trigger") or ""))
        if rule_type in {"category_alias", "type_alias"} and trigger and trigger in normalized:
            applied.append(str(item.get("title") or "Regra personalizada"))
    return applied[:3]


def _personalized_training_enabled(bundle: dict[str, Any], user_id: str) -> bool:
    """O app informa o tier da sessão; o fallback atende usos fora da UI."""
    if "_allow_personalized_training" in bundle:
        return bool(bundle.get("_allow_personalized_training"))

    try:
        from src.access import is_owner
        from src.repository import has_active_ai_subscription

        return bool(is_owner(user_id) or has_active_ai_subscription(user_id))
    except Exception:
        return False


def install_training_runtime(ai_finance_module: Any, ai_training_module: Any) -> None:
    """Conecta os dois níveis de treinamento ao processador financeiro.

    - Gratuito: treinamento operacional fixo do produto, sem memória personalizada.
    - Premium/dono: mesmo núcleo financeiro + regras, memória e materiais privados.
    """
    if getattr(ai_finance_module, "_renova_training_runtime_installed", False):
        return

    original_process = ai_finance_module.process_message
    reply_type = ai_finance_module.AIReply

    def trained_process_message(user_id: str, message: str, bundle: dict[str, Any]):
        if not _personalized_training_enabled(bundle, user_id):
            return process_standard_message(ai_finance_module, user_id, message, bundle)

        try:
            items = ai_training_module.relevant_training_items(user_id, message, limit=8)
        except Exception:
            items = []

        if _is_memory_query(message):
            return reply_type(text=_memory_answer(items))

        result = original_process(user_id, message, bundle)

        # Se o comando for seguro, estiver apenas aguardando um valor e o usuário já
        # tiver ensinado esse valor com alta prioridade, a memória completa o pedido.
        pending_context = getattr(result, "pending_context", None) or {}
        intent = str(pending_context.get("intent") or "")
        if intent in _SAFE_AUTOFILL_INTENTS and items:
            amount, source_title = _training_amount(items, message)
            if amount is not None:
                enriched_message = f"{message.strip()} R$ {amount:.2f}"
                retried = original_process(user_id, enriched_message, bundle)
                if getattr(retried, "executed", False) or not getattr(retried, "pending_context", None):
                    retried.text = (
                        f"{retried.text}\n\n🧠 Usei o treinamento **{source_title}** para completar o valor deste pedido."
                    )
                    result = retried

        # Consultas e análises recebem o contexto livre ensinado pelo usuário.
        if items and _is_analysis_request(message) and not getattr(result, "executed", False):
            consultation_items = [
                item
                for item in items
                if str(item.get("application_mode") or "")
                in {"sempre", "quando_relevante", "somente_consulta"}
            ]
            block = _context_block(consultation_items, limit=4)
            if block:
                result.text = (
                    f"{result.text}\n\n🧠 **Contexto personalizado considerado**\n{block}"
                )

        # Transparência: mostra quando uma regra estruturada ensinada pelo usuário
        # foi compatível com o comando executado.
        if items and getattr(result, "executed", False):
            titles = _structured_rule_titles(items, message)
            if titles:
                result.text = (
                    f"{result.text}\n\n🧠 Regra personalizada aplicada: "
                    + ", ".join(f"**{title}**" for title in titles)
                    + "."
                )

        # Quando ainda faltam detalhes, a IA informa que já possui contexto útil
        # sem inventar nem executar algo que o usuário não pediu explicitamente.
        if (
            items
            and not getattr(result, "executed", False)
            and not getattr(result, "pending_confirmation", None)
            and not getattr(result, "pending_context", None)
            and str(getattr(result, "text", "")).startswith("Entendi:")
        ):
            result.text = (
                f"{result.text}\n\n🧠 Tenho memória relacionada a este assunto:\n"
                f"{_context_block(items, limit=3)}"
            )

        return result

    ai_finance_module.process_message = trained_process_message
    ai_finance_module._renova_training_runtime_installed = True
    ai_finance_module._renova_free_training_installed = True
