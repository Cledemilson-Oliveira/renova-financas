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
from src.training_ingest import (
    chunk_training_text,
    compact_keywords,
    extract_pdf_text_from_url,
    extract_youtube_transcript,
)


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
          <h1>🧠 Treinamento <strong>Personalizado da RENOVA IA</strong></h1>
          <p>
            Ensine preferências, regras e contexto do seu jeito de organizar o dinheiro.
            Materiais externos são estudados exclusivamente por link — sem upload de arquivos.
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
    st.markdown("### Ensine regras e contexto")
    st.caption(
        "Use este formulário apenas para regras, preferências e contexto curto. "
        "Materiais externos, PDFs e vídeos devem ser adicionados por link."
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
            if not title.strip() or not content.strip():
                st.error("Informe um título e o conteúdo da regra ou preferência.")
                return
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
    st.caption("Estas regras entram imediatamente na memória operacional usada pelo chat financeiro.")

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
                        structured_rule={"rule_type": "category_alias", "trigger": trigger.strip(), "category": category},
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
                        structured_rule={"rule_type": "type_alias", "trigger": trigger.strip(), "kind": kind},
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


def _save_source_chunks(
    user_id: str,
    *,
    source_label: str,
    base_title: str,
    text: str,
    area: str,
    priority: int,
    keywords: list[str],
) -> int:
    chunks = chunk_training_text(text)
    if not chunks:
        raise ValueError("Não encontrei conteúdo para adicionar ao treinamento.")

    for index, chunk in enumerate(chunks, start=1):
        part = f" • parte {index}/{len(chunks)}" if len(chunks) > 1 else ""
        content = f"[Fonte: {source_label}]\n\n{chunk}"
        create_training_item(
            user_id,
            title=f"{base_title}{part}"[:120],
            area=area,
            kind="conhecimento",
            content=content,
            application_mode="quando_relevante",
            keywords=keywords,
            priority=priority,
            structured_rule={"rule_type": "knowledge", "text": content, "source": source_label},
        )
    return len(chunks)


def _import_sources(user_id: str) -> None:
    st.markdown("### Estudar materiais externos por link")
    st.caption(
        "Nenhum arquivo é enviado para o armazenamento do RENOVA. O sistema lê a fonte temporariamente, "
        "extrai o texto necessário e guarda somente o conhecimento processado."
    )
    st.info("🔗 Política de armazenamento: materiais de treinamento somente por link. Upload de arquivo é permitido apenas para foto de perfil.")

    pdf_tab, youtube_tab = st.tabs(["📄 PDF por link", "▶️ YouTube por link"])

    with pdf_tab:
        with st.form("training_pdf_link_form", clear_on_submit=True):
            url = st.text_input("Link público do PDF", placeholder="https://exemplo.com/manual.pdf")
            title = st.text_input("Nome do treinamento", placeholder="Ex.: Manual financeiro da empresa")
            c1, c2 = st.columns(2)
            with c1:
                area_label = st.selectbox("Área do conhecimento", list(AREAS.keys()), index=2, key="pdf_area")
            with c2:
                priority = st.slider("Prioridade", 0, 100, 65, 5, key="pdf_priority")
            keywords_raw = st.text_input("Palavras-chave", placeholder="empresa, processo, financeiro", key="pdf_keywords")
            submitted = st.form_submit_button("🔗 ESTUDAR PDF PELO LINK", use_container_width=True)

        if submitted:
            if not url.strip():
                st.error("Informe o link público do PDF.")
            else:
                try:
                    with st.spinner("Lendo o PDF pelo link e organizando o treinamento..."):
                        final_url, text = extract_pdf_text_from_url(url)
                        base_title = title.strip() or "PDF externo"
                        keywords = compact_keywords([*parse_keywords(keywords_raw), base_title, "PDF"])
                        count = _save_source_chunks(
                            user_id,
                            source_label=f"PDF • {final_url}",
                            base_title=base_title,
                            text=text,
                            area=AREAS[area_label],
                            priority=priority,
                            keywords=keywords,
                        )
                    st.success(f"PDF estudado pelo link e adicionado à memória em {count} bloco(s) de conhecimento.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Não consegui estudar esse PDF pelo link: {exc}")

    with youtube_tab:
        st.info(
            "A leitura usa as legendas/transcrição disponibilizadas pelo YouTube. "
            "Se o vídeo não tiver transcrição acessível, use outro conteúdo publicado por link."
        )
        with st.form("training_youtube_link_form", clear_on_submit=True):
            url = st.text_input("Link do YouTube", placeholder="https://www.youtube.com/watch?v=...")
            title = st.text_input("Nome do treinamento", placeholder="Ex.: Treinamento de vendas")
            c1, c2 = st.columns(2)
            with c1:
                area_label = st.selectbox("Área do conhecimento", list(AREAS.keys()), index=2, key="yt_area")
            with c2:
                priority = st.slider("Prioridade", 0, 100, 65, 5, key="yt_priority")
            keywords_raw = st.text_input("Palavras-chave", placeholder="vendas, atendimento, processo", key="yt_keywords")
            submitted = st.form_submit_button("▶️ ESTUDAR VÍDEO PELO LINK", use_container_width=True)

        if submitted:
            if not url.strip():
                st.error("Informe o link do YouTube.")
            else:
                try:
                    with st.spinner("Lendo a transcrição e organizando o treinamento..."):
                        video_id, text = extract_youtube_transcript(url)
                        base_title = title.strip() or f"YouTube: {video_id}"
                        source_url = f"https://youtu.be/{video_id}"
                        keywords = compact_keywords([*parse_keywords(keywords_raw), base_title, "YouTube", video_id])
                        count = _save_source_chunks(
                            user_id,
                            source_label=f"YouTube • {source_url}",
                            base_title=base_title,
                            text=text,
                            area=AREAS[area_label],
                            priority=priority,
                            keywords=keywords,
                        )
                    st.success(f"Vídeo estudado pelo link e adicionado à memória em {count} bloco(s) de conhecimento.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Não consegui obter a transcrição desse vídeo: {exc}")


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
            content = str(item.get("content") or "")
            st.write(content if len(content) <= 3000 else content[:3000] + "…")
            keywords = item.get("keywords") or []
            if keywords:
                st.caption("Palavras-chave: " + " • ".join(map(str, keywords)))
            st.caption(f"Status: {status} · Tipo: {item.get('kind')} · Aplicação: {item.get('application_mode')}")
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
    st.page_link("app.py", label="Voltar ao RENOVA Finanças", icon="🏠")

_hero()

if not is_configured():
    st.error("O Supabase ainda não está configurado neste ambiente.")
    st.stop()

if not is_authenticated():
    st.session_state.nav_page = "Assinar RENOVA IA"
    st.switch_page("app.py")

uid = _user_id()
if not _has_access(uid):
    st.session_state.nav_page = "Assinar RENOVA IA"
    st.switch_page("app.py")

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
st.warning(
    "📎 Arquivos não são armazenados para treinamento. Use links públicos para PDFs e vídeos. "
    "A única exceção de upload no RENOVA Finanças é a foto de perfil."
)

teach_tab, sources_tab, rules_tab, library_tab = st.tabs(
    ["🧠 Regras e contexto", "🔗 Conteúdos por link", "⚙️ Regras rápidas", "📚 Memória da IA"]
)

with teach_tab:
    _save_free_training(uid)
with sources_tab:
    _import_sources(uid)
with rules_tab:
    _save_quick_rule(uid)
with library_tab:
    _training_library(uid, training_items)
