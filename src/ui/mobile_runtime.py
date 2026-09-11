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
