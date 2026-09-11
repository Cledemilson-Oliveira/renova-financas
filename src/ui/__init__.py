"""Camada de interface responsiva do RENOVA Finanças.

A lógica financeira continua compartilhada. Tudo que é específico de tela fica
separado em ``mobile`` e ``desktop`` para evitar retrabalho entre plataformas.
"""

from .device import current_device, is_mobile
from .runtime import apply_device_ui, install_device_runtime

__all__ = ["apply_device_ui", "current_device", "install_device_runtime", "is_mobile"]
