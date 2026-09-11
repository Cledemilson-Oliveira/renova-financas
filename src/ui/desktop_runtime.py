from __future__ import annotations

from typing import Any, Callable

from src.sidebar_runtime import inject_sidebar_runtime_css

from .desktop import apply_desktop_styles, tune_plotly_desktop


def apply_desktop_runtime() -> None:
    """Ativa exclusivamente a camada visual e a navegação do desktop."""
    apply_desktop_styles()
    inject_sidebar_runtime_css()


def render_dataframe_desktop(
    original: Callable[..., Any],
    data: Any,
    *args: Any,
    **kwargs: Any,
) -> Any:
    return original(data, *args, **kwargs)


def prepare_plotly_desktop(
    figure_or_data: Any,
    config: dict[str, Any] | None = None,
) -> tuple[Any, dict[str, Any] | None]:
    return tune_plotly_desktop(figure_or_data), config
