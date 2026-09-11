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


def _install_theme_mode_runtime() -> None:
    """Acopla tema, layout responsivo e atalhos globais da identidade RENOVA."""
    import streamlit as st

    from . import theme as _theme
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

    def brand_block_with_appearance() -> None:
        original_brand_block()
        render_appearance_selector()

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
    _theme._renova_theme_modes_installed = True


_install_public_entry_runtime()
_install_ai_training_runtime()
_install_theme_mode_runtime()
