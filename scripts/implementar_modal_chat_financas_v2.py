from pathlib import Path
import re

APP = Path('app.py')
text = APP.read_text(encoding='utf-8')

text = text.replace('APP_BUILD = "2026.09.12.1"', 'APP_BUILD = "2026.09.12.4"')

start = text.index('def render_ai_chat(input_key: str, *, fragment_rerun: bool = False) -> None:')
end = text.index('\ndef render_ai() -> None:', start)

replacement = r'''def _archive_current_ai_conversation() -> None:
    messages = list(st.session_state.get("ai_messages") or [])
    if not messages:
        return
    history = st.session_state.setdefault("ai_conversation_history", [])
    user_messages = [str(item.get("content") or "") for item in messages if item.get("role") == "user"]
    title = (user_messages[0][:52] + ("…" if len(user_messages[0]) > 52 else "")) if user_messages else "Conversa RENOVA IA"
    history.insert(
        0,
        {
            "id": str(len(history) + 1),
            "title": title,
            "messages": [dict(item) for item in messages],
        },
    )
    del history[12:]


def _reset_ai_conversation(*, archive: bool = True) -> None:
    if archive:
        _archive_current_ai_conversation()
    for key in [
        "ai_messages",
        "ai_pending_action",
        "ai_pending_command",
        "ai_pending_context",
        "ai_last_error",
        "ai_last_prompt",
    ]:
        st.session_state.pop(key, None)
    _ensure_ai_messages()


def _restore_ai_conversation(index: int) -> None:
    history = st.session_state.get("ai_conversation_history") or []
    if not history or index < 0 or index >= len(history):
        return
    _archive_current_ai_conversation()
    st.session_state.ai_messages = [dict(item) for item in history[index].get("messages", [])]
    for key in ["ai_pending_action", "ai_pending_command", "ai_pending_context", "ai_last_error", "ai_last_prompt"]:
        st.session_state.pop(key, None)


def render_ai_chat(input_key: str, *, fragment_rerun: bool = False, show_suggestions: bool = False) -> None:
    _ensure_ai_messages()

    if show_suggestions and not any(message.get("role") == "user" for message in st.session_state.ai_messages):
        st.markdown(
            """
            <div class="ai-welcome-card">
              <div class="ai-welcome-icon">🤖</div>
              <div><strong>RENOVA IA Financeira</strong><br><span>Olá! 👋 Como posso ajudar com suas finanças hoje?</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Sugestões rápidas")
        suggestions = [
            "Analisar minhas finanças",
            "Registrar uma despesa",
            "Ver contas atrasadas",
            "Como posso economizar?",
        ]
        cols = st.columns(2)
        for idx, suggestion in enumerate(suggestions):
            with cols[idx % 2]:
                if st.button(suggestion, key=f"ai_suggestion_{input_key}_{idx}", use_container_width=True):
                    st.session_state.ai_last_prompt = suggestion
                    with st.spinner("RENOVA IA está digitando…"):
                        _execute_ai_prompt(suggestion)
                    st.rerun(scope="fragment" if fragment_rerun else "app")

    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.get("ai_pending_action"):
        st.warning("Existe uma ação sensível aguardando confirmação. Digite **CONFIRMAR** ou **CANCELAR**.")
    elif st.session_state.get("ai_pending_context"):
        st.info("Consultando informações… preciso de mais um dado para concluir o pedido.")

    if st.session_state.get("ai_last_error"):
        st.error("Não foi possível concluir sua solicitação.")
        if st.button("↻ Tentar novamente", key=f"retry_{input_key}", use_container_width=True):
            retry_prompt = str(st.session_state.get("ai_last_prompt") or "").strip()
            st.session_state.pop("ai_last_error", None)
            if retry_prompt:
                with st.spinner("RENOVA IA está digitando…"):
                    _execute_ai_prompt(retry_prompt)
                st.rerun(scope="fragment" if fragment_rerun else "app")

    prompt = st.chat_input("Digite sua mensagem…", key=input_key)
    if prompt:
        st.session_state.ai_last_prompt = prompt
        st.session_state.pop("ai_last_error", None)
        with st.spinner("RENOVA IA está digitando…"):
            _execute_ai_prompt(prompt)
        if fragment_rerun:
            st.rerun(scope="fragment")
        else:
            st.rerun()


def render_ai_subscription_sales() -> None:
    # Regra de funil: assinatura sempre passa pela página comercial antes do checkout.
    st.switch_page("pages/Assinar_RENOVA_IA.py")


@st.dialog("RENOVA IA", width="small")
def open_ai_dialog() -> None:
    personalized = has_personalized_ai_training_access()
    st.session_state.ai_chat_open = True
    st.session_state.ai_chat_minimized = False

    st.markdown(
        """
        <style>
        /* RENOVA IA • painel flutuante desktop / tela cheia mobile */
        div[data-testid="stDialog"]{background:transparent!important;pointer-events:none!important}
        div[role="dialog"]{
          position:fixed!important;right:24px!important;bottom:22px!important;left:auto!important;top:auto!important;
          transform:none!important;width:440px!important;max-width:calc(100vw - 32px)!important;
          height:min(720px,85vh)!important;max-height:85vh!important;margin:0!important;
          pointer-events:auto!important;overflow:hidden!important;
          border-radius:20px!important;border:1px solid rgba(25,217,255,.25)!important;
          background:linear-gradient(180deg,#0B1E31 0%,#081827 100%)!important;
          box-shadow:0 26px 70px rgba(0,0,0,.50),0 0 32px rgba(25,217,255,.08)!important;
          animation:aiPanelIn .2s ease-out!important;
        }
        @keyframes aiPanelIn{from{opacity:0;transform:translateY(16px) scale(.985)}to{opacity:1;transform:none}}
        div[role="dialog"] > div{height:100%!important;max-height:100%!important;padding:0!important;overflow:hidden!important}
        div[role="dialog"] [data-testid="stDialog"]{height:100%!important;max-height:100%!important;padding:0!important;overflow:hidden!important}
        div[role="dialog"] button[aria-label="Close"]{display:none!important}

        .ai-panel-header{
          position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:10px;
          padding:14px 15px 10px;border-bottom:1px solid rgba(255,255,255,.08);
          background:rgba(11,30,49,.97);backdrop-filter:blur(18px);
        }
        .ai-panel-avatar{width:38px;height:38px;border-radius:50%;display:grid;place-items:center;flex:0 0 38px;
          background:linear-gradient(135deg,#087FF5,#18DFA5);box-shadow:0 0 18px rgba(25,217,255,.20)}
        .ai-panel-copy{min-width:0;flex:1;line-height:1.14}
        .ai-panel-copy strong{display:block;color:#F7FBFF;font-size:.92rem}
        .ai-panel-copy span{display:flex;align-items:center;gap:5px;color:#A7BED4;font-size:.68rem;margin-top:3px}
        .ai-online-dot{width:7px;height:7px;border-radius:50%;background:#18DFA5;box-shadow:0 0 9px rgba(24,223,165,.75)}
        .ai-panel-tools{display:flex;justify-content:flex-end;gap:6px}

        .st-key-ai_chat_modal_shell{
          height:calc(min(720px,85vh) - 150px)!important;overflow-y:auto!important;overflow-x:hidden!important;
          padding:12px 12px 98px!important;background:
            radial-gradient(circle at 18% 8%,rgba(24,223,165,.035),transparent 30%),
            linear-gradient(180deg,#0A1A2A,#071522)!important;
          scrollbar-width:thin;scrollbar-color:rgba(25,217,255,.28) transparent;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatMessage"]{
          width:fit-content!important;max-width:82%!important;margin:8px 0!important;padding:9px 12px!important;
          border:1px solid rgba(255,255,255,.08)!important;border-radius:16px 16px 16px 5px!important;
          background:#12283A!important;box-shadow:0 7px 18px rgba(0,0,0,.15)!important;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]){
          margin-left:auto!important;max-width:78%!important;border-radius:16px 16px 5px 16px!important;
          border-color:rgba(24,223,165,.18)!important;background:linear-gradient(135deg,#087F6B,#0A967C)!important;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatMessage"] p{color:#F7FBFF!important;line-height:1.45!important;margin:.05rem 0!important}
        .st-key-ai_chat_modal_shell [data-testid="stChatMessageAvatarUser"],
        .st-key-ai_chat_modal_shell [data-testid="stChatMessageAvatarAssistant"]{transform:scale(.82)}

        .st-key-ai_chat_modal_shell [data-testid="stChatInput"]{
          position:sticky!important;bottom:0!important;z-index:30!important;margin-top:16px!important;
          min-height:54px!important;border-radius:17px!important;border:1px solid rgba(25,217,255,.24)!important;
          background:#102438!important;box-shadow:0 -14px 30px rgba(7,21,34,.90)!important;
        }
        .st-key-ai_chat_modal_shell [data-testid="stChatInput"] textarea{min-height:52px!important;max-height:132px!important;color:#F7FBFF!important}
        .st-key-ai_chat_modal_shell [data-testid="stChatInput"] textarea::placeholder{color:#93AFC1!important;opacity:1!important}
        .ai-disclaimer{text-align:center;color:#7F9AAD;font-size:.60rem;margin:-82px 18px 0;position:relative;z-index:35;pointer-events:none}

        .ai-welcome-card{display:flex;gap:10px;align-items:flex-start;padding:12px;border-radius:15px;margin:3px 0 10px;
          border:1px solid rgba(25,217,255,.13);background:rgba(16,40,58,.70)}
        .ai-welcome-icon{width:34px;height:34px;border-radius:50%;display:grid;place-items:center;background:rgba(25,217,255,.10)}
        .ai-welcome-card strong{color:#F7FBFF}.ai-welcome-card span{color:#AFC4D2;font-size:.78rem;line-height:1.4}

        .ai-menu-panel{padding:8px;margin:0 12px 8px;border-radius:14px;border:1px solid rgba(25,217,255,.13);background:#0C2134}
        .ai-history-note{color:#8EAABD;font-size:.67rem;margin-bottom:6px}

        @media(max-width:768px){
          div[role="dialog"]{inset:0!important;width:100vw!important;max-width:100vw!important;height:100dvh!important;max-height:100dvh!important;border-radius:0!important;border:0!important}
          .st-key-ai_chat_modal_shell{height:calc(100dvh - 140px)!important;padding:10px 9px 104px!important}
          .st-key-ai_chat_modal_shell [data-testid="stChatMessage"]{max-width:88%!important}
          .st-key-ai_chat_modal_shell [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]){max-width:84%!important}
          .ai-panel-header{padding-top:max(12px,env(safe-area-inset-top))}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    header_left, menu_col, minimize_col, close_col = st.columns([5.7, .72, .72, .72])
    with header_left:
        mode_label = "IA Personalizada • Premium" if personalized else "IA Padrão • Gratuita"
        st.markdown(
            f"""
            <div class="ai-panel-header">
              <div class="ai-panel-avatar">🤖</div>
              <div class="ai-panel-copy"><strong>RENOVA IA</strong><span><i class="ai-online-dot"></i> Online • {mode_label}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with menu_col:
        if st.button("•••", key="ai_menu_toggle", help="Opções do chat", use_container_width=True):
            st.session_state.ai_chat_menu_open = not bool(st.session_state.get("ai_chat_menu_open"))
            st.rerun(scope="fragment")
    with minimize_col:
        if st.button("—", key="ai_minimize", help="Minimizar", use_container_width=True):
            st.session_state.ai_chat_open = False
            st.session_state.ai_chat_minimized = True
            st.rerun()
    with close_col:
        if st.button("✕", key="ai_close", help="Fechar chat", use_container_width=True):
            st.session_state.ai_chat_open = False
            st.session_state.ai_chat_minimized = False
            st.rerun()

    if st.session_state.get("ai_chat_menu_open"):
        with st.container(key="ai_menu_panel"):
            st.markdown('<div class="ai-menu-panel">', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("＋ Nova conversa", key="ai_menu_new", use_container_width=True):
                    _reset_ai_conversation(archive=True)
                    st.session_state.ai_chat_menu_open = False
                    st.rerun(scope="fragment")
                if st.button("🕘 Histórico", key="ai_menu_history", use_container_width=True):
                    st.session_state.ai_chat_history_open = not bool(st.session_state.get("ai_chat_history_open"))
                    st.rerun(scope="fragment")
            with c2:
                if st.button("🧹 Limpar conversa", key="ai_menu_clear", use_container_width=True):
                    _reset_ai_conversation(archive=False)
                    st.session_state.ai_chat_menu_open = False
                    st.rerun(scope="fragment")
                if st.button("⚙ Configurações", key="ai_menu_settings", use_container_width=True):
                    st.session_state.ai_chat_settings_open = not bool(st.session_state.get("ai_chat_settings_open"))
                    st.rerun(scope="fragment")
            if st.button("✕ Fechar chat", key="ai_menu_close", use_container_width=True):
                st.session_state.ai_chat_open = False
                st.session_state.ai_chat_minimized = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("ai_chat_history_open"):
        history = st.session_state.get("ai_conversation_history") or []
        if history:
            titles = [str(item.get("title") or "Conversa RENOVA IA") for item in history]
            choice = st.selectbox("Histórico de conversas", list(range(len(titles))), format_func=lambda i: titles[i], key="ai_history_choice")
            if st.button("Abrir conversa selecionada", key="ai_history_restore", use_container_width=True):
                _restore_ai_conversation(int(choice))
                st.session_state.ai_chat_history_open = False
                st.session_state.ai_chat_menu_open = False
                st.rerun(scope="fragment")
        else:
            st.caption("Ainda não há conversas anteriores nesta sessão.")

    if st.session_state.get("ai_chat_settings_open"):
        st.checkbox("Exibir sugestões rápidas em novas conversas", value=True, key="ai_show_suggestions")
        st.caption("As preferências do chat ficam preservadas enquanto sua sessão estiver ativa.")

    with st.container(key="ai_chat_modal_shell"):
        render_ai_chat(
            "ai_modal_input",
            fragment_rerun=True,
            show_suggestions=bool(st.session_state.get("ai_show_suggestions", True)),
        )
    st.markdown('<div class="ai-disclaimer">A RENOVA IA pode cometer erros. Confira informações importantes.</div>', unsafe_allow_html=True)

'''

text = text[:start] + replacement + text[end:]

old_tail = '''pages[page]()\n\nif AI_FAB_CLICKED:\n    open_ai_dialog()'''
new_tail = '''pages[page]()\n\nif AI_FAB_CLICKED:\n    st.session_state.ai_chat_open = True\n    st.session_state.ai_chat_minimized = False\n\nif st.session_state.get("ai_chat_open"):\n    open_ai_dialog()'''
if old_tail not in text:
    raise SystemExit('Trecho final do chat não encontrado.')
text = text.replace(old_tail, new_tail)

APP.write_text(text, encoding='utf-8')
print('Modal flutuante RENOVA IA Financeira v2 aplicado em app.py')
