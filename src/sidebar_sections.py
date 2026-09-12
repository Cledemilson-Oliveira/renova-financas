from __future__ import annotations

from html import escape
import os

import streamlit as st

from .sidebar_runtime import ECOSSISTEMA_RENOVA_PUBLIC_URL
from .theme_modes import render_appearance_selector
from .ui import is_mobile


CREATOR_NAME = "Cledemilson Oliveira De Assis"


def _company_cnpj() -> str:
    """Obtém o CNPJ público configurado para o Ecossistema RENOVA.

    O valor pode ser definido em Streamlit Secrets como RENOVA_COMPANY_CNPJ
    ou por variável de ambiente de mesmo nome. Nunca inventamos um documento.
    """
    value = ""
    try:
        value = str(st.secrets.get("RENOVA_COMPANY_CNPJ", "") or "").strip()
    except Exception:
        value = ""
    if not value:
        value = str(os.getenv("RENOVA_COMPANY_CNPJ", "") or "").strip()
    return value


def render_sidebar_appearance() -> None:
    """Renderiza a seção de aparência depois da navegação principal."""
    if is_mobile():
        return

    with st.expander("🎨 APARÊNCIA E SISTEMA", expanded=False):
        render_appearance_selector()

        try:
            from .supabase_client import current_user

            user = current_user()
            uid = str(user.id) if user and getattr(user, "id", None) else ""
            if uid:
                st.caption("ATALHOS DO SISTEMA")
                st.page_link(
                    "pages/Planejamento_Caixa.py",
                    label="📈 Planejamento de Caixa",
                    use_container_width=True,
                )

                try:
                    from .access import is_owner

                    if is_owner(uid):
                        st.page_link(
                            "pages/Administracao.py",
                            label="🛡️ Gestão de Usuários",
                            use_container_width=True,
                        )
                except Exception:
                    pass
        except Exception:
            pass


def render_ecosystem_card() -> None:
    """Card institucional e comercial no rodapé estrutural da sidebar."""
    if is_mobile():
        return

    cnpj = _company_cnpj()
    cnpj_html = escape(cnpj) if cnpj else "CNPJ não informado"

    st.markdown(
        f"""
        <style>
        .renova-company-card{{
          position:relative;
          overflow:hidden;
          margin:12px 2px 8px;
          padding:15px;
          border-radius:17px;
          border:1px solid rgba(25,217,255,.34);
          background:
            radial-gradient(circle at 100% 0%,rgba(116,87,255,.18),transparent 40%),
            linear-gradient(145deg,#0B2038,#071629);
          box-shadow:0 14px 30px rgba(0,0,0,.24),0 0 18px rgba(25,217,255,.06);
        }}
        .renova-company-card:before{{
          content:"";
          position:absolute;
          left:0;right:0;top:0;height:2px;
          background:linear-gradient(90deg,transparent,#19D9FF,#087FF5,#7457FF,transparent);
        }}
        .renova-company-kicker{{
          color:#19D9FF;
          font-size:.52rem;
          font-weight:950;
          letter-spacing:.14em;
          margin-bottom:7px;
        }}
        .renova-company-title{{
          color:#F5FAFF;
          font-size:.92rem;
          font-weight:950;
          line-height:1.2;
        }}
        .renova-company-copy{{
          color:#A7BED4;
          font-size:.61rem;
          line-height:1.45;
          margin:5px 0 11px;
        }}
        .renova-company-info{{
          display:grid;
          gap:7px;
          margin-bottom:11px;
        }}
        .renova-company-row{{
          padding:8px 9px;
          border-radius:10px;
          border:1px solid rgba(25,217,255,.13);
          background:rgba(25,217,255,.045);
        }}
        .renova-company-row span{{
          display:block;
          color:#7FA3BB;
          font-size:.46rem;
          font-weight:900;
          letter-spacing:.08em;
          margin-bottom:3px;
        }}
        .renova-company-row strong{{
          display:block;
          color:#EDF8FF;
          font-size:.58rem;
          font-weight:850;
          line-height:1.35;
          word-break:break-word;
        }}
        .renova-company-card .cnpj-pending{{color:#A7BED4!important}}
        .renova-company-cta{{
          display:flex;
          align-items:center;
          justify-content:center;
          min-height:38px;
          padding:0 10px;
          border-radius:10px;
          text-decoration:none!important;
          background:linear-gradient(112deg,#087FF5,#19D9FF 52%,#7457FF);
          border:1px solid rgba(25,217,255,.74);
          color:#FFFFFF!important;
          -webkit-text-fill-color:#FFFFFF!important;
          font-size:.59rem;
          font-weight:950;
          box-shadow:0 8px 20px rgba(0,0,0,.24),0 0 16px rgba(25,217,255,.10);
          transition:.18s ease;
        }}
        .renova-company-cta:hover{{
          transform:translateY(-1px);
          filter:brightness(1.08);
          color:#FFFFFF!important;
        }}
        </style>

        <section class="renova-company-card" aria-label="Informações do Ecossistema RENOVA">
          <div class="renova-company-kicker">ECOSSISTEMA RENOVA</div>
          <div class="renova-company-title">Tecnologia, gestão e crescimento em um só ecossistema.</div>
          <div class="renova-company-copy">RENOVA Finanças faz parte da estrutura oficial do Ecossistema RENOVA.</div>

          <div class="renova-company-info">
            <div class="renova-company-row">
              <span>SISTEMA CRIADO POR</span>
              <strong>{escape(CREATOR_NAME)}</strong>
            </div>
            <div class="renova-company-row">
              <span>CNPJ DA EMPRESA</span>
              <strong class="{'cnpj-pending' if not cnpj else ''}">{cnpj_html}</strong>
            </div>
          </div>

          <a class="renova-company-cta" href="{ECOSSISTEMA_RENOVA_PUBLIC_URL}" target="_blank" rel="noopener noreferrer">
            Conhecer o Ecossistema RENOVA ↗
          </a>
        </section>
        """,
        unsafe_allow_html=True,
    )
