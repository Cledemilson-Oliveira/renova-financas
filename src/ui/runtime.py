from __future__ import annotations

from functools import wraps
from typing import Any

import streamlit as st

from .desktop import apply_desktop_styles, tune_plotly_desktop
from .device import is_mobile
from .mobile import apply_mobile_styles, mobile_plotly_config, render_dataframe_mobile, tune_plotly_mobile


_INSTALLED = False
_ORIGINAL_DATAFRAME = None
_ORIGINAL_PLOTLY_CHART = None


def apply_device_ui() -> None:
    if is_mobile():
        apply_mobile_styles()
    else:
        apply_desktop_styles()


def install_device_runtime() -> None:
    """Instala uma camada de apresentação sem tocar na lógica financeira.

    O app continua chamando ``st.dataframe`` e ``st.plotly_chart`` normalmente.
    No celular, a camada mobile converte somente tabelas financeiras largas em
    cards e ajusta gráficos. No desktop, mantém a experiência de tabela ampla.
    """
    global _INSTALLED, _ORIGINAL_DATAFRAME, _ORIGINAL_PLOTLY_CHART
    if _INSTALLED:
        return

    _ORIGINAL_DATAFRAME = st.dataframe
    _ORIGINAL_PLOTLY_CHART = st.plotly_chart

    @wraps(_ORIGINAL_DATAFRAME)
    def responsive_dataframe(data: Any = None, *args: Any, **kwargs: Any) -> Any:
        if is_mobile():
            return render_dataframe_mobile(_ORIGINAL_DATAFRAME, data, *args, **kwargs)
        return _ORIGINAL_DATAFRAME(data, *args, **kwargs)

    @wraps(_ORIGINAL_PLOTLY_CHART)
    def responsive_plotly_chart(figure_or_data: Any, *args: Any, **kwargs: Any) -> Any:
        if is_mobile():
            figure_or_data = tune_plotly_mobile(figure_or_data)
            kwargs["config"] = mobile_plotly_config(kwargs.get("config"))
        else:
            figure_or_data = tune_plotly_desktop(figure_or_data)
        return _ORIGINAL_PLOTLY_CHART(figure_or_data, *args, **kwargs)

    st.dataframe = responsive_dataframe
    st.plotly_chart = responsive_plotly_chart
    _INSTALLED = True
