"""Otimizações transparentes de performance e UX para o RENOVA Finanças.

O Streamlit reexecuta o script a cada interação de widget. Sem uma camada de
cache, marcar um checkbox ou alterar um filtro pode disparar novamente todas as
consultas financeiras no Supabase. Este módulo é carregado automaticamente pelo
Python e aplica um cache curto, por usuário, apenas às leituras.

Também ajusta especificamente o chat modal do Assistente Financeiro IA para ter
comportamento de aplicativo de mensagens: histórico rolável, campo de entrada
preso ao rodapé e posicionamento automático na mensagem mais recente.

Na tabela de lançamentos, as células passam a ser editáveis diretamente e as
alterações são persistidas no Supabase automaticamente, sem exigir o modal de
edição.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from functools import wraps
from threading import RLock
from time import monotonic
from typing import Any, Callable

_CACHE_TTL_SECONDS = 12.0
_LOCK = RLock()
_FINANCIAL_CACHE: dict[str, tuple[float, Any]] = {}
_ACCESS_CACHE: dict[str, tuple[float, Any]] = {}


def _invalidate_user(user_id: Any) -> None:
    if user_id is None:
        return
    with _LOCK:
        _FINANCIAL_CACHE.pop(str(user_id), None)


def _install_repository_cache() -> None:
    try:
        import src.repository as repository
    except Exception:
        return

    original_fetch = getattr(repository, "fetch_financial_data", None)
    if not callable(original_fetch) or getattr(original_fetch, "_renova_cached", False):
        return

    @wraps(original_fetch)
    def cached_fetch_financial_data(user_id: str):
        cache_key = str(user_id)
        now = monotonic()
        with _LOCK:
            cached = _FINANCIAL_CACHE.get(cache_key)
            if cached and now - cached[0] < _CACHE_TTL_SECONDS:
                return deepcopy(cached[1])

        data = original_fetch(user_id)
        with _LOCK:
            _FINANCIAL_CACHE[cache_key] = (monotonic(), deepcopy(data))
        return data

    cached_fetch_financial_data._renova_cached = True  # type: ignore[attr-defined]
    repository.fetch_financial_data = cached_fetch_financial_data

    mutation_names = (
        "create_account",
        "create_card",
        "create_category",
        "create_transaction",
        "delete_transaction",
        "update_transaction",
        "upsert_budget",
        "create_goal",
        "update_goal",
        "delete_goal",
        "create_card_expense",
        "update_card_expense",
        "delete_card_expense",
    )

    for name in mutation_names:
        original = getattr(repository, name, None)
        if not callable(original) or getattr(original, "_renova_invalidates_cache", False):
            continue

        def make_wrapper(fn: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(fn)
            def wrapper(*args, **kwargs):
                result = fn(*args, **kwargs)
                user_id = args[0] if args else kwargs.get("user_id")
                _invalidate_user(user_id)
                return result

            wrapper._renova_invalidates_cache = True  # type: ignore[attr-defined]
            return wrapper

        setattr(repository, name, make_wrapper(original))


def _install_access_cache() -> None:
    """Evita recarregar a lista do Modo Dono em cada clique/checkbox."""
    try:
        import src.access as access
    except Exception:
        return

    original_list = getattr(access, "list_user_access", None)
    if not callable(original_list) or getattr(original_list, "_renova_cached", False):
        return

    @wraps(original_list)
    def cached_list_user_access(*args, **kwargs):
        cache_key = repr((args, sorted(kwargs.items())))
        now = monotonic()
        with _LOCK:
            cached = _ACCESS_CACHE.get(cache_key)
            if cached and now - cached[0] < 60.0:
                return deepcopy(cached[1])

        data = original_list(*args, **kwargs)
        with _LOCK:
            _ACCESS_CACHE[cache_key] = (monotonic(), deepcopy(data))
        return data

    cached_list_user_access._renova_cached = True  # type: ignore[attr-defined]
    access.list_user_access = cached_list_user_access


def _install_modal_chat_ux() -> None:
    """Mantém o input do chat modal fixo no rodapé e o histórico no fim."""
    try:
        import streamlit as st
        import streamlit.components.v1 as components
    except Exception:
        return

    if getattr(st, "_renova_modal_chat_patched", False):
        return

    original_chat_input = st.chat_input

    modal_css = r"""
    <style>
    div[role="dialog"] {
      height: min(820px, 88vh) !important;
      max-height: 88vh !important;
      overflow-y: auto !important;
      overscroll-behavior: contain !important;
      scrollbar-gutter: stable !important;
      padding-bottom: 0 !important;
    }

    div[role="dialog"] [data-testid="stChatInput"] {
      position: sticky !important;
      bottom: 0 !important;
      z-index: 999 !important;
      margin-top: 12px !important;
      padding: 10px 0 12px !important;
      background:
        linear-gradient(180deg, rgba(2,8,14,0), rgba(2,8,14,.96) 28%, rgba(2,8,14,.995) 100%) !important;
      backdrop-filter: blur(14px) !important;
    }

    div[role="dialog"] [data-testid="stChatInput"] > div {
      border-radius: 16px !important;
      box-shadow: 0 -10px 32px rgba(0,0,0,.28), 0 0 22px rgba(25,217,255,.08) !important;
    }

    div[role="dialog"] [data-testid="stChatMessage"]:last-of-type {
      margin-bottom: 20px !important;
    }

    div[role="dialog"] > div:first-child {
      position: sticky !important;
      top: 0 !important;
      z-index: 1000 !important;
    }

    @media (max-width: 768px) {
      div[role="dialog"] {
        width: calc(100vw - 16px) !important;
        max-width: calc(100vw - 16px) !important;
        height: 92dvh !important;
        max-height: 92dvh !important;
        margin: 4dvh 8px !important;
      }

      div[role="dialog"] [data-testid="stChatInput"] {
        padding-bottom: max(10px, env(safe-area-inset-bottom)) !important;
      }
    }
    </style>
    """

    auto_scroll_js = r"""
    <script>
    (function () {
      function goToLatestMessage() {
        try {
          const doc = window.parent.document;
          const dialogs = Array.from(doc.querySelectorAll('div[role="dialog"]'));
          if (!dialogs.length) return;
          const dialog = dialogs[dialogs.length - 1];
          const input = dialog.querySelector('[data-testid="stChatInput"]');
          if (!input) return;

          const messages = dialog.querySelectorAll('[data-testid="stChatMessage"]');
          const last = messages.length ? messages[messages.length - 1] : null;
          if (last) last.scrollIntoView({behavior:'instant', block:'end'});
          input.scrollIntoView({behavior:'instant', block:'end'});
          dialog.scrollTop = dialog.scrollHeight;
        } catch (e) {
          /* CSS sticky continua garantindo o uso mesmo se o JS for bloqueado. */
        }
      }

      requestAnimationFrame(goToLatestMessage);
      setTimeout(goToLatestMessage, 70);
      setTimeout(goToLatestMessage, 180);
      setTimeout(goToLatestMessage, 350);
    })();
    </script>
    """

    @wraps(original_chat_input)
    def renova_chat_input(*args, **kwargs):
        is_modal_ai = kwargs.get("key") == "ai_modal_input"
        if is_modal_ai:
            st.markdown(modal_css, unsafe_allow_html=True)

        value = original_chat_input(*args, **kwargs)

        if is_modal_ai:
            try:
                components.html(auto_scroll_js, height=0, scrolling=False)
            except Exception:
                pass
        return value

    st.chat_input = renova_chat_input
    st._renova_modal_chat_patched = True


def _install_inline_transaction_editor() -> None:
    """Permite editar lançamentos direto na grade e salva cada célula alterada."""
    try:
        import pandas as pd
        import streamlit as st
        import src.repository as repository
    except Exception:
        return

    if getattr(st, "_renova_inline_transactions_patched", False):
        return

    original_data_editor = st.data_editor

    def _is_blank(value: Any) -> bool:
        try:
            return value is None or pd.isna(value)
        except Exception:
            return value is None

    def _as_date(value: Any) -> date | None:
        if _is_blank(value):
            return None
        if isinstance(value, date):
            return value
        try:
            return pd.to_datetime(value).date()
        except Exception:
            return None

    def _as_amount(value: Any) -> float:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        text = str(value or "").strip().replace("R$", "").replace(" ", "")
        if not text:
            return 0.0
        if "," in text:
            text = text.replace(".", "").replace(",", ".")
        return float(text)

    def _same_text(a: Any, b: Any) -> bool:
        return str(a or "").strip() == str(b or "").strip()

    @wraps(original_data_editor)
    def renova_data_editor(data, *args, **kwargs):
        if kwargs.get("key") != "transactions_editor" or not isinstance(data, pd.DataFrame):
            return original_data_editor(data, *args, **kwargs)

        working = data.copy(deep=True)
        if "valor" in working.columns:
            working["valor"] = working["valor"].map(_as_amount)

        categories = st.session_state.get("categories")
        accounts = st.session_state.get("accounts")

        category_names: list[str] = []
        category_ids: dict[str, str] = {}
        if isinstance(categories, pd.DataFrame) and not categories.empty:
            category_view = categories.copy()
            if "is_active" in category_view.columns:
                category_view = category_view[category_view["is_active"] == True]
            if "name" in category_view.columns:
                category_names = sorted(category_view["name"].dropna().astype(str).unique().tolist())
            if {"name", "id"}.issubset(category_view.columns):
                category_ids = {
                    str(row["name"]): str(row["id"])
                    for _, row in category_view.iterrows()
                }

        account_names: list[str] = []
        account_ids: dict[str, str] = {}
        if isinstance(accounts, pd.DataFrame) and not accounts.empty:
            account_view = accounts.copy()
            if "ativo" in account_view.columns:
                account_view = account_view[account_view["ativo"] == True]
            if "conta" in account_view.columns:
                account_names = account_view["conta"].dropna().astype(str).unique().tolist()
            if {"conta", "id"}.issubset(account_view.columns):
                account_ids = {
                    str(row["conta"]): str(row["id"])
                    for _, row in account_view.iterrows()
                }

        config = dict(kwargs.get("column_config") or {})
        config.update(
            {
                "selecionar": st.column_config.CheckboxColumn(
                    "✓", help="Marque para selecionar", default=False, width="small"
                ),
                "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY", width="small"),
                "vencimento": st.column_config.DateColumn(
                    "Vencimento", format="DD/MM/YYYY", width="small"
                ),
                "tipo": st.column_config.SelectboxColumn(
                    "Tipo", options=["Receita", "Despesa"], required=True, width="small"
                ),
                "categoria": st.column_config.SelectboxColumn(
                    "Categoria", options=category_names, required=True, width="medium"
                ) if category_names else st.column_config.TextColumn("Categoria", width="medium"),
                "descricao": st.column_config.TextColumn(
                    "Descrição", required=True, width="large"
                ),
                "valor": st.column_config.NumberColumn(
                    "Valor", min_value=0.01, step=0.01, format="R$ %.2f", width="small"
                ),
                "conta": st.column_config.SelectboxColumn(
                    "Conta", options=account_names, required=True, width="medium"
                ) if account_names else st.column_config.TextColumn("Conta", width="medium"),
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["✅ Pago", "🕒 Previsto", "🚨 Atrasado"],
                    required=True,
                    width="small",
                ),
                "_tx_id": None,
            }
        )
        kwargs["column_config"] = config
        kwargs["disabled"] = ["_tx_id"]

        edited = original_data_editor(working, *args, **kwargs)

        if not isinstance(edited, pd.DataFrame) or "_tx_id" not in edited.columns:
            return edited

        status_map = {
            "✅ Pago": "pago",
            "🕒 Previsto": "previsto",
            "🕒 Pendente": "previsto",
            "🚨 Atrasado": "atrasado",
            "pago": "pago",
            "previsto": "previsto",
            "atrasado": "atrasado",
        }
        kind_map = {"Receita": "receita", "Despesa": "despesa"}
        user_id = str(st.session_state.get("active_financial_user_id") or "")
        if not user_id:
            return edited

        base_by_id = {
            str(row["_tx_id"]): row
            for _, row in working.iterrows()
            if not _is_blank(row.get("_tx_id"))
        }

        saved = 0
        for _, row in edited.iterrows():
            transaction_id = str(row.get("_tx_id") or "")
            base = base_by_id.get(transaction_id)
            if base is None:
                continue

            changes: dict[str, Any] = {}

            if "data" in edited.columns and _as_date(row.get("data")) != _as_date(base.get("data")):
                changes["occurred_on"] = _as_date(row.get("data"))

            if "vencimento" in edited.columns and _as_date(row.get("vencimento")) != _as_date(base.get("vencimento")):
                changes["due_date"] = _as_date(row.get("vencimento"))

            if "tipo" in edited.columns and not _same_text(row.get("tipo"), base.get("tipo")):
                kind = kind_map.get(str(row.get("tipo")))
                if kind:
                    changes["kind"] = kind

            if "categoria" in edited.columns and not _same_text(row.get("categoria"), base.get("categoria")):
                category_id = category_ids.get(str(row.get("categoria")))
                if category_id:
                    changes["category_id"] = category_id

            if "descricao" in edited.columns and not _same_text(row.get("descricao"), base.get("descricao")):
                description = str(row.get("descricao") or "").strip()
                if description:
                    changes["description"] = description

            if "valor" in edited.columns:
                edited_amount = _as_amount(row.get("valor"))
                base_amount = _as_amount(base.get("valor"))
                if abs(edited_amount - base_amount) > 0.0001 and edited_amount > 0:
                    changes["amount"] = edited_amount

            if "conta" in edited.columns and not _same_text(row.get("conta"), base.get("conta")):
                account_id = account_ids.get(str(row.get("conta")))
                if account_id:
                    changes["account_id"] = account_id

            if "status" in edited.columns and not _same_text(row.get("status"), base.get("status")):
                status = status_map.get(str(row.get("status")))
                if status:
                    changes["status"] = status

            if not changes:
                continue

            try:
                repository.update_transaction(user_id, transaction_id, **changes)
                saved += 1
            except Exception as exc:
                try:
                    st.toast(f"Não foi possível salvar a alteração: {exc}", icon="⚠️")
                except Exception:
                    pass

        if saved:
            try:
                st.toast(
                    "Alteração salva automaticamente." if saved == 1 else f"{saved} lançamentos atualizados.",
                    icon="✅",
                )
            except Exception:
                pass

        return edited

    st.data_editor = renova_data_editor
    st._renova_inline_transactions_patched = True


try:
    _install_repository_cache()
    _install_access_cache()
    _install_modal_chat_ux()
    _install_inline_transaction_editor()
except Exception:
    # Nenhuma otimização deve impedir o sistema de iniciar.
    pass
