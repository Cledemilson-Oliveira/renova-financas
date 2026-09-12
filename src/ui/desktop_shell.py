from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


def inject_desktop_shell() -> None:
    """Controla apenas abrir/recolher da sidebar no desktop.

    A navegação fica em componentes Streamlit nativos, em outro módulo. Este
    shell não procura, não oculta e não clica em radios do menu.
    """
    st.markdown(
        """
        <style>
        @media (min-width:901px){
          [data-testid="stSidebarCollapseButton"],
          [data-testid="stSidebarCollapsedControl"],
          [data-testid="collapsedControl"]{
            display:none!important;
            visibility:hidden!important;
            opacity:0!important;
            pointer-events:none!important;
          }

          [data-testid="stSidebar"]{
            display:block!important;
            visibility:visible!important;
            min-width:278px!important;
            max-width:278px!important;
            width:278px!important;
            margin:0!important;
            border:0!important;
            transform:none!important;
          }
          [data-testid="stSidebar"]>div:first-child{
            min-width:278px!important;
            max-width:278px!important;
            width:278px!important;
          }

          body.renova-fin-sidebar-closed [data-testid="stSidebar"]{
            display:none!important;
            visibility:hidden!important;
            width:0!important;
            min-width:0!important;
            max-width:0!important;
            margin:0!important;
            padding:0!important;
            border:0!important;
            box-shadow:none!important;
          }
          body.renova-fin-sidebar-closed [data-testid="stMain"],
          body.renova-fin-sidebar-closed [data-testid="stAppViewContainer"] main,
          body.renova-fin-sidebar-closed [data-testid="stMainBlockContainer"]{
            width:100%!important;
            max-width:none!important;
            margin-left:0!important;
            margin-right:0!important;
          }

          #renova-fin-sidebar-open,
          #renova-fin-sidebar-close{
            appearance:none;
            -webkit-appearance:none;
            border:1px solid rgba(25,217,255,.64);
            font-weight:950;
            letter-spacing:.015em;
            cursor:pointer;
            transition:.18s ease;
            box-shadow:0 10px 28px rgba(0,0,0,.34),0 0 18px rgba(0,144,240,.18);
          }
          #renova-fin-sidebar-open{
            position:fixed;
            left:14px;
            top:72px;
            z-index:100050;
            min-width:154px;
            min-height:46px;
            padding:0 16px;
            border-radius:14px;
            background:linear-gradient(120deg,#0B2038 0%,#087FF5 58%,#19D9FF 100%);
            color:#fff;
            -webkit-text-fill-color:#fff;
            align-items:center;
            justify-content:center;
            gap:8px;
            font-size:.78rem;
          }
          #renova-fin-sidebar-close{
            position:sticky;
            top:8px;
            z-index:100051;
            width:calc(100% - 14px);
            min-height:42px;
            margin:7px 7px 9px;
            border-radius:13px;
            background:linear-gradient(120deg,#071725,#0b3454);
            color:#19D9FF;
            -webkit-text-fill-color:#19D9FF;
            font-size:.76rem;
          }
          #renova-fin-sidebar-open:hover,
          #renova-fin-sidebar-close:hover{
            transform:translateY(-1px);
            border-color:#A997FF;
          }

          .renova-nav-heading{
            display:flex;
            align-items:flex-end;
            justify-content:space-between;
            gap:8px;
            margin:8px 4px 10px;
            padding:0 2px;
          }
          .renova-nav-heading span{
            color:var(--rv-text);
            font-size:.69rem;
            font-weight:950;
            letter-spacing:.12em;
          }
          .renova-nav-heading small{
            color:var(--rv-muted);
            font-size:.52rem;
            font-weight:800;
          }

          [data-testid="stSidebar"] [data-testid="stExpander"]{
            margin-bottom:8px!important;
            border-radius:14px!important;
            border:1px solid color-mix(in srgb,var(--rv-blue) 20%,transparent)!important;
            background:linear-gradient(145deg,var(--rv-panel),var(--rv-panel2))!important;
            box-shadow:0 8px 20px rgba(0,0,0,.10)!important;
            overflow:hidden!important;
          }
          [data-testid="stSidebar"] [data-testid="stExpander"] summary{
            min-height:42px!important;
            font-size:.62rem!important;
            font-weight:950!important;
            letter-spacing:.07em!important;
          }
          [data-testid="stSidebar"] .stButton>button{
            min-height:43px!important;
            border-radius:12px!important;
            font-weight:850!important;
          }
        }

        @media (max-width:900px){
          #renova-fin-sidebar-open,
          #renova-fin-sidebar-close{display:none!important}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    components.html(
        """
        <script>
        (function () {
          const win = window.parent;
          const doc = win.document;
          const STORAGE_KEY = 'renova_financas_sidebar_open_v4';

          function desktop() { return win.innerWidth > 900; }
          function preferredOpen() {
            const raw = win.localStorage.getItem(STORAGE_KEY);
            return raw === null ? true : raw !== '0';
          }
          function setOpen(open) {
            if (!desktop()) return;
            doc.body.classList.toggle('renova-fin-sidebar-closed', !open);
            win.localStorage.setItem(STORAGE_KEY, open ? '1' : '0');
            refresh();
          }
          function ensureOpenButton() {
            let button = doc.getElementById('renova-fin-sidebar-open');
            if (!button) {
              button = doc.createElement('button');
              button.id = 'renova-fin-sidebar-open';
              button.type = 'button';
              button.setAttribute('aria-label', 'Abrir menu RENOVA Finanças');
              button.innerHTML = '<span aria-hidden="true">☰</span><span>ABRIR MENU</span>';
              button.addEventListener('click', function () { setOpen(true); });
              doc.body.appendChild(button);
            }
            return button;
          }
          function ensureCloseButton() {
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return null;
            const host = sidebar.firstElementChild || sidebar;
            let button = host.querySelector('#renova-fin-sidebar-close');
            if (!button) {
              button = doc.createElement('button');
              button.id = 'renova-fin-sidebar-close';
              button.type = 'button';
              button.setAttribute('aria-label', 'Recolher menu RENOVA Finanças');
              button.textContent = '◀ RECOLHER MENU';
              button.addEventListener('click', function () { setOpen(false); });
              host.insertBefore(button, host.firstChild);
            }
            return button;
          }
          function cleanupLegacyNav() {
            const old = doc.getElementById('renova-fin-grouped-nav');
            if (old) old.remove();
          }
          function refresh() {
            cleanupLegacyNav();
            if (!desktop()) {
              doc.body.classList.remove('renova-fin-sidebar-closed');
              const open = doc.getElementById('renova-fin-sidebar-open');
              const close = doc.getElementById('renova-fin-sidebar-close');
              if (open) open.style.display = 'none';
              if (close) close.style.display = 'none';
              return;
            }
            if (!win.__renovaFinDesktopShellV4) {
              doc.body.classList.toggle('renova-fin-sidebar-closed', !preferredOpen());
              win.__renovaFinDesktopShellV4 = true;
            }
            const isOpen = !doc.body.classList.contains('renova-fin-sidebar-closed');
            const open = ensureOpenButton();
            const close = ensureCloseButton();
            if (open) open.style.display = isOpen ? 'none' : 'flex';
            if (close) close.style.display = isOpen ? 'block' : 'none';
          }

          if (!win.__renovaFinDesktopShellObserverV4) {
            win.__renovaFinDesktopShellObserverV4 = new MutationObserver(function () {
              win.requestAnimationFrame(refresh);
            });
            win.__renovaFinDesktopShellObserverV4.observe(doc.body, {childList:true, subtree:true});
          }
          if (!win.__renovaFinDesktopShellResizeV4) {
            win.__renovaFinDesktopShellResizeV4 = function () {
              if (!desktop()) doc.body.classList.remove('renova-fin-sidebar-closed');
              refresh();
            };
            win.addEventListener('resize', win.__renovaFinDesktopShellResizeV4);
          }

          refresh();
          [120, 350, 800].forEach(function (delay) { win.setTimeout(refresh, delay); });
        })();
        </script>
        """,
        height=0,
        width=0,
    )
