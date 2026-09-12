from pathlib import Path

path = Path('app.py')
text = path.read_text(encoding='utf-8')

old = '''        .st-key-ai_chat_modal_shell{\n          height:calc(min(720px,85vh) - 188px)!important;overflow-y:auto!important;overflow-x:hidden!important;\n          padding:12px 12px 18px!important;background:\n            radial-gradient(circle at 18% 8%,rgba(24,223,165,.035),transparent 30%),\n            linear-gradient(180deg,#0A1A2A,#071522)!important;\n          scrollbar-width:thin;scrollbar-color:rgba(25,217,255,.28) transparent;\n        }\n'''

new = '''        .st-key-ai_chat_modal_shell{\n          height:calc(min(720px,85vh) - 188px)!important;\n          min-height:0!important;\n          overflow-y:scroll!important;\n          overflow-x:hidden!important;\n          overscroll-behavior-y:contain!important;\n          scrollbar-gutter:stable!important;\n          touch-action:pan-y!important;\n          -webkit-overflow-scrolling:touch!important;\n          padding:12px 12px 18px!important;background:\n            radial-gradient(circle at 18% 8%,rgba(24,223,165,.035),transparent 30%),\n            linear-gradient(180deg,#0A1A2A,#071522)!important;\n          scrollbar-width:thin;scrollbar-color:rgba(25,217,255,.38) transparent;\n        }\n        .st-key-ai_chat_modal_shell::-webkit-scrollbar{width:8px!important}\n        .st-key-ai_chat_modal_shell::-webkit-scrollbar-track{background:transparent!important}\n        .st-key-ai_chat_modal_shell::-webkit-scrollbar-thumb{\n          background:rgba(25,217,255,.30)!important;border-radius:999px!important;\n          border:2px solid transparent!important;background-clip:padding-box!important;\n        }\n        .st-key-ai_chat_modal_shell::-webkit-scrollbar-thumb:hover{background:rgba(25,217,255,.48)!important;background-clip:padding-box!important}\n'''

if old not in text:
    raise SystemExit('Trecho alvo do chat não encontrado; nenhuma alteração aplicada.')

text = text.replace(old, new, 1)
text = text.replace('APP_BUILD = "2026.09.12.4"', 'APP_BUILD = "2026.09.12.5"', 1) if 'APP_BUILD = "2026.09.12.4"' in text else text
path.write_text(text, encoding='utf-8')
print('Rolagem interna do chat RENOVA IA reforçada com sucesso.')
