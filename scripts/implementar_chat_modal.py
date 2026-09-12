from pathlib import Path

APP = Path("app.py")
text = APP.read_text(encoding="utf-8")

old = '''@st.dialog("🤖 Assistente Financeiro IA", width="large")
def open_ai_dialog() -> None:
    personalized = has_personalized_ai_training_access()
    if personalized:
        st.caption("IA Personalizada ativa: execução financeira + memória e treinamentos da sua conta.")
        st.page_link("pages/Treinamento_IA.py", label="🧠 Treinar minha IA", use_container_width=True)
    else:
        st.caption("IA Padrão gratuita ativa: lançamentos, consultas, análises e gestão essencial pelo chat.")
        if st.button("🧠 Desbloquear treinamento personalizado", key="modal_upgrade_training", use_container_width=True):
            st.session_state.nav_page = "Assinar RENOVA IA"
            st.rerun()
    render_ai_chat("ai_modal_input", fragment_rerun=True)
'''

new = '''@st.dialog("🤖 Assistente Financeiro IA", width="large")
def open_ai_dialog() -> None:
    personalized = has_personalized_ai_training_access()

    st.markdown(
        """
        <style>
        /* RENOVA IA • modal de conversa inspirado em mensageiros modernos */
        div[role="dialog"]{
          width:min(94vw,1120px)!important;
          max-width:1120px!important;
        }
        div[role="dialog"] > div{
          border-radius:24px!important;
          border:1px solid rgba(25,217,255,.22)!important;
          background:
            radial-gradient(circle at 90% 0%,rgba(25,217,255,.09),transparent 24%),
            linear-gradient(145deg,rgba(5,18,31,.99),rgba(2,9,15,.995))!important;
          box-shadow:0 28px 90px rgba(0,0,0,.58),0 0 40px rgba(25,217,255,.08)!important;
          overflow:hidden!important;
        }
        div[role="dialog"] [data-testid="stDialog"]{
          max-height:88vh!important;
        }
        .ai-modal-status{
          display:flex;align-items:center;gap:10px;flex-wrap:wrap;
          margin:-2px 0 10px;padding:10px 12px;border-radius:16px;
          border:1px solid rgba(25,217,255,.16);
          background:rgba(8,31,50,.72);
        }
        .ai-modal-avatar{
          width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;
          background:linear-gradient(135deg,#087FF5,#18DFA5);color:white;font-size:18px;
          box-shadow:0 0 20px rgba(25,217,255,.24);
        }
        .ai-modal-status-copy{line-height:1.15}
        .ai-modal-status-copy strong{display:block;color:#F5FAFF;font-size:.88rem}
        .ai-modal-status-copy span{color:#9FC4D8;font-size:.68rem}
        .ai-online-dot{width:8px;height:8px;border-radius:50%;background:#18DFA5;box-shadow:0 0 10px rgba(24,223,165,.72)}

        .st-key-ai_chat_modal_shell{
          position:relative!important;
          min-height:470px!important;
          max-height:64vh!important;
          overflow-y:auto!important;
          padding:12px 10px 90px!important;
          margin-top:8px!important;
          border:1px solid rgba(25,217,255,.12)!important;
          border-radius:20px!important;
          background:
            radial-gradient(circle at 18% 12%,rgba(24,223,165,.035),transparent 30%),
            linear-gradient(180deg,rgba(2,12,21,.82),rgba(3,15,26,.94))!important;
          scrollbar-width:thin;
          scrollbar-color:rgba(25,217,255,.35) transparent;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatMessage"]{
          width:fit-content!important;
          max-width:min(78%,760px)!important;
          margin:8px 0!important;
          padding:10px 13px!important;
          border-radius:18px 18px 18px 5px!important;
          border:1px solid rgba(25,217,255,.15)!important;
          background:linear-gradient(145deg,rgba(12,37,57,.96),rgba(7,24,39,.98))!important;
          box-shadow:0 8px 20px rgba(0,0,0,.18)!important;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]){
          margin-left:auto!important;
          border-radius:18px 18px 5px 18px!important;
          border-color:rgba(24,223,165,.24)!important;
          background:linear-gradient(135deg,#0A6F60,#0D8A72)!important;
          box-shadow:0 8px 22px rgba(0,0,0,.18),0 0 18px rgba(24,223,165,.06)!important;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatMessage"] p{
          color:#F4FAFF!important;
          line-height:1.5!important;
          margin-bottom:.15rem!important;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatMessageAvatarUser"],
        .st-key-ai_chat_modal_shell [data-testid="stChatMessageAvatarAssistant"]{
          transform:scale(.86);
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatInput"]{
          position:sticky!important;
          bottom:0!important;
          z-index:20!important;
          margin-top:18px!important;
          border-radius:999px!important;
          border:1px solid rgba(25,217,255,.24)!important;
          background:rgba(6,24,39,.96)!important;
          box-shadow:0 -10px 32px rgba(2,9,15,.46),0 8px 24px rgba(0,0,0,.22)!important;
          backdrop-filter:blur(16px)!important;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatInput"] textarea{
          min-height:48px!important;
          color:#F5FAFF!important;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatInput"] textarea::placeholder{color:#7896AA!important}

        @media(max-width:768px){
          div[role="dialog"]{width:98vw!important;max-width:98vw!important}
          div[role="dialog"] > div{border-radius:18px!important}
          .st-key-ai_chat_modal_shell{min-height:58vh!important;max-height:68vh!important;padding:8px 6px 84px!important}
          .st-key-ai_chat_modal_shell [data-testid="stChatMessage"]{max-width:90%!important;padding:9px 11px!important}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    top_left, top_right = st.columns([3.3, 1.15])
    with top_left:
        mode_label = "IA Personalizada • Premium" if personalized else "IA Padrão • Gratuita"
        st.markdown(
            f"""
            <div class="ai-modal-status">
              <div class="ai-modal-avatar">🤖</div>
              <div class="ai-modal-status-copy">
                <strong>RENOVA IA Financeira</strong>
                <span>{mode_label} • pronta para analisar e executar</span>
              </div>
              <div class="ai-online-dot" title="Online"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top_right:
        if st.button("＋ Nova conversa", key="ai_new_conversation", use_container_width=True):
            for key in ["ai_messages", "ai_pending_action", "ai_pending_command", "ai_pending_context", "ai_last_error"]:
                st.session_state.pop(key, None)
            _ensure_ai_messages()
            st.rerun(scope="fragment")

    if personalized:
        action_left, action_right = st.columns([2.4, 1])
        with action_left:
            st.caption("🟢 Online • memória e treinamentos personalizados ativos nesta conta.")
        with action_right:
            st.page_link("pages/Treinamento_IA.py", label="🧠 Treinar minha IA", use_container_width=True)
    else:
        action_left, action_right = st.columns([2.25, 1])
        with action_left:
            st.caption("🟢 Online • lançamentos, consultas, análises e gestão essencial disponíveis gratuitamente.")
        with action_right:
            if st.button("🧠 Personalizar IA", key="modal_upgrade_training", use_container_width=True):
                st.session_state.nav_page = "Assinar RENOVA IA"
                st.rerun()

    with st.container(key="ai_chat_modal_shell"):
        render_ai_chat("ai_modal_input", fragment_rerun=True)
'''

if old not in text:
    raise SystemExit("Bloco original do modal RENOVA IA não encontrado; abortando para evitar alteração incorreta.")

text = text.replace(old, new, 1)
text = text.replace('APP_BUILD = "2026.09.12.1"', 'APP_BUILD = "2026.09.12.2"', 1)
APP.write_text(text, encoding="utf-8")
print("Modal RENOVA IA atualizado para interface estilo ChatGPT/WhatsApp.")
