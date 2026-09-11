import streamlit as st

RENOVA_LOGO_URL = (
    "https://nnjvxomaermffqnmwtzr.supabase.co/storage/v1/object/public/"
    "branding-renova/LOGO%20OFICIAL%20RENOVA.png"
)

PALETTE = {
    "bg": "#02070C",
    "surface": "#07131D",
    "surface_2": "#04111C",
    "gold": "#FFD75A",
    "gold_dark": "#D9A520",
    "blue": "#0090F0",
    "blue_dark": "#05225A",
    "text": "#F7FAFC",
    "muted": "#B8C8D6",
    "success": "#35D07F",
    "danger": "#FF5E6C",
    "info": "#68D3FF",
}


def apply_renova_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
          --rv-bg:#02070C;
          --rv-surface:#07131D;
          --rv-surface-2:#04111C;
          --rv-blue:#0090F0;
          --rv-blue-soft:#68D3FF;
          --rv-blue-dark:#05225A;
          --rv-gold:#FFD75A;
          --rv-gold-2:#D9A520;
          --rv-text:#F7FAFC;
          --rv-muted:#B8C8D6;
          --rv-green:#35D07F;
          --rv-red:#FF5E6C;
        }

        html, body, .stApp {
          background: var(--rv-bg) !important;
          color: var(--rv-text) !important;
        }

        .stApp {
          background-image:
            linear-gradient(rgba(0,144,240,.035) 1px, transparent 1px),
            linear-gradient(90deg,rgba(0,144,240,.035) 1px,transparent 1px),
            radial-gradient(circle at 48% -10%,rgba(0,144,240,.18),transparent 36%),
            radial-gradient(circle at 82% 12%,rgba(255,215,90,.08),transparent 25%),
            radial-gradient(circle at 8% 88%,rgba(0,144,240,.06),transparent 27%),
            linear-gradient(135deg,#02070C 0%,#04121E 52%,#02080E 100%) !important;
          background-size:42px 42px,42px 42px,auto,auto,auto,auto !important;
          background-attachment:fixed !important;
        }

        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"] {
          background:transparent !important;
        }

        [data-testid="stMainBlockContainer"] {
          max-width:1500px !important;
          padding-top:2.1rem !important;
          padding-bottom:6rem !important;
          position:relative;
          z-index:1;
        }

        [data-testid="stHeader"] {
          background:rgba(2,7,12,.78) !important;
          backdrop-filter:blur(18px) saturate(130%) !important;
          border-bottom:1px solid rgba(0,144,240,.10) !important;
        }

        [data-testid="stSidebar"] {
          min-width:264px !important;
          width:264px !important;
          background:linear-gradient(180deg,rgba(2,8,14,.98),rgba(4,17,27,.98) 72%,rgba(7,19,29,.98)) !important;
          border-right:1px solid rgba(0,174,255,.18) !important;
          box-shadow:14px 0 40px rgba(0,0,0,.28) !important;
        }

        [data-testid="stSidebar"] > div:first-child {
          background:
            radial-gradient(circle at 50% 0%,rgba(0,144,240,.13),transparent 33%),
            linear-gradient(180deg,rgba(2,8,14,.97),rgba(4,17,27,.95)) !important;
          backdrop-filter:blur(18px) !important;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] > label { display:none !important; }
        [data-testid="stSidebar"] [role="radiogroup"] {
          gap:8px !important;
          padding:5px 5px 18px !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] {
          position:relative !important;
          overflow:hidden !important;
          min-height:49px !important;
          padding:10px 13px !important;
          border-radius:14px !important;
          border:1px solid rgba(0,174,255,.26) !important;
          background:linear-gradient(135deg,rgba(5,23,37,.92),rgba(3,11,19,.90)) !important;
          box-shadow:0 8px 22px rgba(0,0,0,.23),inset 0 1px rgba(255,255,255,.018) !important;
          transition:transform .2s ease,border-color .2s ease,box-shadow .2s ease,background .2s ease !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]::before {
          content:"";
          position:absolute;
          inset:-1px auto -1px -58%;
          width:42%;
          background:linear-gradient(100deg,transparent,rgba(104,211,255,.15),transparent);
          transform:skewX(-18deg);
          transition:left .48s ease;
          pointer-events:none;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover {
          transform:translateX(5px) !important;
          border-color:rgba(0,195,255,.72) !important;
          background:linear-gradient(135deg,rgba(5,40,64,.98),rgba(3,16,28,.96)) !important;
          box-shadow:0 10px 28px rgba(0,0,0,.32),0 0 20px rgba(0,174,255,.15) !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover::before { left:125%; }
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
          border-color:rgba(255,215,90,.82) !important;
          background:linear-gradient(120deg,rgba(38,31,7,.95),rgba(7,28,43,.96)) !important;
          box-shadow:0 10px 28px rgba(0,0,0,.34),0 0 22px rgba(255,215,90,.13),inset 0 0 18px rgba(255,215,90,.045) !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label p {
          color:#EAF7FF !important;
          font-size:.91rem !important;
          font-weight:760 !important;
          letter-spacing:.01em !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) p {
          color:#FFE477 !important;
          font-weight:900 !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
          width:10px !important;
          height:10px !important;
          min-width:10px !important;
          margin-right:9px !important;
          background:#061725 !important;
          border:1.5px solid #00B8FF !important;
          box-shadow:0 0 10px rgba(0,184,255,.48) !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) > div:first-child {
          background:#FFD75A !important;
          border-color:#FFF1A4 !important;
          box-shadow:0 0 14px rgba(255,215,90,.75) !important;
        }

        .renova-brand {
          position:relative;
          overflow:hidden;
          margin:4px 2px 16px;
          padding:17px 14px 15px;
          text-align:center;
          border:1px solid rgba(0,184,255,.24);
          border-radius:20px;
          background:
            radial-gradient(circle at 50% 0%,rgba(0,144,240,.18),transparent 46%),
            linear-gradient(145deg,rgba(4,22,35,.97),rgba(2,9,15,.99));
          box-shadow:0 16px 32px rgba(0,0,0,.31),inset 0 0 24px rgba(0,144,240,.035);
        }
        .renova-brand::after {
          content:"";
          position:absolute;
          left:-38%;
          bottom:0;
          width:38%;
          height:2px;
          background:linear-gradient(90deg,transparent,#0090F0,#FFD75A,transparent);
          box-shadow:0 0 14px rgba(0,144,240,.36);
          animation:rvBrandScan 5.4s ease-in-out infinite;
        }
        @keyframes rvBrandScan { 0%,18%{left:-38%} 75%,100%{left:110%} }
        @keyframes rvLogoFloat { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-4px)} }
        .renova-brand img {
          width:78px;
          max-width:78px;
          height:auto;
          margin:0 auto 8px;
          display:block;
          animation:rvLogoFloat 4.3s ease-in-out infinite;
          filter:drop-shadow(0 0 15px rgba(0,174,255,.26)) drop-shadow(0 0 8px rgba(255,215,90,.15));
        }
        .renova-brand .kicker {
          color:#77CFFF;
          font-size:.58rem;
          font-weight:900;
          letter-spacing:.17em;
        }
        .renova-brand h2 {
          margin:4px 0 0;
          color:#FFFFFF;
          font-size:1.18rem;
          font-weight:950;
          letter-spacing:.015em;
          text-shadow:0 0 15px rgba(0,144,240,.24);
        }
        .renova-brand p {
          margin:4px 0 0;
          color:#B8D8EA;
          font-size:.72rem;
          font-weight:700;
        }
        .renova-brand .brand-rule {
          height:1px;
          margin:12px 11px 9px;
          background:linear-gradient(90deg,transparent,rgba(255,215,90,.65),transparent);
        }
        .renova-brand .brand-system {
          color:#FFE477;
          font-size:.64rem;
          font-weight:900;
          letter-spacing:.12em;
        }

        .renova-hero {
          position:relative;
          overflow:hidden;
          border:1px solid rgba(255,215,90,.32);
          border-radius:22px;
          padding:3.35rem 1.55rem 1.35rem;
          margin-bottom:18px;
          background:
            linear-gradient(rgba(0,144,240,.05) 1px,transparent 1px),
            linear-gradient(90deg,rgba(0,144,240,.05) 1px,transparent 1px),
            radial-gradient(circle at 88% 14%,rgba(0,144,240,.23),transparent 30%),
            radial-gradient(circle at 8% 120%,rgba(255,215,90,.14),transparent 34%),
            linear-gradient(125deg,#04111C 0%,#061D31 46%,#02070C 100%);
          background-size:28px 28px,28px 28px,auto,auto,auto;
          box-shadow:0 22px 52px rgba(0,0,0,.40),0 0 34px rgba(0,144,240,.08),inset 0 1px rgba(255,255,255,.035);
        }
        .renova-hero::before {
          content:"RENOVA FINANÇAS • INTELIGÊNCIA FINANCEIRA";
          position:absolute;
          left:1.55rem;
          top:1.10rem;
          color:#F7D664;
          font-size:.62rem;
          line-height:1;
          font-weight:950;
          letter-spacing:.16em;
          text-shadow:0 0 16px rgba(247,214,100,.22);
        }
        .renova-hero::after {
          content:"";
          position:absolute;
          left:-35%;
          bottom:0;
          width:35%;
          height:2px;
          background:linear-gradient(90deg,transparent,#0090F0,#FFD75A,transparent);
          box-shadow:0 0 14px rgba(0,144,240,.35);
          animation:rvHeroScan 5.2s ease-in-out infinite;
        }
        @keyframes rvHeroScan { 0%,18%{left:-35%} 75%,100%{left:110%} }
        .renova-hero h1 {
          margin:0;
          color:#F7FAFC;
          font-size:clamp(1.8rem,4vw,2.75rem);
          font-weight:950;
          letter-spacing:-.045em;
        }
        .renova-hero strong {
          color:#FFD75A;
          text-shadow:0 0 18px rgba(255,215,90,.16);
        }
        .renova-hero p {
          color:#C5D5E0;
          margin:8px 0 0;
          max-width:920px;
          font-size:.95rem;
        }

        .metric-card {
          position:relative;
          overflow:hidden;
          min-height:126px;
          padding:18px 18px;
          border:1px solid rgba(0,144,240,.25);
          border-radius:18px;
          background:
            radial-gradient(circle at 90% 10%,rgba(0,144,240,.14),transparent 27%),
            linear-gradient(145deg,rgba(7,24,38,.98),rgba(3,10,16,.99));
          box-shadow:0 14px 34px rgba(0,0,0,.31),inset 0 1px rgba(255,255,255,.025);
          transition:transform .2s ease,border-color .2s ease,box-shadow .2s ease;
        }
        .metric-card::before {
          content:"";
          position:absolute;
          left:0;right:0;top:0;height:2px;
          background:linear-gradient(90deg,transparent,#0090F0,#FFD75A,transparent);
          opacity:.88;
        }
        .metric-card::after {
          content:"◆";
          position:absolute;
          right:15px;top:14px;
          width:32px;height:32px;
          display:grid;place-items:center;
          border-radius:10px;
          color:#F7D664;
          background:linear-gradient(145deg,rgba(4,45,82,.75),rgba(5,16,25,.94));
          border:1px solid rgba(247,214,100,.25);
          box-shadow:0 0 20px rgba(0,144,240,.10);
          font-size:.82rem;
        }
        .metric-card:hover {
          transform:translateY(-4px);
          border-color:rgba(255,215,90,.54);
          box-shadow:0 18px 42px rgba(0,0,0,.37),0 0 25px rgba(0,144,240,.10);
        }
        .metric-card .label {
          color:#9FB7C8;
          font-size:.76rem;
          font-weight:850;
          letter-spacing:.015em;
        }
        .metric-card .value {
          color:#FFFFFF;
          font-size:clamp(1.25rem,2.25vw,1.75rem);
          font-weight:950;
          margin-top:10px;
          letter-spacing:-.035em;
        }
        .metric-card .hint {
          color:#FFD75A;
          font-size:.76rem;
          font-weight:760;
          margin-top:7px;
        }

        div[data-testid="stMetric"], [data-testid="stExpander"] {
          background:linear-gradient(145deg,rgba(7,20,31,.97),rgba(3,10,17,.99)) !important;
          border:1px solid rgba(247,214,100,.24) !important;
          border-radius:17px !important;
          box-shadow:0 12px 31px rgba(0,0,0,.27) !important;
          transition:.18s ease !important;
        }
        div[data-testid="stMetric"]:hover, [data-testid="stExpander"]:hover {
          transform:translateY(-2px) !important;
          border-color:rgba(0,144,240,.50) !important;
          box-shadow:0 16px 38px rgba(0,0,0,.35),0 0 20px rgba(0,144,240,.07) !important;
        }
        div[data-testid="stMetric"] label { color:#AFC3D2 !important; }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] { color:#F7FAFC !important;font-weight:900 !important; }

        h1,h2,h3 { color:#F7FAFC !important;letter-spacing:-.025em !important; }
        p,label { color:#D4E0E8; }
        hr { border-color:rgba(0,144,240,.15) !important; }

        .stButton > button,
        .stDownloadButton > button,
        [data-testid="stFormSubmitButton"] button {
          min-height:43px !important;
          border-radius:11px !important;
          border:1px solid #FFE57B !important;
          background:linear-gradient(110deg,#C99308,#FFCA2C 30%,#FFF0A3 49%,#FFD75A 63%,#D8A716) !important;
          color:#06111B !important;
          -webkit-text-fill-color:#06111B !important;
          font-weight:900 !important;
          box-shadow:0 6px 18px rgba(0,0,0,.25),0 0 11px rgba(255,202,44,.11) !important;
          transition:.18s ease !important;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        [data-testid="stFormSubmitButton"] button:hover {
          background:linear-gradient(135deg,#03101B,#07305B 60%,#02070C) !important;
          color:#FFD75A !important;
          -webkit-text-fill-color:#FFD75A !important;
          border-color:#FFD75A !important;
          box-shadow:0 0 19px rgba(0,144,240,.23),0 0 15px rgba(255,215,90,.18) !important;
          transform:translateY(-1px) !important;
        }
        .stButton > button:hover *,
        .stDownloadButton > button:hover *,
        [data-testid="stFormSubmitButton"] button:hover * {
          color:#FFD75A !important;
          -webkit-text-fill-color:#FFD75A !important;
        }

        [data-testid="stDataFrame"] {
          border:1px solid rgba(0,144,240,.20);
          border-radius:17px;
          overflow:hidden;
          box-shadow:0 12px 30px rgba(0,0,0,.22);
        }

        [data-baseweb="input"] > div,
        [data-baseweb="textarea"] > div,
        [data-baseweb="select"] > div,
        div[data-testid="stNumberInput"] input {
          background:#06131E !important;
          color:#FFFFFF !important;
          border:1px solid rgba(247,214,100,.42) !important;
          border-radius:11px !important;
        }
        [data-baseweb="input"]:focus-within,
        [data-baseweb="textarea"]:focus-within,
        [data-baseweb="select"] > div:focus-within {
          border-color:#0090F0 !important;
          box-shadow:0 0 0 2px rgba(0,144,240,.10),0 0 17px rgba(0,144,240,.08) !important;
        }

        [data-testid="stTabs"] [data-baseweb="tab-list"] {
          gap:7px !important;
          padding:6px !important;
          border:1px solid rgba(0,144,240,.20) !important;
          border-radius:14px !important;
          background:linear-gradient(145deg,rgba(4,17,28,.92),rgba(2,8,14,.96)) !important;
        }
        [data-testid="stTabs"] [data-baseweb="tab"] {
          border-radius:10px !important;
          min-height:42px !important;
          color:#AFC3D2 !important;
        }
        [data-testid="stTabs"] [aria-selected="true"] {
          color:#FFE477 !important;
          background:linear-gradient(120deg,rgba(38,31,7,.9),rgba(7,28,43,.93)) !important;
        }

        [data-testid="stAlert"] {
          border-radius:15px !important;
          border:1px solid rgba(0,144,240,.24) !important;
          background:linear-gradient(145deg,rgba(5,22,35,.95),rgba(3,11,18,.98)) !important;
        }

        [data-testid="stAppViewContainer"]::after {
          content:"";
          position:fixed;
          left:0;right:0;bottom:-7vh;
          height:22vh;
          pointer-events:none;
          background:
            linear-gradient(rgba(0,144,240,.06) 1px,transparent 1px),
            linear-gradient(90deg,rgba(0,144,240,.06) 1px,transparent 1px);
          background-size:52px 28px;
          transform:perspective(380px) rotateX(62deg);
          transform-origin:bottom;
          opacity:.40;
          z-index:0;
        }

        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="collapsedControl"] button {
          width:42px !important;
          height:42px !important;
          min-width:42px !important;
          min-height:42px !important;
          border-radius:12px !important;
          border:1px solid rgba(255,215,90,.66) !important;
          background:linear-gradient(145deg,#071C2D,#03101A) !important;
          color:#FFD75A !important;
          box-shadow:0 8px 22px rgba(0,0,0,.36),0 0 18px rgba(0,144,240,.18) !important;
        }
        [data-testid="stSidebarCollapseButton"] svg,
        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="collapsedControl"] svg {
          color:#FFD75A !important;
          fill:#FFD75A !important;
          stroke:#FFD75A !important;
        }

        @media (max-width:768px) {
          .stApp { background-size:32px 32px,32px 32px,auto,auto,auto,auto !important; }
          [data-testid="stMainBlockContainer"] { padding:1.05rem .9rem 5.5rem !important; }
          .renova-hero { padding:3rem 1.05rem 1.05rem;border-radius:17px; }
          .renova-hero::before { left:1.05rem;top:1rem;font-size:.52rem;letter-spacing:.12em; }
          .renova-hero h1 { font-size:1.72rem; }
          .renova-hero p { font-size:.88rem; }
          .metric-card { min-height:112px;border-radius:15px; }
          .metric-card .value { font-size:1.34rem; }
          [data-testid="stAppViewContainer"]::after { opacity:.16;height:13vh; }
          [data-testid="stSidebar"] { min-width:88vw !important;width:88vw !important; }
        }

        @media (prefers-reduced-motion:reduce) {
          * { animation:none !important;scroll-behavior:auto !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def brand_block() -> None:
    st.markdown(
        f"""
        <div class="renova-brand">
          <img src="{RENOVA_LOGO_URL}" alt="Logo RENOVA">
          <div class="kicker">ECOSSISTEMA RENOVA</div>
          <h2>RENOVA Finanças</h2>
          <p>Controle • Clareza • Decisão</p>
          <div class="brand-rule"></div>
          <div class="brand-system">GESTÃO FINANCEIRA INTELIGENTE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
