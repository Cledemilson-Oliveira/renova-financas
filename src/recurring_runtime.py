from __future__ import annotations

import pandas as pd

from src.recurring_finance import list_recurring_plans, materialize_due_recurring


def install_recurring_runtime(repository_module) -> None:
    """Acopla recorrências ao carregamento financeiro sem alterar o app principal."""
    if getattr(repository_module, "_renova_recurring_runtime_installed", False):
        return

    original_fetch = repository_module.fetch_financial_data

    def fetch_with_recurring(user_id: str):
        try:
            materialize_due_recurring(user_id)
        except Exception:
            # A leitura financeira não deve cair se a materialização automática
            # estiver temporariamente indisponível. A tela de planejamento expõe
            # erros operacionais de forma explícita ao usuário.
            pass

        bundle = original_fetch(user_id)
        try:
            bundle["recurring"] = list_recurring_plans(user_id, include_inactive=True)
        except Exception:
            bundle["recurring"] = pd.DataFrame()
        return bundle

    repository_module.fetch_financial_data = fetch_with_recurring
    repository_module._renova_recurring_runtime_installed = True
