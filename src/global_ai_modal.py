from __future__ import annotations

import streamlit as st

from src.access import is_owner
from src.ai_finance import confirm_pending_action, process_message
from src.repository import fetch_financial_data, has_active_ai_subscription
from src.supabase_client import current_user
from src.theme import floating_ai_button


def _session_user_id() -> str:
    user = current_user()
    return str(user.id) if user and getattr(user, "id", None) else ""


def _has_personalized_access(user_id: str) -> bool:
    if not user_id:
        return False
    try:
        return bool(is_owner(user_id) or has_active_ai_subscription(user_id))
    except Exception:
        return False


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


def _render_chat(user_id: str) -> None:
    _ensure_messages()

    st.markdown(
        """
        <div class="renova-ai-chat-status">
          <span class="dot"></span>
          RENOVA IA online • pronta para consultar, analisar e executar sua gestão financeira
        </div>
        """,
        unsafe_allow_html=True,
    )

    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.get("ai_pending_action"):
        st.warning("Existe uma ação sensível aguardando confirmação. Digite **CONFIRMAR** ou **CANCELAR**.")
    elif st.session_state.get("ai_pending_context"):
        st.info("Estou aguardando a informação que falta para concluir o pedido anterior.")

    prompt = st.chat_input("Mensagem para a RENOVA IA...", key="global_ai_modal_input")
    if prompt:
        _execute_prompt(user_id, prompt)
        st.rerun(scope="fragment")


@st.dialog("RENOVA IA Financeira", width="large")
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
    """Exibe o botão flutuante e abre o mesmo chat da RENOVA IA em qualquer página autenticada."""
    target_user_id = str(user_id or _session_user_id() or "")
    if floating_ai_button():
        _open_global_dialog(target_user_id)
