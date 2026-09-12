from pathlib import Path

APP = Path("app.py")
text = APP.read_text(encoding="utf-8")

old = 'div[data-testid="stDialog"]{background:transparent!important;pointer-events:none!important}'
new = 'div[data-testid="stDialog"]{background:transparent!important;pointer-events:auto!important}'

if old not in text:
    raise SystemExit("CSS do modal esperado não foi encontrado; nenhuma alteração foi aplicada.")

text = text.replace(old, new, 1)

anchor = '.st-key-ai_chat_modal_shell [data-testid="stChatInput"] textarea{min-height:52px!important;max-height:132px!important;color:#F7FBFF!important}'
addition = anchor + '\n        .st-key-ai_chat_modal_shell [data-testid="stChatInput"],\n        .st-key-ai_chat_modal_shell [data-testid="stChatInput"] textarea,\n        .st-key-ai_chat_modal_shell [data-testid="stChatInput"] button{pointer-events:auto!important;position:relative!important;z-index:60!important}'
if anchor not in text:
    raise SystemExit("Âncora do campo de chat não encontrada.")
text = text.replace(anchor, addition, 1)

text = text.replace('APP_BUILD = "2026.09.12.1"', 'APP_BUILD = "2026.09.12.2"', 1)

APP.write_text(text, encoding="utf-8")
print("Correção de foco/clique do campo da RENOVA IA aplicada.")
