from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

RENOVA_LOGO_URL = (
    "https://nnjvxomaermffqnmwtzr.supabase.co/storage/v1/object/public/"
    "branding-renova/LOGO%20OFICIAL%20RENOVA.png"
)

COLORS = {
    "bg": "#02070D",
    "panel": "#06131F",
    "panel_2": "#081C2B",
    "blue": "#00AEEF",
    "blue_2": "#0077FF",
    "gold": "#FFD75A",
    "gold_2": "#D9A520",
    "green": "#35D07F",
    "red": "#FF5E6C",
    "white": "#F7FBFF",
    "muted": "#AFC3D2",
}


def configure_plotly() -> None:
    template = go.layout.Template(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": COLORS["white"], "family": "Inter, Arial, sans-serif"},
            colorway=[
                COLORS["blue"],
                COLORS["gold"],
                COLORS["green"],
                COLORS["red"],
                "#7B8CFF",
                "#19D3F3",
                "#FF9F40",
            ],
            xaxis={
                "gridcolor": "rgba(0,174,239,.10)",
                "linecolor": "rgba(255,215,90,.18)",
                "zerolinecolor": "rgba(255,255,255,.08)",
                "tickfont": {"color": COLORS["muted"]},
                "title": {"font": {"color": COLORS["muted"]}},
            },
            yaxis={
                "gridcolor": "rgba(0,174,239,.10)",
                "linecolor": "rgba(255,215,90,.18)",
                "zerolinecolor": "rgba(255,255,255,.08)",
                "tickfont": {"color": COLORS["muted"]},
                "title": {"font": {"color": COLORS["muted"]}},
            },
            legend={
                "font": {"color": COLORS["muted"]},
                "bgcolor": "rgba(2,7,13,.35)",
            },
            hoverlabel={
                "bgcolor": "#07131D",
                "bordercolor": COLORS["gold"],
                "font": {"color": COLORS["white"]},
            },
        )
    )
    pio.templates["renova_financas"] = template
    pio.templates.default = "renova_financas"
