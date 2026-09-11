import streamlit as st

PALETTE = {
    "bg": "#0B0B0C",
    "surface": "#111111",
    "surface_2": "#141414",
    "gold": "#FFD75A",
    "gold_dark": "#D9A520",
    "text": "#F5F5F5",
    "muted": "#CFCFCF",
    "success": "#35D07F",
    "danger": "#FF5E6C",
    "info": "#6CB6FF",
}


def apply_renova_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
          --renova-bg: #0B0B0C;
          --renova-surface: #111111;
          --renova-surface-2: #141414;
          --renova-gold: #FFD75A;
          --renova-gold-dark: #D9A520;
          --renova-text: #F5F5F5;
          --renova-muted: #CFCFCF;
        }

        .stApp {
          background:
            radial-gradient(circle at 10% 0%, rgba(255,215,90,.10), transparent 28%),
            radial-gradient(circle at 100% 15%, rgba(217,165,32,.06), transparent 24%),
            #0B0B0C;
          color: var(--renova-text);
        }

        [data-testid="stSidebar"] {
          background: linear-gradient(180deg, #0D0D0F 0%, #090909 100%);
          border-right: 1px solid rgba(255,215,90,.13);
        }

        .renova-brand {
          padding: 12px 14px;
          border: 1px solid rgba(255,215,90,.22);
          border-radius: 18px;
          background: linear-gradient(135deg, rgba(255,215,90,.08), rgba(255,255,255,.02));
          margin-bottom: 14px;
        }

        .renova-brand h2 { margin: 0; color: #FFD75A; font-size: 1.32rem; }
        .renova-brand p { margin: 4px 0 0; color: #CFCFCF; font-size: .84rem; }

        .renova-hero {
          border: 1px solid rgba(255,215,90,.20);
          border-radius: 24px;
          padding: 22px 24px;
          margin-bottom: 18px;
          background:
            linear-gradient(120deg, rgba(255,215,90,.09), rgba(255,255,255,.02)),
            #101011;
          box-shadow: 0 16px 45px rgba(0,0,0,.28);
        }
        .renova-hero h1 { margin: 0; color: #F5F5F5; font-size: clamp(1.7rem, 4vw, 2.55rem); }
        .renova-hero strong { color: #FFD75A; }
        .renova-hero p { color: #CFCFCF; margin: 8px 0 0; }

        .metric-card {
          border: 1px solid rgba(255,215,90,.14);
          background: linear-gradient(180deg, rgba(255,255,255,.025), rgba(255,255,255,.01));
          border-radius: 20px;
          padding: 16px 18px;
          min-height: 118px;
        }
        .metric-card .label { color: #CFCFCF; font-size: .82rem; }
        .metric-card .value { color: #F5F5F5; font-size: 1.55rem; font-weight: 750; margin-top: 9px; }
        .metric-card .hint { color: #FFD75A; font-size: .76rem; margin-top: 6px; }

        div[data-testid="stMetric"] {
          background: #111111;
          border: 1px solid rgba(255,215,90,.12);
          border-radius: 18px;
          padding: 14px;
        }

        .stButton > button, .stDownloadButton > button {
          border-radius: 12px;
          border: 1px solid rgba(255,215,90,.40);
          background: #0D0D0F;
          color: #FFD75A;
          font-weight: 700;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
          border-color: #FFD75A;
          color: #0B0B0C;
          background: #FFD75A;
        }

        [data-testid="stDataFrame"] {
          border: 1px solid rgba(255,215,90,.12);
          border-radius: 16px;
          overflow: hidden;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        div[data-testid="stNumberInput"] input {
          background: #141414 !important;
          color: #F5F5F5 !important;
          border-color: rgba(255,215,90,.14) !important;
        }

        @media (max-width: 768px) {
          .renova-hero { padding: 18px; border-radius: 18px; }
          .renova-hero h1 { font-size: 1.75rem; }
          .metric-card { min-height: 104px; }
          .metric-card .value { font-size: 1.35rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def brand_block() -> None:
    st.markdown(
        """
        <div class="renova-brand">
          <h2>RENOVA Finanças</h2>
          <p>Controle • Clareza • Decisão</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
