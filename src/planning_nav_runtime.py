from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


def install_planning_navigation_runtime(theme_module) -> None:
    """Adiciona Planejamento de Caixa ao menu mobile preservando a sessão Streamlit."""
    if getattr(theme_module, "_renova_planning_navigation_installed", False):
        return

    original_install_mobile_navigation = theme_module.install_mobile_navigation

    def install_mobile_navigation_with_planning() -> None:
        original_install_mobile_navigation()

        # Links nativos do Streamlit mantêm a mesma sessão. Eles ficam invisíveis
        # e são acionados pelo controle mobile customizado, evitando full reload.
        with st.container(key="renova_planning_native_link"):
            st.page_link("pages/Planejamento_Caixa.py", label="Planejamento de Caixa")
        with st.container(key="renova_panel_native_link"):
            st.page_link("app.py", label="Painel")

        components.html(
            """
            <script>
            (function () {
              const win = window.parent;
              const doc = win.document;
              const OPTION_VALUE = '__renova_cash_planning__';
              const LABEL = '📈  Planejamento de Caixa';
              const MOBILE_MAX = 900;

              function isMobile() {
                return win.innerWidth <= MOBILE_MAX;
              }

              function isPlanningPage() {
                return /Planejamento_Caixa/i.test(win.location.pathname || '');
              }

              function nativeNavigate(selector) {
                const link = doc.querySelector(selector + ' a');
                if (!link) return false;
                link.click();
                return true;
              }

              function ensureStyles() {
                if (doc.getElementById('renova-planning-nav-style')) return;
                const style = doc.createElement('style');
                style.id = 'renova-planning-nav-style';
                style.textContent = `
                  .st-key-renova_planning_native_link,
                  .st-key-renova_panel_native_link{display:none!important}
                  #renova-planning-mobile-bar{display:none}
                  @media(max-width:900px){
                    body.renova-planning-page #renova-planning-mobile-bar{
                      display:flex;position:fixed;top:8px;left:8px;right:8px;z-index:10060;
                      align-items:center;justify-content:space-between;gap:10px;
                      min-height:56px;padding:8px 10px;border-radius:16px;
                      border:1px solid rgba(255,215,90,.45);
                      background:linear-gradient(135deg,#071C2D,#0A2A48 58%,#03101A);
                      box-shadow:0 16px 38px rgba(0,0,0,.35),0 0 22px rgba(0,174,239,.18);
                    }
                    body.renova-planning-page #renova-planning-mobile-bar button{
                      display:inline-flex;align-items:center;justify-content:center;min-height:40px;
                      padding:0 12px;border-radius:11px;cursor:pointer;
                      color:#F7FBFF!important;font-size:.78rem;font-weight:900;
                      border:1px solid rgba(0,174,239,.45);background:#06131F;
                    }
                    body.renova-planning-page #renova-planning-mobile-bar strong{
                      color:#FFD75A;font-size:.76rem;font-weight:950;text-align:right;
                    }
                    body.renova-planning-page [data-testid="stMainBlockContainer"]{
                      padding-top:5.8rem!important;
                    }
                  }
                `;
                doc.head.appendChild(style);
              }

              function ensurePlanningPageBar() {
                if (!isPlanningPage() || !isMobile()) {
                  doc.body.classList.remove('renova-planning-page');
                  const old = doc.getElementById('renova-planning-mobile-bar');
                  if (old) old.remove();
                  return;
                }
                doc.body.classList.add('renova-planning-page');
                let bar = doc.getElementById('renova-planning-mobile-bar');
                if (!bar) {
                  bar = doc.createElement('div');
                  bar.id = 'renova-planning-mobile-bar';
                  bar.innerHTML = '<button type="button" id="renova-planning-back">← Painel</button><strong>📈 Planejamento<br>de Caixa</strong>';
                  doc.body.appendChild(bar);
                }
                const back = doc.getElementById('renova-planning-back');
                if (back && back.dataset.bound !== '1') {
                  back.addEventListener('click', function () {
                    nativeNavigate('.st-key-renova_panel_native_link');
                  });
                  back.dataset.bound = '1';
                }
              }

              function addPlanningOption() {
                if (!isMobile() || isPlanningPage()) return;
                const select = doc.querySelector('#renova-mobile-nav-select');
                if (!select) return;

                let option = Array.from(select.options).find((item) => item.value === OPTION_VALUE);
                if (!option) {
                  option = doc.createElement('option');
                  option.value = OPTION_VALUE;
                  option.textContent = LABEL;
                  select.appendChild(option);
                }

                if (select.dataset.planningBound !== '1') {
                  select.addEventListener('change', function () {
                    if (select.value === OPTION_VALUE) {
                      nativeNavigate('.st-key-renova_planning_native_link');
                    }
                  });
                  select.dataset.planningBound = '1';
                }
              }

              function sync() {
                ensureStyles();
                ensurePlanningPageBar();
                addPlanningOption();
              }

              sync();
              [120, 350, 700, 1200, 2200, 4200, 7000, 10500].forEach((delay) => setTimeout(sync, delay));
              win.addEventListener('resize', sync);
            })();
            </script>
            """,
            height=0,
            width=0,
        )

    theme_module.install_mobile_navigation = install_mobile_navigation_with_planning
    theme_module._renova_planning_navigation_installed = True
