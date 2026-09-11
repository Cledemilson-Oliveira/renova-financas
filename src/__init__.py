"""RENOVA Finanças application package."""


def _install_public_entry_runtime() -> None:
    """Conecta os CTAs públicos às rotas reais de cadastro."""
    from .public_entry_runtime import install_public_entry_runtime

    install_public_entry_runtime()


def _install_ai_training_runtime() -> None:
    """Ativa a camada de memória personalizada da RENOVA IA ao carregar o pacote."""
    from . import ai_finance as _ai_finance
    from . import ai_training as _ai_training
    from .ai_training_runtime import install_training_runtime

    install_training_runtime(_ai_finance, _ai_training)


def _install_recurring_finance_runtime() -> None:
    """Gera automaticamente contas/receitas recorrentes antes das leituras financeiras."""
    from . import repository as _repository
    from .recurring_runtime import install_recurring_runtime

    install_recurring_runtime(_repository)


def _install_theme_mode_runtime() -> None:
    """Acopla tema, layout responsivo e atalhos globais da identidade RENOVA."""
    import streamlit as st

    from . import theme as _theme
    from .sidebar_runtime import (
        auto_collapse_sidebar_robust,
        inject_sidebar_runtime_css,
        render_ecosystem_product_card,
        render_sidebar_collapse_control,
    )
    from .theme_accessibility import inject_accessibility_css
    from .theme_modes import apply_display_mode, render_appearance_selector
    from .ui import apply_device_ui, install_device_runtime

    if getattr(_theme, "_renova_theme_modes_installed", False):
        return

    install_device_runtime()

    original_apply_theme = _theme.apply_renova_theme
    original_brand_block = _theme.brand_block

    def apply_theme_with_mode() -> None:
        original_apply_theme()
        apply_display_mode()
        inject_accessibility_css()
        apply_device_ui()
        inject_sidebar_runtime_css()

    def brand_block_with_appearance() -> None:
        # Controle explícito: não depende da posição do botão nativo do Streamlit.
        render_sidebar_collapse_control(st)
        original_brand_block()
        render_ecosystem_product_card(st)
        render_appearance_selector()

        # Planejamento recorrente fica disponível para todo usuário autenticado.
        try:
            from .supabase_client import current_user

            user = current_user()
            uid = str(user.id) if user and getattr(user, "id", None) else ""
            if uid:
                st.page_link(
                    "pages/Planejamento_Caixa.py",
                    label="📈 Planejamento de Caixa",
                    use_container_width=True,
                )
        except Exception:
            pass

        # A gestão de usuários só é exposta visualmente para a conta dono.
        try:
            from .access import is_owner
            from .supabase_client import current_user

            user = current_user()
            uid = str(user.id) if user and getattr(user, "id", None) else ""
            if uid and is_owner(uid):
                st.page_link(
                    "pages/Administracao.py",
                    label="🛡️ Gestão de Usuários",
                    use_container_width=True,
                )
        except Exception:
            pass

    _theme.apply_renova_theme = apply_theme_with_mode
    _theme.brand_block = brand_block_with_appearance
    # O app importa esta função depois que o pacote src já foi inicializado.
    # Assim, toda troca de página usa o recolhimento resiliente automaticamente.
    _theme.auto_collapse_sidebar = auto_collapse_sidebar_robust
    _theme._renova_theme_modes_installed = True


_install_public_entry_runtime()
_install_ai_training_runtime()
_install_recurring_finance_runtime()
_install_theme_mode_runtime()
