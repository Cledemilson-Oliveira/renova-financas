from __future__ import annotations

import streamlit as st


_FREE_CTA_TARGET = "/Criar_Conta"
_PREMIUM_CTA_TARGET = "/Criar_Conta?plan=premium"


def _upgrade_sales_copy(body: str) -> str:
    body = body.replace('<div class="plan">RENOVA IA</div>', '<div class="plan">RENOVA IA Personal</div>')
    body = body.replace(
        '<div class="price">R$ 9,90 <small>/mês</small></div>',
        '<div style="opacity:.62;text-decoration:line-through;font-size:.78rem;margin-bottom:.25rem">Valor de referência: R$ 29,90/mês</div>'
        '<div class="price">R$ 9,90 <small>/mês</small></div>'
        '<div style="color:#BDEBFF;font-size:.72rem;margin:.45rem 0 1rem">Preço de lançamento. Mantido enquanto a assinatura permanecer ativa.</div>',
    )
    body = body.replace(
        'Para transformar a IA padrão em um assistente treinado para o seu jeito de trabalhar.',
        'Sua IA financeira que aprende seu jeito de cuidar do dinheiro.',
    )
    body = body.replace('RENOVA IA PERSONALIZADA', 'RENOVA IA PERSONAL')
    body = body.replace('Personalize sua <strong>RENOVA IA</strong>', 'Conheça o <strong>RENOVA IA Personal</strong>')
    body = body.replace(
        'A IA Padrão já é gratuita. A assinatura libera memória, regras e treinamento exclusivos para sua conta.',
        'Sua IA financeira que aprende seu jeito de cuidar do dinheiro. A IA Padrão continua gratuita; o Personal adiciona memória, regras e treinamento exclusivos.',
    )
    body = body.replace(
        'A assinatura é opcional e libera treinamento e memória personalizados.',
        'A assinatura é opcional. Preço de lançamento: R$ 9,90/mês; quem entra nessa condição mantém esse valor enquanto a assinatura permanecer ativa.',
    )
    return body


def install_public_entry_runtime() -> None:
    """Conecta CTAs públicos a rotas reais e mantém a oferta comercial consistente."""
    if getattr(st, "_renova_public_entry_runtime_installed", False):
        return

    original_markdown = st.markdown

    def markdown_with_public_routes(body, *args, **kwargs):
        if isinstance(body, str):
            body = body.replace('href="#criar-conta"', f'href="{_FREE_CTA_TARGET}"')
            body = body.replace(
                '<div class="sales-cta primary full static">Personalize sua IA por R$ 9,90/mês</div>',
                f'<a href="{_PREMIUM_CTA_TARGET}" class="sales-cta primary full">Quero RENOVA IA Personal por R$ 9,90/mês</a>',
            )
            body = _upgrade_sales_copy(body)
        return original_markdown(body, *args, **kwargs)

    st.markdown = markdown_with_public_routes
    st._renova_public_entry_runtime_installed = True
