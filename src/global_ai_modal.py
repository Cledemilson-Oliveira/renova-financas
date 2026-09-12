from __future__ import annotations

import time

import streamlit as st
import streamlit.components.v1 as components

from src.access import is_owner
from src.ai_finance import confirm_pending_action, process_message
from src.repository import fetch_financial_data, has_active_ai_subscription
from src.supabase_client import current_user
from src.theme import floating_ai_button


_AI_ACCESS_TTL_SECONDS = 20.0


def _session_user_id() -> str:
    user = current_user()
    return str(user.id) if user and getattr(user, "id", None) else ""


def _has_personalized_access(user_id: str) -> bool:
    if not user_id:
        return False

    cached_user = str(st.session_state.get("_global_ai_access_user_id") or "")
    cached_at = float(st.session_state.get("_global_ai_access_at") or 0.0)
    if cached_user == user_id and cached_at and (time.monotonic() - cached_at) < _AI_ACCESS_TTL_SECONDS:
        return bool(st.session_state.get("_global_ai_access_value", False))

    try:
        value = bool(is_owner(user_id) or has_active_ai_subscription(user_id))
    except Exception:
        value = False

    st.session_state._global_ai_access_user_id = user_id
    st.session_state._global_ai_access_value = value
    st.session_state._global_ai_access_at = time.monotonic()
    return value


def _ensure_messages() -> None:
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = [
            {
                "role": "assistant",
                "content": (
                    "Olá! Eu sou a **RENOVA IA Financeira**. Posso analisar seus números e executar "
                    "ações de gestão financeira pelo chat."
                ),
            }
        ]


def _execute_prompt(user_id: str, prompt: str) -> None:
    _ensure_messages()
    st.session_state.ai_messages.append({"role": "user", "content": prompt})
    normalized = prompt.strip().upper()
    pending = st.session_state.get("ai_pending_action")

    try:
        if pending and normalized == "CONFIRMAR":
            result = confirm_pending_action(
                user_id,
                str(st.session_state.get("ai_pending_command") or ""),
                pending,
            )
            st.session_state.pop("ai_pending_action", None)
            st.session_state.pop("ai_pending_command", None)
        elif pending and normalized == "CANCELAR":
            st.session_state.pop("ai_pending_action", None)
            st.session_state.pop("ai_pending_command", None)
            st.session_state.ai_messages.append(
                {
                    "role": "assistant",
                    "content": "✅ A ação sensível foi cancelada e nenhuma alteração foi feita.",
                }
            )
            return
        elif pending:
            st.session_state.ai_messages.append(
                {
                    "role": "assistant",
                    "content": "Há uma ação sensível pendente. Digite **CONFIRMAR** ou **CANCELAR** antes de enviar outro comando.",
                }
            )
            return
        else:
            bundle = fetch_financial_data(user_id)
            bundle["_allow_personalized_training"] = _has_personalized_access(user_id)

            pending_context = st.session_state.get("ai_pending_context")
            effective_prompt = prompt
            if pending_context:
                original = str(pending_context.get("original_message") or "").strip()
                if original:
                    effective_prompt = f"{original} {prompt}".strip()

            result = process_message(user_id, effective_prompt, bundle)

            if result.pending_confirmation:
                st.session_state.ai_pending_action = result.pending_confirmation
                st.session_state.ai_pending_command = effective_prompt

            if result.pending_context:
                st.session_state.ai_pending_context = result.pending_context
            else:
                st.session_state.pop("ai_pending_context", None)

        st.session_state.ai_messages.append({"role": "assistant", "content": result.text})
        if result.executed:
            st.session_state.pop("ai_pending_context", None)
    except Exception as exc:
        st.session_state.ai_messages.append(
            {
                "role": "assistant",
                "content": "Não consegui executar esse comando agora. Nenhuma ação parcial foi considerada concluída.",
            }
        )
        st.session_state.ai_last_error = str(exc)


def _scroll_to_latest(*, force: bool = False) -> None:
    count = len(st.session_state.get("ai_messages") or [])
    last_count = int(st.session_state.get("_global_ai_last_scroll_count") or -1)
    if not force and count == last_count and not st.session_state.pop("_global_ai_force_scroll", False):
        return

    st.session_state._global_ai_last_scroll_count = count
    components.html(
        """
        <script>
        (() => {
          const doc = window.parent.document;
          const scroll = () => {
            const shell = doc.querySelector('.st-key-global_ai_chat_shell');
            if (shell) shell.scrollTop = shell.scrollHeight;
            if (window.parent.matchMedia('(min-width: 769px)').matches) {
              const input = doc.querySelector('.st-key-global_ai_chat_composer textarea');
              if (input && doc.activeElement !== input) {
                try { input.focus({preventScroll:true}); } catch (_) {}
              }
            }
          };
          requestAnimationFrame(scroll);
          setTimeout(scroll, 70);
          setTimeout(scroll, 220);
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def _render_chat(user_id: str) -> None:
    _ensure_messages()

    st.markdown(
        """
        <span class="renova-global-ai-marker"></span>
        <style>
        div[role="dialog"]:has(.renova-global-ai-marker){
          position:fixed!important;
          right:24px!important;
          bottom:22px!important;
          left:auto!important;
          top:auto!important;
          transform:none!important;
          width:440px!important;
          max-width:calc(100vw - 32px)!important;
          height:min(720px,85vh)!important;
          max-height:85vh!important;
          margin:0!important;
          overflow:hidden!important;
          border-radius:20px!important;
          border:1px solid rgba(25,217,255,.25)!important;
          background:linear-gradient(180deg,#0B1E31 0%,#081827 100%)!important;
          box-shadow:0 26px 70px rgba(0,0,0,.50),0 0 32px rgba(25,217,255,.08)!important;
        }
        div[role="dialog"]:has(.renova-global-ai-marker) > div{
          height:100%!important;
          max-height:100%!important;
          overflow:hidden!important;
          padding-bottom:0!important;
        }
        .renova-ai-chat-status{
          position:sticky;top:0;z-index:20;
          display:flex;align-items:center;gap:7px;
          margin:0 0 8px;padding:8px 10px;
          border:1px solid rgba(25,217,255,.12);border-radius:12px;
          background:rgba(11,30,49,.96);color:#A7BED4;font-size:.70rem;
        }
        .renova-ai-chat-status .dot{width:7px;height:7px;border-radius:50%;background:#18DFA5;box-shadow:0 0 9px rgba(24,223,165,.7)}
        .st-key-global_ai_chat_shell{
          height:calc(min(720px,85vh) - 190px)!important;
          min-height:0!important;
          overflow-y:scroll!important;
          overflow-x:hidden!important;
          overscroll-behavior-y:contain!important;
          -webkit-overflow-scrolling:touch!important;
          scrollbar-gutter:stable!important;
          padding:6px 5px 14px!important;
          scrollbar-width:thin;
          scrollbar-color:rgba(25,217,255,.38) transparent;
        }
        .st-key-global_ai_chat_shell [data-testid="stChatMessage"]{
          width:fit-content!important;max-width:82%!important;
          margin:8px 0!important;padding:9px 12px!important;
          border:1px solid rgba(255,255,255,.08)!important;
          border-radius:16px 16px 16px 5px!important;
          background:#12283A!important;
        }
        .st-key-global_ai_chat_shell [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]){
          margin-left:auto!important;max-width:78%!important;
          border-radius:16px 16px 5px 16px!important;
          border-color:rgba(24,223,165,.18)!important;
          background:linear-gradient(135deg,#087F6B,#0A967C)!important;
        }
        .st-key-global_ai_chat_shell [data-testid="stChatMessage"] p{color:#F7FBFF!important;line-height:1.45!important;margin:.05rem 0!important}
        .st-key-global_ai_chat_composer{
          position:absolute!important;left:0!important;right:0!important;bottom:0!important;z-index:50!important;
          padding:10px 12px 8px!important;
          border-top:1px solid rgba(255,255,255,.08)!important;
          background:rgba(8,24,39,.985)!important;
          backdrop-filter:blur(18px)!important;
          box-shadow:0 -16px 34px rgba(0,0,0,.38)!important;
        }
        .st-key-global_ai_chat_composer [data-testid="stChatInput"]{
          position:relative!important;inset:auto!important;margin:0!important;
          min-height:54px!important;border-radius:17px!important;
          border:1px solid rgba(25,217,255,.28)!important;
          background:#102438!important;
        }
        .st-key-global_ai_chat_composer [data-testid="stChatInput"] textarea{
          min-height:52px!important;max-height:132px!important;color:#F7FBFF!important;
        }
        .global-ai-disclaimer{text-align:center;color:#7F9AAD;font-size:.60rem;margin:5px 8px 0}
        @media(max-width:768px){
          div[role="dialog"]:has(.renova-global-ai-marker){
            inset:0!important;width:100vw!important;max-width:100vw!important;
            height:100dvh!important;max-height:100dvh!important;
            border-radius:0!important;border:0!important;
          }
          .st-key-global_ai_chat_shell{height:calc(100dvh - 190px)!important;padding:6px 4px 14px!important}
          .st-key-global_ai_chat_composer{padding-bottom:max(10px,env(safe-area-inset-bottom))!important}
          .st-key-global_ai_chat_composer [data-testid="stChatInput"] textarea{font-size:16px!important}
          .st-key-global_ai_chat_shell [data-testid="stChatMessage"]{max-width:88%!important}
          .st-key-global_ai_chat_shell [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]){max-width:84%!important}
        }
        </style>
        <div class="renova-ai-chat-status">
          <span class="dot"></span>
          RENOVA IA online • pronta para consultar, analisar e executar sua gestão financeira
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="global_ai_chat_shell"):
        for message in st.session_state.ai_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if st.session_state.get("ai_pending_action"):
            st.warning("Existe uma ação sensível aguardando confirmação. Digite **CONFIRMAR** ou **CANCELAR**.")
        elif st.session_state.get("ai_pending_context"):
            st.info("Estou aguardando a informação que falta para concluir o pedido anterior.")

    with st.container(key="global_ai_chat_composer"):
        prompt = st.chat_input("Mensagem para a RENOVA IA...", key="global_ai_modal_input")
        st.markdown(
            '<div class="global-ai-disclaimer">A RENOVA IA pode cometer erros. Confira informações importantes.</div>',
            unsafe_allow_html=True,
        )
        if prompt:
            _execute_prompt(user_id, prompt)
            st.rerun(scope="fragment")

    _scroll_to_latest()


@st.dialog("RENOVA IA Financeira", width="small")
def _open_global_dialog(user_id: str) -> None:
    if not user_id:
        st.error("Sua sessão não foi identificada. Entre novamente para usar a RENOVA IA.")
        return

    if _has_personalized_access(user_id):
        st.caption("IA Personalizada ativa • memória e treinamentos privados disponíveis.")
    else:
        st.caption("IA Padrão ativa • lançamentos, consultas e análises financeiras disponíveis.")

    _render_chat(user_id)


def render_global_ai_assistant(user_id: str | None = None) -> None:
    """Exibe o botão flutuante e abre o chat da RENOVA IA em qualquer página autenticada."""
    target_user_id = str(user_id or _session_user_id() or "")
    if floating_ai_button():
        st.session_state._global_ai_force_scroll = True
        _open_global_dialog(target_user_id)
