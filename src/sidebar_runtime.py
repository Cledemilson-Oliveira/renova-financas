from __future__ import annotations

import json

import streamlit as st
import streamlit.components.v1 as components


ECOSSISTEMA_RENOVA_PUBLIC_URL = "https://ecossistema-renova.streamlit.app/"

# Mantém os mesmos destinos já usados pelo app. O runtime apenas organiza a
# apresentação, sem criar uma segunda fonte de verdade para a navegação.
_NAV_GROUPS = [
    ("🏠 INÍCIO", ["Dashboard"]),
    ("💸 MOVIMENTAÇÕES", ["Lançamentos", "Categorias"]),
    ("🏦 CONTAS E CRÉDITO", ["Contas", "Cartões"]),
    ("📊 PLANEJAMENTO", ["Orçamentos", "Análises", "Relatórios"]),
    ("🤖 RENOVA IA", ["RENOVA IA", "Treinamento IA", "Assinar RENOVA IA"]),
]

_NAV_ICONS = {
    "Dashboard": "⌂",
    "Lançamentos": "↕",
    "Categorias": "◫",
    "Contas": "▣",
    "Cartões": "▤",
    "Orçamentos": "◎",
    "Análises": "◈",
    "Relatórios": "▥",
    "RENOVA IA": "✦",
    "Treinamento IA": "◇",
    "Assinar RENOVA IA": "★",
}


def inject_sidebar_runtime_css() -> None:
    """Instala o shell lateral desktop no padrão do ERP RENOVA.

    O estado de abrir/fechar fica no DOM/localStorage em vez de depender do
    controle nativo do Streamlit. Isso elimina os dois botões de recolher,
    remove a faixa vazia ao fechar e mantém um botão próprio para reabrir.
    """
    st.markdown(
        """
        <style>
        @media (min-width:901px){
          /* Existe uma única fonte visual para abrir/recolher a sidebar. */
          [data-testid="stSidebarCollapseButton"],
          [data-testid="stSidebarCollapsedControl"],
          [data-testid="collapsedControl"]{
            display:none!important;
            visibility:hidden!important;
            opacity:0!important;
            pointer-events:none!important;
          }

          /* Sidebar aberta. */
          [data-testid="stSidebar"]{
            display:block!important;
            visibility:visible!important;
            min-width:278px!important;
            max-width:278px!important;
            width:278px!important;
            transform:none!important;
            margin:0!important;
            border:0!important;
          }
          [data-testid="stSidebar"]>div:first-child{
            min-width:278px!important;
            max-width:278px!important;
            width:278px!important;
          }

          /* Sidebar fechada: não reserva coluna/flex-basis. */
          body.renova-fin-sidebar-closed [data-testid="stSidebar"]{
            display:none!important;
            visibility:hidden!important;
            min-width:0!important;
            max-width:0!important;
            width:0!important;
            margin:0!important;
            padding:0!important;
            border:0!important;
            box-shadow:none!important;
          }
          body.renova-fin-sidebar-closed [data-testid="stMain"],
          body.renova-fin-sidebar-closed [data-testid="stAppViewContainer"] main{
            width:100%!important;
            max-width:none!important;
            margin-left:0!important;
          }
          body.renova-fin-sidebar-closed [data-testid="stMainBlockContainer"]{
            width:100%!important;
            max-width:none!important;
            margin-left:0!important;
            margin-right:0!important;
          }

          /* Controles próprios — mesma linguagem visual do ERP RENOVA. */
          #renova-fin-sidebar-open,
          #renova-fin-sidebar-close{
            appearance:none;
            -webkit-appearance:none;
            border:1px solid rgba(247,214,100,.88);
            background:linear-gradient(120deg,#061827 0%,#07508a 65%,#0090f0 100%);
            color:#fff;
            -webkit-text-fill-color:#fff;
            font-weight:950;
            letter-spacing:.015em;
            cursor:pointer;
            box-shadow:0 10px 28px rgba(0,0,0,.38),0 0 18px rgba(0,144,240,.22);
            transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease;
          }
          #renova-fin-sidebar-open:hover,
          #renova-fin-sidebar-close:hover{
            transform:translateY(-1px);
            border-color:#fff0a3;
            box-shadow:0 12px 32px rgba(0,0,0,.42),0 0 22px rgba(247,214,100,.18);
          }
          #renova-fin-sidebar-open:focus-visible,
          #renova-fin-sidebar-close:focus-visible{
            outline:3px solid rgba(247,214,100,.72);
            outline-offset:2px;
          }
          #renova-fin-sidebar-open{
            position:fixed;
            left:14px;
            top:72px;
            z-index:100050;
            min-height:46px;
            min-width:154px;
            padding:0 16px;
            border-radius:14px;
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
            color:#ffe477;
            -webkit-text-fill-color:#ffe477;
            font-size:.76rem;
          }

          /* O rádio original continua no DOM como fonte de verdade e para o
             menu mobile, porém no desktop usamos a navegação agrupada. */
          [data-testid="stSidebar"] [data-testid="stRadio"]{
            position:absolute!important;
            width:1px!important;
            height:1px!important;
            overflow:hidden!important;
            opacity:0!important;
            pointer-events:none!important;
            margin:0!important;
            padding:0!important;
          }

          #renova-fin-grouped-nav{
            margin:5px 4px 14px;
          }
          #renova-fin-grouped-nav .rv-nav-title{
            display:flex;
            align-items:flex-end;
            justify-content:space-between;
            gap:8px;
            margin:3px 4px 9px;
            padding:0 2px;
          }
          #renova-fin-grouped-nav .rv-nav-title span{
            color:var(--rv-text);
            font-size:.69rem;
            font-weight:950;
            letter-spacing:.12em;
          }
          #renova-fin-grouped-nav .rv-nav-title small{
            color:var(--rv-muted);
            font-size:.52rem;
            font-weight:800;
          }
          #renova-fin-grouped-nav details{
            margin:0 0 8px;
            overflow:hidden;
            border:1px solid color-mix(in srgb,var(--rv-blue) 20%,transparent);
            border-radius:14px;
            background:linear-gradient(145deg,var(--rv-panel),var(--rv-panel2));
            box-shadow:0 8px 20px rgba(0,0,0,.10);
          }
          #renova-fin-grouped-nav summary{
            list-style:none;
            min-height:42px;
            display:flex;
            align-items:center;
            padding:0 12px;
            cursor:pointer;
            color:var(--rv-muted);
            font-size:.62rem;
            font-weight:950;
            letter-spacing:.09em;
            user-select:none;
          }
          #renova-fin-grouped-nav summary::-webkit-details-marker{display:none}
          #renova-fin-grouped-nav summary:after{
            content:"⌄";
            margin-left:auto;
            color:var(--rv-gold2);
            font-size:.86rem;
            transition:transform .18s ease;
          }
          #renova-fin-grouped-nav details[open] summary:after{transform:rotate(180deg)}
          #renova-fin-grouped-nav .rv-nav-items{
            display:grid;
            gap:6px;
            padding:0 7px 8px;
          }
          #renova-fin-grouped-nav .rv-nav-item{
            width:100%;
            min-height:43px;
            display:flex;
            align-items:center;
            gap:9px;
            padding:0 11px;
            border-radius:12px;
            border:1px solid color-mix(in srgb,var(--rv-blue) 18%,transparent);
            background:color-mix(in srgb,var(--rv-blue) 4%,var(--rv-panel));
            color:var(--rv-text);
            -webkit-text-fill-color:var(--rv-text);
            cursor:pointer;
            text-align:left;
            font-size:.76rem;
            font-weight:850;
            transition:transform .16s ease,border-color .16s ease,background .16s ease,box-shadow .16s ease;
          }
          #renova-fin-grouped-nav .rv-nav-item:hover{
            transform:translateX(4px);
            border-color:color-mix(in srgb,var(--rv-blue) 58%,transparent);
            background:color-mix(in srgb,var(--rv-blue) 9%,var(--rv-panel));
            box-shadow:0 8px 18px rgba(0,0,0,.12);
          }
          #renova-fin-grouped-nav .rv-nav-item.active{
            border-color:rgba(247,214,100,.76);
            background:linear-gradient(120deg,color-mix(in srgb,var(--rv-gold) 11%,var(--rv-panel)),var(--rv-panel2));
            color:var(--rv-gold2);
            -webkit-text-fill-color:var(--rv-gold2);
            box-shadow:0 8px 20px rgba(0,0,0,.14),0 0 16px rgba(247,214,100,.08);
          }
          #renova-fin-grouped-nav .rv-nav-icon{
            width:18px;
            min-width:18px;
            color:var(--rv-blue);
            -webkit-text-fill-color:var(--rv-blue);
            font-size:.89rem;
            font-weight:950;
            text-align:center;
          }
          #renova-fin-grouped-nav .rv-nav-item.active .rv-nav-icon{
            color:var(--rv-gold2);
            -webkit-text-fill-color:var(--rv-gold2);
          }

          /* O antigo botão Python deixou de ser necessário. */
          .st-key-renova_sidebar_collapse{display:none!important}

          /* Perfil continua com o padrão visual premium. */
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
        }

        /* Cartão institucional permanece disponível dentro de "Sistema". */
        .renova-product-card{
          margin:8px 0 4px;
          padding:13px;
          border-radius:14px;
          border:1px solid color-mix(in srgb,var(--rv-blue) 20%,transparent);
          background:linear-gradient(145deg,var(--rv-panel),var(--rv-panel2));
          box-shadow:0 9px 22px rgba(0,0,0,.09);
        }
        .renova-product-kicker{
          color:var(--rv-gold2);font-size:.50rem;font-weight:950;letter-spacing:.14em;margin-bottom:6px
        }
        .renova-product-title{color:var(--rv-text);font-size:.78rem;font-weight:950;line-height:1.2}
        .renova-product-subtitle{color:var(--rv-muted);font-size:.60rem;margin-top:3px;line-height:1.35}
        .renova-product-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:10px}
        .renova-product-cell{
          min-width:0;padding:8px;border-radius:10px;
          border:1px solid color-mix(in srgb,var(--rv-blue) 13%,transparent);
          background:color-mix(in srgb,var(--rv-blue) 4%,transparent)
        }
        .renova-product-cell span{
          display:block;color:var(--rv-muted);font-size:.47rem;font-weight:850;letter-spacing:.04em
        }
        .renova-product-cell strong{
          display:block;color:var(--rv-text);font-size:.57rem;line-height:1.3;margin-top:3px;word-break:break-word
        }
        .renova-ecosystem-link{
          display:flex;align-items:center;justify-content:center;min-height:31px;margin-top:9px;padding:0 9px;
          border-radius:9px;text-decoration:none!important;color:var(--rv-muted)!important;
          border:1px solid color-mix(in srgb,var(--rv-blue) 18%,transparent);
          background:transparent;font-size:.55rem;font-weight:900;transition:.18s ease
        }
        .renova-ecosystem-link:hover{
          color:var(--rv-blue)!important;border-color:color-mix(in srgb,var(--rv-blue) 42%,transparent);
          background:color-mix(in srgb,var(--rv-blue) 6%,transparent);transform:translateY(-1px)
        }

        @media (max-width:900px){
          #renova-fin-sidebar-open,
          #renova-fin-sidebar-close,
          #renova-fin-grouped-nav{display:none!important}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    groups_js = json.dumps(_NAV_GROUPS, ensure_ascii=False)
    icons_js = json.dumps(_NAV_ICONS, ensure_ascii=False)
    components.html(
        f"""
        <script>
        (function () {{
          const win = window.parent;
          const doc = win.document;
          const STORAGE_KEY = 'renova_financas_sidebar_open_v3';
          const GROUPS = {groups_js};
          const ICONS = {icons_js};

          function desktop() {{
            return win.innerWidth > 900;
          }}

          function getOpenPreference() {{
            const raw = win.localStorage.getItem(STORAGE_KEY);
            return raw === null ? true : raw !== '0';
          }}

          function setOpen(open) {{
            if (!desktop()) return;
            doc.body.classList.toggle('renova-fin-sidebar-closed', !open);
            win.localStorage.setItem(STORAGE_KEY, open ? '1' : '0');
            refreshControls();
          }}

          function ensureOpenControl() {{
            let button = doc.getElementById('renova-fin-sidebar-open');
            if (!button) {{
              button = doc.createElement('button');
              button.id = 'renova-fin-sidebar-open';
              button.type = 'button';
              button.setAttribute('aria-label', 'Abrir menu RENOVA Finanças');
              button.innerHTML = '<span aria-hidden="true">☰</span><span>ABRIR MENU</span>';
              button.addEventListener('click', function () {{ setOpen(true); }});
              doc.body.appendChild(button);
            }}
            return button;
          }}

          function ensureCloseControl() {{
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return null;
            const host = sidebar.firstElementChild || sidebar;
            let button = host.querySelector('#renova-fin-sidebar-close');
            if (!button) {{
              button = doc.createElement('button');
              button.id = 'renova-fin-sidebar-close';
              button.type = 'button';
              button.setAttribute('aria-label', 'Recolher menu RENOVA Finanças');
              button.textContent = '◀ RECOLHER MENU';
              button.addEventListener('click', function () {{ setOpen(false); }});
              host.insertBefore(button, host.firstChild);
            }}
            return button;
          }}

          function refreshControls() {{
            if (!desktop()) {{
              doc.body.classList.remove('renova-fin-sidebar-closed');
              const open = doc.getElementById('renova-fin-sidebar-open');
              if (open) open.style.display = 'none';
              const close = doc.getElementById('renova-fin-sidebar-close');
              if (close) close.style.display = 'none';
              return;
            }}
            const isOpen = !doc.body.classList.contains('renova-fin-sidebar-closed');
            const open = ensureOpenControl();
            const close = ensureCloseControl();
            if (open) open.style.display = isOpen ? 'none' : 'flex';
            if (close) close.style.display = isOpen ? 'block' : 'none';
          }}

          function radioItems() {{
            const radio = doc.querySelector('[data-testid="stSidebar"] [data-testid="stRadio"]');
            if (!radio) return {{ radio:null, items:[] }};
            const labels = Array.from(
              radio.querySelectorAll('label[data-baseweb="radio"]')
            );
            const items = labels.map(function (label) {{
              const p = label.querySelector('p');
              const input = label.querySelector('input');
              const text = (p ? p.textContent : label.textContent || '').trim();
              return {{ label, input, text }};
            }}).filter(function (item) {{ return item.text; }});
            return {{ radio, items }};
          }}

          function activePage(items) {{
            const active = items.find(function (item) {{
              return item.input && item.input.checked;
            }});
            return active ? active.text : '';
          }}

          function findItem(items, target) {{
            return items.find(function (item) {{ return item.text === target; }});
          }}

          function buildGroupedNavigation() {{
            if (!desktop()) return;

            const source = radioItems();
            if (!source.radio || !source.items.length) return;

            const available = source.items.map(function (item) {{ return item.text; }});
            const signature = available.join('|');
            let root = doc.getElementById('renova-fin-grouped-nav');

            if (!root) {{
              root = doc.createElement('nav');
              root.id = 'renova-fin-grouped-nav';
              root.setAttribute('aria-label', 'Navegação principal RENOVA Finanças');
              source.radio.parentNode.insertBefore(root, source.radio);
            }}

            if (root.dataset.signature !== signature) {{
              root.innerHTML = '';
              const title = doc.createElement('div');
              title.className = 'rv-nav-title';
              title.innerHTML = '<span>NAVEGAÇÃO</span><small>Áreas do sistema</small>';
              root.appendChild(title);

              const used = new Set();
              GROUPS.forEach(function (group) {{
                const titleText = group[0];
                const pages = group[1].filter(function (page) {{
                  return available.indexOf(page) >= 0;
                }});
                if (!pages.length) return;

                const details = doc.createElement('details');
                details.className = 'rv-nav-group';
                details.dataset.group = titleText;

                const summary = doc.createElement('summary');
                summary.textContent = titleText;
                details.appendChild(summary);

                const list = doc.createElement('div');
                list.className = 'rv-nav-items';

                pages.forEach(function (page) {{
                  used.add(page);
                  const button = doc.createElement('button');
                  button.type = 'button';
                  button.className = 'rv-nav-item';
                  button.dataset.target = page;
                  button.innerHTML =
                    '<span class="rv-nav-icon" aria-hidden="true">' +
                    (ICONS[page] || '•') +
                    '</span><span>' + page + '</span>';
                  button.addEventListener('click', function () {{
                    const latest = radioItems().items;
                    const targetItem = findItem(latest, page);
                    if (targetItem && targetItem.label) targetItem.label.click();
                  }});
                  list.appendChild(button);
                }});

                details.appendChild(list);
                root.appendChild(details);
              }});

              const extras = available.filter(function (page) {{ return !used.has(page); }});
              if (extras.length) {{
                const details = doc.createElement('details');
                details.className = 'rv-nav-group';
                const summary = doc.createElement('summary');
                summary.textContent = '⋯ OUTROS';
                details.appendChild(summary);
                const list = doc.createElement('div');
                list.className = 'rv-nav-items';
                extras.forEach(function (page) {{
                  const button = doc.createElement('button');
                  button.type = 'button';
                  button.className = 'rv-nav-item';
                  button.dataset.target = page;
                  button.innerHTML =
                    '<span class="rv-nav-icon" aria-hidden="true">•</span><span>' + page + '</span>';
                  button.addEventListener('click', function () {{
                    const latest = radioItems().items;
                    const targetItem = findItem(latest, page);
                    if (targetItem && targetItem.label) targetItem.label.click();
                  }});
                  list.appendChild(button);
                }});
                details.appendChild(list);
                root.appendChild(details);
              }}

              root.dataset.signature = signature;
            }}

            const current = activePage(source.items);
            root.querySelectorAll('.rv-nav-item').forEach(function (button) {{
              const isActive = button.dataset.target === current;
              button.classList.toggle('active', isActive);
              if (isActive) {{
                button.setAttribute('aria-current', 'page');
                const details = button.closest('details');
                if (details) details.open = true;
              }} else {{
                button.removeAttribute('aria-current');
              }}
            }});
          }}

          function refresh() {{
            if (!desktop()) {{
              refreshControls();
              return;
            }}
            if (!win.__renovaFinanceSidebarInitialized) {{
              doc.body.classList.toggle('renova-fin-sidebar-closed', !getOpenPreference());
              win.__renovaFinanceSidebarInitialized = true;
            }}
            refreshControls();
            buildGroupedNavigation();
          }}

          win.__renovaFinanceSidebarRefresh = refresh;

          if (!win.__renovaFinanceSidebarObserver) {{
            win.__renovaFinanceSidebarObserver = new MutationObserver(function () {{
              win.requestAnimationFrame(refresh);
            }});
            if (doc.body) {{
              win.__renovaFinanceSidebarObserver.observe(doc.body, {{
                childList:true,
                subtree:true
              }});
            }}
          }}

          if (!win.__renovaFinanceSidebarResizeHandler) {{
            win.__renovaFinanceSidebarResizeHandler = function () {{
              if (!desktop()) {{
                doc.body.classList.remove('renova-fin-sidebar-closed');
              }} else if (win.__renovaFinanceSidebarInitialized) {{
                doc.body.classList.toggle('renova-fin-sidebar-closed', !getOpenPreference());
              }}
              refresh();
            }};
            win.addEventListener('resize', win.__renovaFinanceSidebarResizeHandler);
          }}

          refresh();
          [120, 350, 800, 1600].forEach(function (delay) {{
            win.setTimeout(refresh, delay);
          }});
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def render_sidebar_collapse_control(st_ref=st) -> None:
    """Compatibilidade: o controle agora é inserido pelo runtime DOM.

    Mantemos a função porque src.__init__ e versões anteriores podem importá-la,
    mas não renderizamos um segundo botão Streamlit.
    """
    return None


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
    """Não recolhe automaticamente no desktop.

    O ERP RENOVA mantém o menu sob controle explícito do usuário. A função
    permanece como no-op para preservar a API que app.py já importa.
    """
    return None
