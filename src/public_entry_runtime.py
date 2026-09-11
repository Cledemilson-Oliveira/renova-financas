from __future__ import annotations

import streamlit as st


_FREE_CTA_TARGET = "/Criar_Conta"
_PREMIUM_CTA_TARGET = "/Criar_Conta?plan=premium"


def install_public_entry_runtime() -> None:
    """Corrige CTAs públicos sem acoplar a landing ao fluxo interno do app.

    A landing original usava âncoras HTML dentro de uma aba Streamlit. O navegador
    conseguia navegar até a âncora, mas não conseguia ativar a aba de cadastro, o
    que fazia o CTA parecer inoperante. Esta camada converte os CTAs conhecidos em
    rotas reais do aplicativo.
    """
    if getattr(st, "_renova_public_entry_runtime_installed", False):
        return

    original_markdown = st.markdown

    def markdown_with_public_routes(body, *args, **kwargs):
        if isinstance(body, str):
            body = body.replace('href="#criar-conta"', f'href="{_FREE_CTA_TARGET}"')
            body = body.replace(
                '<div class="sales-cta primary full static">Personalize sua IA por R$ 9,90/mês</div>',
                f'<a href="{_PREMIUM_CTA_TARGET}" class="sales-cta primary full">Personalize sua IA por R$ 9,90/mês</a>',
            )
        return original_markdown(body, *args, **kwargs)

    st.markdown = markdown_with_public_routes
    st._renova_public_entry_runtime_installed = True
