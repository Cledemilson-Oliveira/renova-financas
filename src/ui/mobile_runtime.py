from __future__ import annotations

from html import escape
from typing import Any, Callable

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from .mobile import (
    _date_text,
    _money_text,
    apply_mobile_styles,
    mobile_plotly_config,
    render_dataframe_mobile,
    tune_plotly_mobile,
)


def _cleanup_desktop_shell_artifacts() -> None:
    """Remove e desliga qualquer runtime desktop em sessões mobile."""
    components.html(
        """
        <script>
        (function () {
          const win = window.parent;
          const doc = win.document;

          function cleanup() {
            doc.body.classList.remove('renova-fin-sidebar-closed');

            try {
              if (win.__renovaFinanceSidebarObserver) {
                win.__renovaFinanceSidebarObserver.disconnect();
                win.__renovaFinanceSidebarObserver = null;
              }
              if (win.__renovaFinanceSidebarResizeHandler) {
                win.removeEventListener('resize', win.__renovaFinanceSidebarResizeHandler);
                win.__renovaFinanceSidebarResizeHandler = null;
              }
              if (win.__renovaFinDesktopShellObserverV4) {
                win.__renovaFinDesktopShellObserverV4.disconnect();
                win.__renovaFinDesktopShellObserverV4 = null;
              }
              if (win.__renovaFinDesktopShellResizeV4) {
                win.removeEventListener('resize', win.__renovaFinDesktopShellResizeV4);
                win.__renovaFinDesktopShellResizeV4 = null;
              }
              win.__renovaFinanceSidebarRefresh = null;
              win.__renovaFinanceSidebarInitialized = false;
              win.__renovaFinDesktopShellV4 = false;
            } catch (e) {}

            [
              'renova-fin-sidebar-open',
              'renova-fin-sidebar-close',
              'renova-fin-grouped-nav'
            ].forEach(function (id) {
              const node = doc.getElementById(id);
              if (node) node.remove();
            });
          }

          cleanup();
          [120, 360, 900].forEach(function (delay) {
            win.setTimeout(cleanup, delay);
          });
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def _render_transaction_cards_safe(df: pd.DataFrame) -> None:
    """Renderiza lançamentos sem indentação Markdown que possa virar bloco de código."""
    cards: list[str] = []

    for _, row in df.iterrows():
        kind = str(row.get("tipo") or "")
        icon = "💰" if kind == "Receita" else "💸" if kind == "Despesa" else "🔄"
        description = escape(str(row.get("descricao") or "Lançamento"))
        value = escape(_money_text(row.get("valor")))
        when = escape(_date_text(row.get("data")))
        due = escape(_date_text(row.get("vencimento")))
        category = escape(str(row.get("categoria") or "Sem categoria"))
        account = escape(str(row.get("conta") or ""))
        status = escape(str(row.get("status") or ""))

        account_pill = (
            f'<span class="renova-mobile-pill">🏦 {account}</span>'
            if account
            else ""
        )
        due_pill = (
            f'<span class="renova-mobile-pill gold">📅 vence {due}</span>'
            if due
            else ""
        )
        status_class = " alert" if status.lower() in {"atrasado", "previsto", "pendente"} else ""
        status_pill = (
            f'<span class="renova-mobile-pill{status_class}">{status}</span>'
            if status
            else ""
        )

        # Mantido propositalmente em uma única linha. Strings HTML com quatro
        # ou mais espaços no início podem ser classificadas pelo Markdown como
        # código, mesmo quando unsafe_allow_html=True.
        card = (
            f'<article class="renova-mobile-row">'
            f'<div class="renova-mobile-row-top">'
            f'<div class="renova-mobile-row-title">{icon} {description}</div>'
            f'<div class="renova-mobile-row-value">{value}</div>'
            f'</div>'
            f'<div class="renova-mobile-row-meta">'
            f'<span class="renova-mobile-pill">📆 {when}</span>'
            f'<span class="renova-mobile-pill">🏷️ {category}</span>'
            f'{account_pill}{due_pill}{status_pill}'
            f'</div>'
            f'</article>'
        )
        cards.append(card)

    html = f'<div class="renova-mobile-list">{"".join(cards)}</div>'
    st.markdown(html, unsafe_allow_html=True)


def apply_mobile_runtime() -> None:
    """Ativa exclusivamente a camada visual do celular."""
    apply_mobile_styles()
    _cleanup_desktop_shell_artifacts()


def render_dataframe_mobile_runtime(
    original: Callable[..., Any],
    data: Any,
    *args: Any,
    **kwargs: Any,
) -> Any:
    if isinstance(data, pd.DataFrame) and not data.empty:
        columns = set(map(str, data.columns))
        if {"descricao", "valor", "tipo"}.issubset(columns):
            _render_transaction_cards_safe(data)
            return None

    return render_dataframe_mobile(original, data, *args, **kwargs)


def prepare_plotly_mobile(
    figure_or_data: Any,
    config: dict[str, Any] | None = None,
) -> tuple[Any, dict[str, Any]]:
    figure_or_data = tune_plotly_mobile(figure_or_data)
    return figure_or_data, mobile_plotly_config(config)
