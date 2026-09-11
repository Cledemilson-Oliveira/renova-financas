"""RENOVA Finanças application package."""


def _install_ai_training_runtime() -> None:
    """Ativa a camada de memória personalizada da RENOVA IA ao carregar o pacote."""
    from . import ai_finance as _ai_finance
    from . import ai_training as _ai_training
    from .ai_training_runtime import install_training_runtime

    install_training_runtime(_ai_finance, _ai_training)


_install_ai_training_runtime()
