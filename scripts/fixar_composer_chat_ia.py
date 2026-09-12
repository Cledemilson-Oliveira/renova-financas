from pathlib import Path

path = Path('app.py')
text = path.read_text(encoding='utf-8')

old_sig = 'def render_ai_chat(input_key: str, *, fragment_rerun: bool = False, show_suggestions: bool = False) -> None:\n'
new_sig = 'def render_ai_chat(input_key: str, *, fragment_rerun: bool = False, show_suggestions: bool = False, render_input: bool = True) -> None:\n'
if old_sig not in text:
    raise SystemExit('assinatura render_ai_chat não encontrada')
text = text.replace(old_sig, new_sig, 1)

old_input = '''    prompt = st.chat_input("Digite sua mensagem…", key=input_key)\n    if prompt:\n        st.session_state.ai_last_prompt = prompt\n        st.session_state.pop("ai_last_error", None)\n        with st.spinner("RENOVA IA está digitando…"):\n            _execute_ai_prompt(prompt)\n        if fragment_rerun:\n            st.rerun(scope="fragment")\n        else:\n            st.rerun()\n'''
new_input = '''    if render_input:\n        render_ai_input(input_key, fragment_rerun=fragment_rerun)\n\n\ndef render_ai_input(input_key: str, *, fragment_rerun: bool = False) -> None:\n    prompt = st.chat_input("Digite sua mensagem…", key=input_key)\n    if prompt:\n        st.session_state.ai_last_prompt = prompt\n        st.session_state.pop("ai_last_error", None)\n        with st.spinner("RENOVA IA está digitando…"):\n            _execute_ai_prompt(prompt)\n        if fragment_rerun:\n            st.rerun(scope="fragment")\n        else:\n            st.rerun()\n'''
if old_input not in text:
    raise SystemExit('bloco de input não encontrado')
text = text.replace(old_input, new_input, 1)

text = text.replace('''        .st-key-ai_chat_modal_shell{\n          height:calc(min(720px,85vh) - 150px)!important;overflow-y:auto!important;overflow-x:hidden!important;\n          padding:12px 12px 98px!important;background:\n''','''        .st-key-ai_chat_modal_shell{\n          height:calc(min(720px,85vh) - 188px)!important;overflow-y:auto!important;overflow-x:hidden!important;\n          padding:12px 12px 18px!important;background:\n''',1)

old_css = '''        .st-key-ai_chat_modal_shell [data-testid="stChatInput"]{\n          position:sticky!important;bottom:0!important;z-index:30!important;margin-top:16px!important;\n          min-height:54px!important;border-radius:17px!important;border:1px solid rgba(25,217,255,.24)!important;\n          background:#102438!important;box-shadow:0 -14px 30px rgba(7,21,34,.90)!important;\n        }\n        .st-key-ai_chat_modal_shell [data-testid="stChatInput"] textarea{min-height:52px!important;max-height:132px!important;color:#F7FBFF!important}\n        .st-key-ai_chat_modal_shell [data-testid="stChatInput"],\n        .st-key-ai_chat_modal_shell [data-testid="stChatInput"] textarea,\n        .st-key-ai_chat_modal_shell [data-testid="stChatInput"] button{pointer-events:auto!important;position:relative!important;z-index:60!important}\n        .st-key-ai_chat_modal_shell [data-testid="stChatInput"] textarea::placeholder{color:#93AFC1!important;opacity:1!important}\n        .ai-disclaimer{text-align:center;color:#7F9AAD;font-size:.60rem;margin:-82px 18px 0;position:relative;z-index:35;pointer-events:none}\n'''
new_css = '''        .st-key-ai_chat_composer{\n          position:absolute!important;left:0!important;right:0!important;bottom:0!important;z-index:80!important;\n          padding:10px 12px 8px!important;border-top:1px solid rgba(255,255,255,.08)!important;\n          background:rgba(8,24,39,.985)!important;backdrop-filter:blur(18px)!important;\n          box-shadow:0 -16px 34px rgba(0,0,0,.38)!important;\n        }\n        .st-key-ai_chat_composer [data-testid="stChatInput"]{\n          position:relative!important;inset:auto!important;margin:0!important;min-height:54px!important;\n          border-radius:17px!important;border:1px solid rgba(25,217,255,.28)!important;\n          background:#102438!important;box-shadow:none!important;pointer-events:auto!important;\n        }\n        .st-key-ai_chat_composer [data-testid="stChatInput"] textarea{\n          min-height:52px!important;max-height:132px!important;color:#F7FBFF!important;pointer-events:auto!important;\n        }\n        .st-key-ai_chat_composer [data-testid="stChatInput"] button{pointer-events:auto!important}\n        .st-key-ai_chat_composer [data-testid="stChatInput"] textarea::placeholder{color:#93AFC1!important;opacity:1!important}\n        .ai-disclaimer{text-align:center;color:#7F9AAD;font-size:.60rem;margin:5px 8px 0;position:relative;z-index:82;pointer-events:none}\n'''
if old_css not in text:
    raise SystemExit('css antigo do chat input não encontrado')
text = text.replace(old_css, new_css, 1)

text = text.replace('''          .st-key-ai_chat_modal_shell{height:calc(100dvh - 140px)!important;padding:10px 9px 104px!important}\n''','''          .st-key-ai_chat_modal_shell{height:calc(100dvh - 188px)!important;padding:10px 9px 18px!important}\n          .st-key-ai_chat_composer{padding-bottom:max(10px,env(safe-area-inset-bottom))!important}\n''',1)

old_call = '''    with st.container(key="ai_chat_modal_shell"):\n        render_ai_chat(\n            "ai_modal_input",\n            fragment_rerun=True,\n            show_suggestions=bool(st.session_state.get("ai_show_suggestions", True)),\n        )\n    st.markdown('<div class="ai-disclaimer">A RENOVA IA pode cometer erros. Confira informações importantes.</div>', unsafe_allow_html=True)\n'''
new_call = '''    with st.container(key="ai_chat_modal_shell"):\n        render_ai_chat(\n            "ai_modal_input",\n            fragment_rerun=True,\n            show_suggestions=bool(st.session_state.get("ai_show_suggestions", True)),\n            render_input=False,\n        )\n\n    with st.container(key="ai_chat_composer"):\n        render_ai_input("ai_modal_input", fragment_rerun=True)\n        st.markdown('<div class="ai-disclaimer">A RENOVA IA pode cometer erros. Confira informações importantes.</div>', unsafe_allow_html=True)\n'''
if old_call not in text:
    raise SystemExit('chamada modal não encontrada')
text = text.replace(old_call, new_call, 1)

text = text.replace('APP_BUILD = "2026.09.12.2"', 'APP_BUILD = "2026.09.12.3"', 1)

path.write_text(text, encoding='utf-8')
print('Composer fixo aplicado com sucesso.')
