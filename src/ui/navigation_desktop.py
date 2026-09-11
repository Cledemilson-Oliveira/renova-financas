from __future__ import annotations

from collections.abc import Sequence

import streamlit as st


NAV_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("🏠 INÍCIO", ("Dashboard",)),
    ("💸 MOVIMENTAÇÕES", ("Lançamentos", "Categorias")),
    ("🏦 CONTAS E CRÉDITO", ("Contas", "Cartões")),
    ("📊 PLANEJAMENTO", ("Orçamentos", "Análises", "Relatórios")),
    ("🤖 RENOVA IA", ("RENOVA IA", "Treinamento IA", "Assinar RENOVA IA")),
)

NAV_LABELS = {
    "Dashboard": "Painel",
    "Lançamentos": "Lançamentos",
    "Categorias": "Categorias",
    "Contas": "Contas",
    "Cartões": "Cartões",
    "Orçamentos": "Orçamentos",
    "Análises": "Análises",
    "Relatórios": "Relatórios",
    "RENOVA IA": "RENOVA IA",
    "Treinamento IA": "Treinamento IA",
    "Assinar RENOVA IA": "Assinar RENOVA IA",
}

NAV_ICONS = {
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


def _go_to(target: str) -> None:
    """Troca de módulo sem usar ``nav_page`` como chave de widget.

    Isso evita o ``StreamlitAPIException`` que ocorria quando um botão do painel
    tentava alterar ``st.session_state.nav_page`` depois que o antigo ``st.radio``
    já havia sido criado com a mesma chave.
    """
    st.session_state["nav_page"] = target
    st.session_state["_last_nav_page"] = target


def _button_label(page: str) -> str:
    return f"{NAV_ICONS.get(page, '•')}  {NAV_LABELS.get(page, page)}"


def render_desktop_navigation(options: Sequence[str], current: str) -> str:
    """Menu desktop nativo, agrupado no padrão do ERP RENOVA."""
    available = list(options)
    if not available:
        return current

    if current not in available:
        current = available[0]
        _go_to(current)

    st.markdown(
        '<div class="renova-nav-heading"><span>NAVEGAÇÃO</span><small>Áreas do sistema</small></div>',
        unsafe_allow_html=True,
    )

    used: set[str] = set()
    for group_title, group_pages in NAV_GROUPS:
        pages = [page for page in group_pages if page in available]
        if not pages:
            continue
        used.update(pages)
        with st.expander(group_title, expanded=current in pages):
            for page in pages:
                active = page == current
                if st.button(
                    _button_label(page),
                    key=f"renova_desktop_nav::{page}",
                    use_container_width=True,
                    type="primary" if active else "secondary",
                ):
                    _go_to(page)
                    st.rerun()

    extras = [page for page in available if page not in used]
    if extras:
        with st.expander("⋯ OUTROS", expanded=current in extras):
            for page in extras:
                active = page == current
                if st.button(
                    _button_label(page),
                    key=f"renova_desktop_nav::{page}",
                    use_container_width=True,
                    type="primary" if active else "secondary",
                ):
                    _go_to(page)
                    st.rerun()

    return str(st.session_state.get("nav_page") or current)
