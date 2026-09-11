from __future__ import annotations

from functools import wraps
from typing import Any

import streamlit as st

from .device import current_device


_INSTALLED = False
_ORIGINAL_DATAFRAME = None
_ORIGINAL_PLOTLY_CHART = None


def _device_runtime():
    """Carrega somente o runtime da plataforma ativa.

    Desktop e mobile não são mais importados juntos. Isso reduz efeitos
    colaterais de CSS/JavaScript entre os dois layouts e mantém cada plataforma
    com uma única camada responsável pela apresentação.
    """
    if current_device() == "mobile":
        from . import mobile_runtime

        return mobile_runtime

    from . import desktop_runtime

    return desktop_runtime


def apply_device_ui() -> None:
    runtime = _device_runtime()
    if current_device() == "mobile":
        runtime.apply_mobile_runtime()
    else:
        runtime.apply_desktop_runtime()


def install_device_runtime() -> None:
    """Instala adaptadores de tabela e gráfico com despacho por dispositivo.

    A lógica financeira continua compartilhada. A renderização específica é
    escolhida apenas no momento de desenhar cada componente, sem carregar o
    módulo visual da outra plataforma.
    """
    global _INSTALLED, _ORIGINAL_DATAFRAME, _ORIGINAL_PLOTLY_CHART
    if _INSTALLED:
        return

    _ORIGINAL_DATAFRAME = st.dataframe
    _ORIGINAL_PLOTLY_CHART = st.plotly_chart

    @wraps(_ORIGINAL_DATAFRAME)
    def responsive_dataframe(data: Any = None, *args: Any, **kwargs: Any) -> Any:
        runtime = _device_runtime()
        if current_device() == "mobile":
            return runtime.render_dataframe_mobile_runtime(
                _ORIGINAL_DATAFRAME,
                data,
                *args,
                **kwargs,
            )
        return runtime.render_dataframe_desktop(
            _ORIGINAL_DATAFRAME,
            data,
            *args,
            **kwargs,
        )

    @wraps(_ORIGINAL_PLOTLY_CHART)
    def responsive_plotly_chart(figure_or_data: Any, *args: Any, **kwargs: Any) -> Any:
        runtime = _device_runtime()
        config = kwargs.get("config")

        if current_device() == "mobile":
            figure_or_data, config = runtime.prepare_plotly_mobile(figure_or_data, config)
        else:
            figure_or_data, config = runtime.prepare_plotly_desktop(figure_or_data, config)

        if config is not None:
            kwargs["config"] = config
        return _ORIGINAL_PLOTLY_CHART(figure_or_data, *args, **kwargs)

    st.dataframe = responsive_dataframe
    st.plotly_chart = responsive_plotly_chart
    _INSTALLED = True
