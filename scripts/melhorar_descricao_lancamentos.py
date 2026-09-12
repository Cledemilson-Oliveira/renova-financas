from pathlib import Path

path = Path('app.py')
text = path.read_text(encoding='utf-8')

old = '''    due_date = None
    status_db = "pago"
    if not is_income:
        situation = st.radio(
            "Situação da despesa",
            ["✅ Pago", "🕒 Pendente"],
            horizontal=True,
            key=f"quick_{kind_db}_status",
        )
'''

new = '''    description_label = "Descrição / origem da receita" if is_income else "Descrição / destino da despesa"
    description_placeholder = (
        "Ex.: Salário empresa X, comissão cliente Y..."
        if is_income
        else "Ex.: Mercado Central, aluguel, combustível..."
    )
    description = st.text_input(
        description_label,
        placeholder=description_placeholder,
        key=f"quick_{kind_db}_description",
        help="Identifique de onde veio a receita ou onde foi feita a despesa para facilitar consultas e relatórios.",
    )

    due_date = None
    status_db = "pago"
    if not is_income:
        situation = st.radio(
            "Situação da despesa",
            ["✅ Pago", "🕒 Pendente"],
            horizontal=True,
            key=f"quick_{kind_db}_status",
        )
'''

if old not in text:
    raise SystemExit('Bloco principal não encontrado; nenhuma alteração aplicada.')
text = text.replace(old, new, 1)

old_description = '''    description = st.text_input(
        "Descrição",
        placeholder="Descreva o lançamento",
        key=f"quick_{kind_db}_description",
    )

'''
if old_description not in text:
    raise SystemExit('Bloco antigo de descrição não encontrado.')
text = text.replace(old_description, '', 1)

text = text.replace('APP_BUILD = "2026.09.12.3"', 'APP_BUILD = "2026.09.12.4"', 1)
text = text.replace('APP_BUILD = "2026.09.12.2"', 'APP_BUILD = "2026.09.12.4"', 1)

path.write_text(text, encoding='utf-8')
print('Descrição de receita/despesa reposicionada e destacada com sucesso.')
