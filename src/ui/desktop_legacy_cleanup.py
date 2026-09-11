from __future__ import annotations

import streamlit.components.v1 as components


def cleanup_legacy_desktop_runtime() -> None:
    """Desliga o antigo menu DOM antes de instalar o shell desktop novo."""
    components.html(
        """
        <script>
        (function () {
          const win = window.parent;
          const doc = win.document;

          try {
            if (win.__renovaFinanceSidebarObserver) {
              win.__renovaFinanceSidebarObserver.disconnect();
              win.__renovaFinanceSidebarObserver = null;
            }
            if (win.__renovaFinanceSidebarResizeHandler) {
              win.removeEventListener('resize', win.__renovaFinanceSidebarResizeHandler);
              win.__renovaFinanceSidebarResizeHandler = null;
            }
            win.__renovaFinanceSidebarRefresh = null;
            win.__renovaFinanceSidebarInitialized = false;
          } catch (e) {}

          const legacyNav = doc.getElementById('renova-fin-grouped-nav');
          if (legacyNav) legacyNav.remove();

          // Os controles são recriados pelo shell v4 com listeners limpos.
          const oldOpen = doc.getElementById('renova-fin-sidebar-open');
          if (oldOpen) oldOpen.remove();
          const oldClose = doc.getElementById('renova-fin-sidebar-close');
          if (oldClose) oldClose.remove();

          doc.body.classList.remove('renova-fin-sidebar-closed');
        })();
        </script>
        """,
        height=0,
        width=0,
    )
