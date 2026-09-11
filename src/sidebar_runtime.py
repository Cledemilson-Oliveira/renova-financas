from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


ECOSSISTEMA_RENOVA_PUBLIC_URL = "https://ecossistema-renova.streamlit.app/"


def inject_sidebar_runtime_css() -> None:
    """Refina a navegação lateral sem alterar regras financeiras ou autenticação."""
    st.markdown(
        """
        <style>
        /* Controle próprio de recolher: sempre visível e discreto. */
        .st-key-renova_sidebar_collapse{
          margin:2px 4px 10px!important;
        }
        .st-key-renova_sidebar_collapse button{
          min-height:36px!important;
          border-radius:11px!important;
          border:1px solid color-mix(in srgb,var(--rv-blue) 36%,transparent)!important;
          background:linear-gradient(135deg,var(--rv-panel),var(--rv-panel2))!important;
          color:var(--rv-text)!important;
          -webkit-text-fill-color:var(--rv-text)!important;
          box-shadow:0 6px 16px rgba(0,0,0,.10)!important;
          font-size:.67rem!important;
          font-weight:900!important;
          letter-spacing:.035em!important;
        }
        .st-key-renova_sidebar_collapse button *{
          color:var(--rv-text)!important;
          -webkit-text-fill-color:var(--rv-text)!important;
        }
        .st-key-renova_sidebar_collapse button:hover{
          border-color:var(--rv-gold)!important;
          color:var(--rv-gold)!important;
          -webkit-text-fill-color:var(--rv-gold)!important;
          transform:translateY(-1px)!important;
        }
        .st-key-renova_sidebar_collapse button:hover *{
          color:var(--rv-gold)!important;
          -webkit-text-fill-color:var(--rv-gold)!important;
        }

        /* Mantém também o controle nativo identificável quando o Streamlit o expõe. */
        [data-testid="stSidebarCollapseButton"]{
          opacity:1!important;
          visibility:visible!important;
          pointer-events:auto!important;
          z-index:100001!important;
        }
        [data-testid="stSidebarCollapseButton"] button{
          opacity:1!important;
          visibility:visible!important;
        }

        /* Cartão do usuário: identidade, plano e papel ficam legíveis em qualquer tema. */
        .sidebar-profile-card{
          position:relative!important;
          margin:8px 4px 16px!important;
          padding:17px 14px 14px!important;
          border-radius:18px!important;
          border:1px solid color-mix(in srgb,var(--rv-blue) 26%,transparent)!important;
          background:
            radial-gradient(circle at 96% 5%,color-mix(in srgb,var(--rv-blue) 12%,transparent),transparent 34%),
            linear-gradient(145deg,var(--rv-panel),var(--rv-panel2))!important;
          box-shadow:0 12px 28px rgba(0,0,0,.13)!important;
          overflow:hidden!important;
        }
        .sidebar-profile-card:before{
          content:"MINHA CONTA";
          display:block;
          margin-bottom:10px;
          color:var(--rv-blue)!important;
          font-size:.52rem;
          font-weight:950;
          letter-spacing:.15em;
        }
        .sidebar-profile-card:after{
          content:"";
          position:absolute;
          left:0;right:0;bottom:0;height:2px;
          background:linear-gradient(90deg,transparent,var(--rv-blue),var(--rv-gold),transparent);
          opacity:.75;
        }
        .sidebar-profile-top{gap:12px!important}
        .sidebar-profile-avatar,.sidebar-profile-avatar-img{
          width:54px!important;height:54px!important;min-width:54px!important;
          flex:0 0 54px!important;
          border:2px solid color-mix(in srgb,var(--rv-gold) 74%,transparent)!important;
          box-shadow:0 0 18px color-mix(in srgb,var(--rv-blue) 22%,transparent)!important;
        }
        .sidebar-profile-name{
          color:var(--rv-text)!important;
          font-size:.96rem!important;
          font-weight:950!important;
          line-height:1.18!important;
          letter-spacing:-.015em!important;
        }
        .sidebar-profile-email{
          color:var(--rv-muted)!important;
          font-size:.64rem!important;
          line-height:1.35!important;
          margin-top:4px!important;
        }
        .sidebar-profile-chips{gap:6px!important;margin-top:12px!important}
        .sidebar-profile-chip{
          color:var(--rv-blue)!important;
          background:color-mix(in srgb,var(--rv-blue) 8%,transparent)!important;
          border-color:color-mix(in srgb,var(--rv-blue) 23%,transparent)!important;
          font-size:.54rem!important;
          font-weight:900!important;
        }
        .sidebar-profile-chip.gold{
          color:var(--rv-gold2)!important;
          background:color-mix(in srgb,var(--rv-gold) 9%,transparent)!important;
          border-color:color-mix(in srgb,var(--rv-gold) 26%,transparent)!important;
        }

        /* Assinatura institucional do produto. */
        .renova-product-card{
          margin:8px 4px 14px;
          padding:13px;
          border-radius:16px;
          border:1px solid color-mix(in srgb,var(--rv-blue) 20%,transparent);
          background:linear-gradient(145deg,var(--rv-panel),var(--rv-panel2));
          box-shadow:0 9px 22px rgba(0,0,0,.09);
        }
        .renova-product-kicker{
          color:var(--rv-gold2);
          font-size:.50rem;
          font-weight:950;
          letter-spacing:.14em;
          margin-bottom:6px;
        }
        .renova-product-title{
          color:var(--rv-text);
          font-size:.78rem;
          font-weight:950;
          line-height:1.2;
        }
        .renova-product-subtitle{
          color:var(--rv-muted);
          font-size:.60rem;
          margin-top:3px;
          line-height:1.35;
        }
        .renova-product-grid{
          display:grid;
          grid-template-columns:1fr 1fr;
          gap:6px;
          margin-top:10px;
        }
        .renova-product-cell{
          min-width:0;
          padding:8px;
          border-radius:10px;
          border:1px solid color-mix(in srgb,var(--rv-blue) 13%,transparent);
          background:color-mix(in srgb,var(--rv-blue) 4%,transparent);
        }
        .renova-product-cell span{
          display:block;
          color:var(--rv-muted);
          font-size:.47rem;
          font-weight:850;
          letter-spacing:.04em;
        }
        .renova-product-cell strong{
          display:block;
          color:var(--rv-text);
          font-size:.57rem;
          line-height:1.3;
          margin-top:3px;
          word-break:break-word;
        }
        .renova-ecosystem-link{
          display:flex;
          align-items:center;
          justify-content:center;
          min-height:31px;
          margin-top:9px;
          padding:0 9px;
          border-radius:9px;
          text-decoration:none!important;
          color:var(--rv-muted)!important;
          border:1px solid color-mix(in srgb,var(--rv-blue) 18%,transparent);
          background:transparent;
          font-size:.55rem;
          font-weight:900;
          transition:.18s ease;
        }
        .renova-ecosystem-link:hover{
          color:var(--rv-blue)!important;
          border-color:color-mix(in srgb,var(--rv-blue) 42%,transparent);
          background:color-mix(in srgb,var(--rv-blue) 6%,transparent);
          transform:translateY(-1px);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_collapse_control(st_ref=st) -> None:
    with st_ref.container(key="renova_sidebar_collapse"):
        if st_ref.button(
            "◀ RECOLHER MENU",
            key="renova_sidebar_collapse_button",
            use_container_width=True,
            help="Recolher a navegação e ampliar a área de trabalho",
        ):
            auto_collapse_sidebar_robust()


def render_ecosystem_product_card(st_ref=st) -> None:
    st_ref.markdown(
        f"""
        <section class="renova-product-card" aria-label="Produto do Ecossistema RENOVA">
          <div class="renova-product-kicker">PRODUTO OFICIAL</div>
          <div class="renova-product-title">RENOVA Finanças</div>
          <div class="renova-product-subtitle">Uma solução integrada ao Ecossistema RENOVA.</div>
          <div class="renova-product-grid">
            <div class="renova-product-cell">
              <span>DESENVOLVIDO POR</span>
              <strong>Cledemilson Oliveira</strong>
            </div>
            <div class="renova-product-cell">
              <span>ECOSSISTEMA</span>
              <strong>RENOVA</strong>
            </div>
          </div>
          <a class="renova-ecosystem-link" href="{ECOSSISTEMA_RENOVA_PUBLIC_URL}" target="_blank" rel="noopener noreferrer">
            Conhecer o Ecossistema RENOVA ↗
          </a>
        </section>
        """,
        unsafe_allow_html=True,
    )


def auto_collapse_sidebar_robust() -> None:
    """Recolhe a sidebar após a navegação usando seletores resilientes do Streamlit."""
    components.html(
        """
        <script>
        (function () {
          const doc = window.parent.document;

          function isSidebarVisible(sidebar) {
            if (!sidebar) return false;
            const rect = sidebar.getBoundingClientRect();
            const style = window.parent.getComputedStyle(sidebar);
            return rect.width > 60 && style.visibility !== 'hidden' && style.display !== 'none';
          }

          function findCollapseButton(sidebar) {
            const selectors = [
              '[data-testid="stSidebarCollapseButton"] button',
              '[data-testid="stSidebarCollapseButton"]',
              '[data-testid="stSidebar"] button[aria-label*="collapse" i]',
              '[data-testid="stSidebar"] button[aria-label*="close" i]',
              '[data-testid="stSidebar"] button[aria-label*="sidebar" i]',
              '[data-testid="stSidebar"] button[title*="collapse" i]',
              '[data-testid="stSidebar"] button[title*="close" i]'
            ];

            for (const selector of selectors) {
              const candidate = doc.querySelector(selector);
              if (!candidate) continue;
              if (candidate.tagName === 'BUTTON') return candidate;
              const nested = candidate.querySelector && candidate.querySelector('button');
              if (nested) return nested;
            }

            const buttons = Array.from(sidebar.querySelectorAll('button'));
            return buttons.find((button) => {
              const text = [
                button.getAttribute('aria-label') || '',
                button.getAttribute('title') || '',
                button.textContent || ''
              ].join(' ').toLowerCase();
              return /(collapse|close|sidebar|recolher|fechar)/i.test(text);
            }) || null;
          }

          function collapse() {
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (!isSidebarVisible(sidebar)) return;
            const button = findCollapseButton(sidebar);
            if (button) button.click();
          }

          // O rerun do Streamlit pode reposicionar o botão; tentativas espaçadas
          // mantêm a ação confiável sem reabrir a sidebar já recolhida.
          [100, 320, 680].forEach((delay) => setTimeout(collapse, delay));
        })();
        </script>
        """,
        height=0,
        width=0,
    )
