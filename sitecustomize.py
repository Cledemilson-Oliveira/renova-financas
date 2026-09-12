"""Otimizações transparentes de performance e UX para o RENOVA Finanças.

O Streamlit reexecuta o script a cada interação de widget. Sem uma camada de
cache, marcar um checkbox ou alterar um filtro pode disparar novamente todas as
consultas financeiras no Supabase. Este módulo é carregado automaticamente pelo
Python e aplica um cache curto, por usuário, apenas às leituras.

Também ajusta especificamente o chat modal do Assistente Financeiro IA para ter
comportamento de aplicativo de mensagens: histórico rolável, campo de entrada
preso ao rodapé e posicionamento automático na mensagem mais recente.
"""

from __future__ import annotations

from copy import deepcopy
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
    /* Janela do Assistente Financeiro IA */
    div[role="dialog"] {
      height: min(820px, 88vh) !important;
      max-height: 88vh !important;
      overflow-y: auto !important;
      overscroll-behavior: contain !important;
      scrollbar-gutter: stable !important;
      padding-bottom: 0 !important;
    }

    /* Mantém o campo de digitação sempre visível no rodapé. */
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

    /* Reserva espaço para a última mensagem não ficar escondida atrás do input. */
    div[role="dialog"] [data-testid="stChatMessage"]:last-of-type {
      margin-bottom: 20px !important;
    }

    /* O topo do diálogo permanece disponível enquanto o histórico rola. */
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


try:
    _install_repository_cache()
    _install_access_cache()
    _install_modal_chat_ux()
except Exception:
    # Nenhuma otimização deve impedir o sistema de iniciar.
    pass
