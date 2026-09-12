"""Otimizações transparentes de performance para o RENOVA Finanças.

O Streamlit reexecuta o script a cada interação de widget. Sem uma camada de
cache, marcar um checkbox ou alterar um filtro pode disparar novamente todas as
consultas financeiras no Supabase. Este módulo é carregado automaticamente pelo
Python e aplica um cache curto, por usuário, apenas às leituras.

Toda operação de escrita conhecida invalida imediatamente o cache do usuário,
portanto adicionar, editar ou excluir dados continua refletindo no próximo
rerun. O cache também expira sozinho em poucos segundos para não esconder
alterações feitas em outra sessão/dispositivo por muito tempo.
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
                # O app transforma alguns DataFrames localmente. Entregar uma
                # cópia evita que um rerun contamine o snapshot compartilhado.
                return deepcopy(cached[1])

        data = original_fetch(user_id)
        with _LOCK:
            _FINANCIAL_CACHE[cache_key] = (monotonic(), deepcopy(data))
        return data

    cached_fetch_financial_data._renova_cached = True  # type: ignore[attr-defined]
    repository.fetch_financial_data = cached_fetch_financial_data

    # Funções de escrita usadas pelo app e pela IA. O primeiro argumento de
    # todas elas é o user_id; após sucesso, invalidamos somente aquele usuário.
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
        # Atualmente a chamada do app não recebe argumentos. Ainda assim, a
        # chave considera args/kwargs para permanecer segura se a função evoluir.
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


try:
    _install_repository_cache()
    _install_access_cache()
except Exception:
    # Performance nunca deve impedir o sistema de iniciar. Em qualquer cenário
    # inesperado, o app continua funcionando com o comportamento original.
    pass
