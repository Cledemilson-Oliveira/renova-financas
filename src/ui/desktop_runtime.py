from __future__ import annotations

from typing import Any, Callable

from .desktop import apply_desktop_styles, tune_plotly_desktop
from .desktop_shell import inject_desktop_shell


def apply_desktop_runtime() -> None:
    """Ativa somente a camada visual e o shell do desktop."""
    apply_desktop_styles()
    inject_desktop_shell()


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
