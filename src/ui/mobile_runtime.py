from __future__ import annotations

from typing import Any, Callable

import streamlit.components.v1 as components

from .mobile import (
    apply_mobile_styles,
    mobile_plotly_config,
    render_dataframe_mobile,
    tune_plotly_mobile,
)


def _cleanup_desktop_shell_artifacts() -> None:
    """Remove resíduos do shell desktop quando a sessão está em modo mobile.

    O Streamlit reaproveita o DOM entre reruns. Se o usuário redimensionar a tela
    ou abrir a mesma sessão em um WebView móvel, controles injetados pelo desktop
    podem permanecer na árvore mesmo depois da troca de layout. O cleanup evita
    a mistura de navegação e também elimina o principal ponto de vazamento visual
    observado no painel mobile.
    """
    components.html(
        """
        <script>
        (function () {
          const win = window.parent;
          const doc = win.document;

          function cleanup() {
            doc.body.classList.remove('renova-fin-sidebar-closed');
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
    return render_dataframe_mobile(original, data, *args, **kwargs)


def prepare_plotly_mobile(
    figure_or_data: Any,
    config: dict[str, Any] | None = None,
) -> tuple[Any, dict[str, Any]]:
    figure_or_data = tune_plotly_mobile(figure_or_data)
    return figure_or_data, mobile_plotly_config(config)
