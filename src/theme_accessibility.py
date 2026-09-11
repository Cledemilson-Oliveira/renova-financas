from __future__ import annotations

import streamlit as st

from src.theme_modes import current_theme_mode


_DARK_CONTRAST_CSS = r"""
/* RENOVA Finanças — camada final de contraste e acessibilidade */

/* Campos reais: evita texto escuro sobre fundo escuro no desktop/mobile. */
.stApp input:not([type="checkbox"]):not([type="radio"]):not([type="file"]),
.stApp textarea,
.stApp [data-baseweb="select"] [role="combobox"]{
  background:#071A2B!important;
  color:#F7FBFF!important;
  -webkit-text-fill-color:#F7FBFF!important;
  caret-color:#FFD75A!important;
}
.stApp input:not([type="checkbox"]):not([type="radio"]):not([type="file"])::placeholder,
.stApp textarea::placeholder{
  color:#AFC3D2!important;
  -webkit-text-fill-color:#AFC3D2!important;
  opacity:1!important;
}
.stApp [data-baseweb="input"]>div,
.stApp [data-baseweb="textarea"]>div,
.stApp [data-baseweb="select"]>div,
.stApp [data-testid="stTextInput"]>div,
.stApp [data-testid="stTextArea"]>div,
.stApp [data-testid="stDateInput"]>div,
.stApp [data-testid="stNumberInput"]>div{
  background:#071A2B!important;
  border-color:rgba(0,174,239,.34)!important;
}
.stApp [data-baseweb="select"] span,
.stApp [data-baseweb="select"] div,
.stApp [role="option"]{
  color:#F7FBFF!important;
  -webkit-text-fill-color:#F7FBFF!important;
}
.stApp [data-testid="stTextInput"] button,
.stApp [data-testid="stTextInput"] button svg,
.stApp button[aria-label*="password" i],
.stApp button[aria-label*="senha" i],
.stApp button[aria-label*="password" i] svg,
.stApp button[aria-label*="senha" i] svg{
  color:#F7FBFF!important;
  fill:#F7FBFF!important;
  stroke:#F7FBFF!important;
}
.stApp input:-webkit-autofill,
.stApp input:-webkit-autofill:hover,
.stApp input:-webkit-autofill:focus{
  -webkit-text-fill-color:#F7FBFF!important;
  caret-color:#F7FBFF!important;
  -webkit-box-shadow:0 0 0 1000px #071A2B inset!important;
  box-shadow:0 0 0 1000px #071A2B inset!important;
  transition:background-color 99999s ease-out 0s!important;
}

/* Botão abrir/fechar sidebar: grande, legível e reconhecível. */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"]{
  position:fixed!important;
  top:10px!important;
  left:10px!important;
  z-index:100000!important;
  width:auto!important;
  height:auto!important;
}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button{
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  gap:7px!important;
  min-width:92px!important;
  min-height:44px!important;
  padding:0 13px!important;
  border-radius:13px!important;
  border:2px solid rgba(255,215,90,.92)!important;
  background:linear-gradient(135deg,#07263D,#0A4168 58%,#061A2B)!important;
  color:#FFE477!important;
  -webkit-text-fill-color:#FFE477!important;
  box-shadow:0 8px 24px rgba(0,0,0,.38),0 0 20px rgba(0,174,239,.26),0 0 12px rgba(255,215,90,.18)!important;
  font-size:0!important;
  font-weight:950!important;
  opacity:1!important;
  transition:transform .18s ease,box-shadow .18s ease!important;
}
[data-testid="stSidebarCollapseButton"] button::after,
[data-testid="stSidebarCollapsedControl"] button::after,
[data-testid="collapsedControl"] button::after{
  color:#FFE477!important;
  -webkit-text-fill-color:#FFE477!important;
  font-size:.78rem!important;
  font-weight:950!important;
  line-height:1!important;
  letter-spacing:.015em!important;
  white-space:nowrap!important;
}
[data-testid="stSidebarCollapsedControl"] button::after,
[data-testid="collapsedControl"] button::after{content:"Menu"}
[data-testid="stSidebarCollapseButton"] button::after{content:"Fechar"}
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg{
  width:19px!important;
  height:19px!important;
  min-width:19px!important;
  color:#FFE477!important;
  fill:#FFE477!important;
  stroke:#FFE477!important;
  opacity:1!important;
}
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stSidebarCollapsedControl"] button:hover,
[data-testid="collapsedControl"] button:hover{
  transform:translateY(-1px) scale(1.02)!important;
  box-shadow:0 11px 28px rgba(0,0,0,.44),0 0 25px rgba(0,174,239,.34),0 0 16px rgba(255,215,90,.24)!important;
}

/* Login não precisa de menu lateral. */
body:has(input[aria-label="E-mail"]):has(input[aria-label="Senha"]) [data-testid="stSidebarCollapsedControl"],
body:has(input[aria-label="E-mail"]):has(input[aria-label="Senha"]) [data-testid="collapsedControl"],
body:has(input[aria-label="E-mail"]):has(input[aria-label="Senha"]) [data-testid="stSidebarCollapseButton"]{
  display:none!important;
}

@media(max-width:768px){
  [data-testid="stSidebarCollapsedControl"],
  [data-testid="collapsedControl"]{
    top:8px!important;
    left:8px!important;
  }
  [data-testid="stSidebarCollapseButton"] button,
  [data-testid="stSidebarCollapsedControl"] button,
  [data-testid="collapsedControl"] button{
    min-width:88px!important;
    min-height:46px!important;
    padding:0 12px!important;
    border-radius:14px!important;
  }
  [data-testid="stSidebarCollapseButton"] button::after,
  [data-testid="stSidebarCollapsedControl"] button::after,
  [data-testid="collapsedControl"] button::after{
    font-size:.76rem!important;
  }
  .stApp input:not([type="checkbox"]):not([type="radio"]):not([type="file"]),
  .stApp textarea,
  .stApp [data-baseweb="select"] [role="combobox"]{
    font-size:16px!important;
    line-height:1.35!important;
  }
}
"""


_LIGHT_CONTRAST_CSS = r"""
/* Modo claro: fundo claro sempre recebe texto escuro. */
.stApp input:not([type="checkbox"]):not([type="radio"]):not([type="file"]),
.stApp textarea,
.stApp [data-baseweb="select"] [role="combobox"]{
  background:#FFFFFF!important;
  color:#17364A!important;
  -webkit-text-fill-color:#17364A!important;
  caret-color:#007FB8!important;
}
.stApp input:not([type="checkbox"]):not([type="radio"]):not([type="file"])::placeholder,
.stApp textarea::placeholder{
  color:#6B7F8C!important;
  -webkit-text-fill-color:#6B7F8C!important;
  opacity:1!important;
}
.stApp [data-baseweb="input"]>div,
.stApp [data-baseweb="textarea"]>div,
.stApp [data-baseweb="select"]>div,
.stApp [data-testid="stTextInput"]>div,
.stApp [data-testid="stTextArea"]>div,
.stApp [data-testid="stDateInput"]>div,
.stApp [data-testid="stNumberInput"]>div{
  background:#FFFFFF!important;
  border-color:rgba(0,127,184,.28)!important;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.60)!important;
}
.stApp [data-baseweb="select"] span,
.stApp [data-baseweb="select"] div,
.stApp [role="option"]{
  color:#17364A!important;
  -webkit-text-fill-color:#17364A!important;
}
.stApp [data-testid="stTextInput"] button,
.stApp [data-testid="stTextInput"] button svg,
.stApp button[aria-label*="password" i],
.stApp button[aria-label*="senha" i],
.stApp button[aria-label*="password" i] svg,
.stApp button[aria-label*="senha" i] svg{
  color:#17364A!important;
  fill:#17364A!important;
  stroke:#17364A!important;
}
.stApp input:-webkit-autofill,
.stApp input:-webkit-autofill:hover,
.stApp input:-webkit-autofill:focus{
  -webkit-text-fill-color:#17364A!important;
  caret-color:#17364A!important;
  -webkit-box-shadow:0 0 0 1000px #FFFFFF inset!important;
  box-shadow:0 0 0 1000px #FFFFFF inset!important;
  transition:background-color 99999s ease-out 0s!important;
}

/* No claro, o controle do menu usa azul sólido + texto branco para alto contraste. */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button{
  border-color:#B88400!important;
  background:linear-gradient(135deg,#087EAE,#006A98 58%,#075A82)!important;
  color:#FFFFFF!important;
  -webkit-text-fill-color:#FFFFFF!important;
  box-shadow:0 8px 22px rgba(31,67,86,.22),0 0 0 3px rgba(255,255,255,.86),0 0 18px rgba(0,127,184,.18)!important;
}
[data-testid="stSidebarCollapseButton"] button::after,
[data-testid="stSidebarCollapsedControl"] button::after,
[data-testid="collapsedControl"] button::after{
  color:#FFFFFF!important;
  -webkit-text-fill-color:#FFFFFF!important;
}
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg{
  color:#FFFFFF!important;
  fill:#FFFFFF!important;
  stroke:#FFFFFF!important;
}
"""


def inject_accessibility_css() -> None:
    """Aplica contraste final e reforça o controle de navegação em todos os temas."""
    mode = current_theme_mode()
    if mode == "light":
        css = f"<style>{_DARK_CONTRAST_CSS}{_LIGHT_CONTRAST_CSS}</style>"
    elif mode == "dark":
        css = f"<style>{_DARK_CONTRAST_CSS}</style>"
    else:
        css = (
            f"<style>{_DARK_CONTRAST_CSS}"
            f"@media (prefers-color-scheme: light){{{_LIGHT_CONTRAST_CSS}}}"
            "</style>"
        )
    st.markdown(css, unsafe_allow_html=True)
