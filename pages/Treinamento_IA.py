from __future__ import annotations

import streamlit as st

from src.access import is_owner
from src.ai_training import (
    APPLICATION_MODES,
    AREAS,
    KINDS,
    create_training_item,
    delete_training_item,
    list_training_items,
    parse_keywords,
    set_training_item_active,
)
from src.repository import fetch_financial_data, has_active_ai_subscription
from src.supabase_client import current_user, is_authenticated, is_configured
from src.theme import apply_renova_theme, brand_block


st.set_page_config(
    page_title="Treinamento da IA • RENOVA Finanças",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_renova_theme()


def _user_id() -> str:
    user = current_user()
    return str(user.id) if user and getattr(user, "id", None) else ""


def _has_access(user_id: str) -> bool:
    if not user_id:
        return False
    try:
        return bool(is_owner(user_id) or has_active_ai_subscription(user_id))
    except Exception:
        return False


def _hero() -> None:
    st.markdown(
        """
        <section class="renova-hero">
          <h1>🧠 Treinamento da <strong>RENOVA IA</strong></h1>
          <p>
            Ensine como você vive, trabalha e administra seu dinheiro. A IA transforma
            seus ensinamentos em memória operacional e regras personalizadas para a sua conta.
          </p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _status_cards(items: list[dict]) -> None:
    total = len(items)
    active = len([item for item in items if item.get("is_active")])
    rules = len([item for item in items if item.get("kind") in {"regra", "preferencia", "vocabulario"}])
    always = len([item for item in items if item.get("application_mode") == "sempre" and item.get("is_active")])
    cols = st.columns(4)
    cols[0].metric("Conhecimentos", total)
    cols[1].metric("Ativos", active)
    cols[2].metric("Regras operacionais", rules)
    cols[3].metric("Sempre considerar", always)


def _save_free_training(user_id: str) -> None:
    st.markdown("### Ensine do seu jeito")
    st.caption(
        "Você pode registrar contexto pessoal, informações do negócio, objetivos, preferências e regras. "
        "Exemplo: ‘Quando eu disser pensão, use a categoria Família’."
    )
    with st.form("training_free_form", clear_on_submit=True):
        c1, c2 = st.columns([1.35, 1])
        with c1:
            title = st.text_input("Título", placeholder="Ex.: Regra para pensão")
            content = st.text_area(
                "O que a IA deve aprender?",
                placeholder=(
                    "Ex.: Quando eu disser pensão, use a categoria Família.\n\n"
                    "Ou: Minha prioridade financeira é manter as despesas fixas pagas antes de qualquer gasto de lazer."
                ),
                height=180,
            )
        with c2:
            area_label = st.selectbox("Área", list(AREAS.keys()), index=3)
            kind_label = st.selectbox("Tipo de ensinamento", list(KINDS.keys()))
            mode_label = st.selectbox("Como aplicar", list(APPLICATION_MODES.keys()), index=1)
            priority = st.slider("Prioridade", 0, 100, 60, 5)
            keywords_raw = st.text_input("Palavras-chave", placeholder="pensão, família, despesa fixa")

        submitted = st.form_submit_button("🧠 ENSINAR À RENOVA IA", use_container_width=True)
        if submitted:
            try:
                create_training_item(
                    user_id,
                    title=title,
                    area=AREAS[area_label],
                    kind=KINDS[kind_label],
                    content=content,
                    application_mode=APPLICATION_MODES[mode_label],
                    keywords=parse_keywords(keywords_raw),
                    priority=priority,
                )
                st.success("Treinamento salvo. A RENOVA IA já pode reutilizar esse ensinamento.")
                st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível salvar o treinamento: {exc}")


def _save_quick_rule(user_id: str) -> None:
    st.markdown("### Regras rápidas de execução")
    st.caption(
        "Estas regras são estruturadas e entram imediatamente na memória operacional usada pelo chat financeiro."
    )

    try:
        bundle = fetch_financial_data(user_id)
        categories = bundle.get("categories")
        accounts = bundle.get("accounts")
    except Exception:
        categories = None
        accounts = None

    category_names = [] if categories is None or categories.empty else categories["name"].astype(str).tolist()
    account_names = [] if accounts is None or accounts.empty else accounts["conta"].astype(str).tolist()

    rule_type = st.radio(
        "Tipo de regra",
        ["Palavra → Categoria", "Palavra → Receita/Despesa", "Conta padrão"],
        horizontal=True,
    )

    if rule_type == "Palavra → Categoria":
        with st.form("quick_category_rule", clear_on_submit=True):
            trigger = st.text_input("Quando eu disser...", placeholder="Ex.: pensão")
            category = st.selectbox("Usar a categoria", category_names or ["Cadastre uma categoria primeiro"])
            submitted = st.form_submit_button("Salvar regra de categoria", use_container_width=True)
            if submitted:
                if not category_names:
                    st.error("Cadastre uma categoria antes de criar esta regra.")
                elif not trigger.strip():
                    st.error("Informe a palavra ou expressão de gatilho.")
                else:
                    content = f"Quando eu disser {trigger.strip()}, use a categoria {category}."
                    create_training_item(
                        user_id,
                        title=f"{trigger.strip()} → {category}",
                        area="regras",
                        kind="vocabulario",
                        content=content,
                        application_mode="sempre",
                        keywords=[trigger.strip(), category],
                        priority=90,
                        structured_rule={
                            "rule_type": "category_alias",
                            "trigger": trigger.strip(),
                            "category": category,
                        },
                    )
                    st.success("Regra criada e ativada no chat financeiro.")
                    st.rerun()

    elif rule_type == "Palavra → Receita/Despesa":
        with st.form("quick_type_rule", clear_on_submit=True):
            trigger = st.text_input("Quando eu disser...", placeholder="Ex.: comissão")
            kind = st.selectbox("Tratar como", ["receita", "despesa"])
            submitted = st.form_submit_button("Salvar regra de tipo", use_container_width=True)
            if submitted:
                if not trigger.strip():
                    st.error("Informe a palavra ou expressão de gatilho.")
                else:
                    content = f"Quando eu disser {trigger.strip()}, considere como {kind}."
                    create_training_item(
                        user_id,
                        title=f"{trigger.strip()} → {kind}",
                        area="regras",
                        kind="vocabulario",
                        content=content,
                        application_mode="sempre",
                        keywords=[trigger.strip(), kind],
                        priority=90,
                        structured_rule={
                            "rule_type": "type_alias",
                            "trigger": trigger.strip(),
                            "kind": kind,
                        },
                    )
                    st.success("Regra criada e ativada no chat financeiro.")
                    st.rerun()

    else:
        with st.form("quick_account_rule", clear_on_submit=True):
            account = st.selectbox("Conta padrão da IA", account_names or ["Cadastre uma conta primeiro"])
            submitted = st.form_submit_button("Definir conta padrão", use_container_width=True)
            if submitted:
                if not account_names:
                    st.error("Cadastre uma conta antes de definir a conta padrão.")
                else:
                    content = f"Use sempre a conta {account}."
                    create_training_item(
                        user_id,
                        title=f"Conta padrão: {account}",
                        area="preferencias",
                        kind="preferencia",
                        content=content,
                        application_mode="sempre",
                        keywords=[account, "conta padrão"],
                        priority=100,
                        structured_rule={"rule_type": "default_account", "account": account},
                    )
                    st.success("Conta padrão aprendida pela RENOVA IA.")
                    st.rerun()


def _training_library(user_id: str, items: list[dict]) -> None:
    st.markdown("### O que a IA aprendeu")
    if not items:
        st.info("Ainda não há treinamentos cadastrados.")
        return

    for item in items:
        status = "ATIVO" if item.get("is_active") else "PAUSADO"
        area = str(item.get("area") or "geral").upper()
        priority = int(item.get("priority") or 0)
        with st.expander(f"{'🟢' if item.get('is_active') else '⚪'} {item.get('title')} • {area} • prioridade {priority}"):
            st.write(item.get("content") or "")
            keywords = item.get("keywords") or []
            if keywords:
                st.caption("Palavras-chave: " + " • ".join(map(str, keywords)))
            st.caption(
                f"Status: {status} · Tipo: {item.get('kind')} · Aplicação: {item.get('application_mode')}"
            )
            c1, c2 = st.columns(2)
            with c1:
                action_label = "Pausar treinamento" if item.get("is_active") else "Reativar treinamento"
                if st.button(action_label, key=f"training_toggle_{item['id']}", use_container_width=True):
                    set_training_item_active(user_id, str(item["id"]), not bool(item.get("is_active")))
                    st.rerun()
            with c2:
                if st.button("Excluir treinamento", key=f"training_delete_{item['id']}", use_container_width=True):
                    delete_training_item(user_id, str(item["id"]))
                    st.rerun()


with st.sidebar:
    brand_block()
    st.page_link("app.py", label="← Voltar ao RENOVA Finanças", icon="🏠")

_hero()

if not is_configured():
    st.error("O Supabase ainda não está configurado neste ambiente.")
    st.stop()

if not is_authenticated():
    st.warning("Entre na sua conta para acessar o Treinamento da IA.")
    st.page_link("app.py", label="Ir para o login")
    st.stop()

uid = _user_id()
if not _has_access(uid):
    st.warning("🧠 O Treinamento da IA é exclusivo para assinantes RENOVA IA.")
    st.write(
        "No plano RENOVA IA, cada usuário possui uma memória de treinamento própria, isolada e protegida pelo Supabase."
    )
    st.page_link("app.py", label="Voltar e assinar RENOVA IA")
    st.stop()

try:
    training_items = list_training_items(uid)
except Exception as exc:
    st.error(f"Não foi possível carregar seus treinamentos agora: {exc}")
    st.stop()

_status_cards(training_items)
st.info(
    "🔐 Seus treinamentos ficam vinculados à sua conta. Regras de segurança, permissões e confirmações sensíveis "
    "continuam valendo mesmo quando você ensina novas preferências à IA."
)

teach_tab, rules_tab, library_tab = st.tabs(
    ["🧠 Ensinar conhecimento", "⚙️ Regras rápidas", "📚 Memória da IA"]
)

with teach_tab:
    _save_free_training(uid)
with rules_tab:
    _save_quick_rule(uid)
with library_tab:
    _training_library(uid, training_items)
