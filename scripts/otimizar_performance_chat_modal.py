from pathlib import Path


APP = Path("app.py")
text = APP.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f"Trecho não encontrado: {label}")
    text = text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Imports e build
# ---------------------------------------------------------------------------
replace_once(
    "from datetime import date\nfrom html import escape\n",
    "from datetime import date\nfrom html import escape\nimport time\n",
    "import time",
)
replace_once(
    "import streamlit as st\n",
    "import streamlit as st\nimport streamlit.components.v1 as components\n",
    "streamlit components",
)
replace_once(
    'APP_BUILD = "2026.09.12.5"',
    'APP_BUILD = "2026.09.12.6"',
    "build",
)


# ---------------------------------------------------------------------------
# Carregamento financeiro e acessos: cache por sessão + TTL curto.
# Evita 7 consultas financeiras + consultas de permissão em todo rerun.
# ---------------------------------------------------------------------------
start = text.index("def active_user_id() -> str:\n")
end = text.index("def account_options() -> dict[str, str]:\n")
replacement = '''def active_user_id() -> str:
    user = current_user()
    if not user:
        return ""
    return str(st.session_state.get("active_financial_user_id") or user.id)


_FINANCIAL_DATA_KEYS = ("transactions", "accounts", "cards", "budgets", "categories", "goals")
_FINANCIAL_DATA_TTL_SECONDS = 15.0
_ACCESS_CACHE_TTL_SECONDS = 45.0
_AI_ACCESS_CACHE_TTL_SECONDS = 20.0


def _cache_is_fresh(timestamp_key: str, ttl_seconds: float) -> bool:
    loaded_at = float(st.session_state.get(timestamp_key) or 0.0)
    return bool(loaded_at and (time.monotonic() - loaded_at) < ttl_seconds)


def _cached_is_owner(user_id: str) -> bool:
    if not user_id:
        return False
    if (
        st.session_state.get("_owner_cache_user_id") == user_id
        and _cache_is_fresh("_owner_cache_at", _ACCESS_CACHE_TTL_SECONDS)
    ):
        return bool(st.session_state.get("_owner_cache_value", False))
    value = bool(is_owner(user_id))
    st.session_state._owner_cache_user_id = user_id
    st.session_state._owner_cache_value = value
    st.session_state._owner_cache_at = time.monotonic()
    return value


def _cached_owner_users(user_id: str) -> list[dict]:
    if not user_id or not _cached_is_owner(user_id):
        return []
    if (
        st.session_state.get("_owner_users_cache_user_id") == user_id
        and _cache_is_fresh("_owner_users_cache_at", _ACCESS_CACHE_TTL_SECONDS)
    ):
        return list(st.session_state.get("_owner_users_cache_value") or [])
    value = list_user_access()
    st.session_state._owner_users_cache_user_id = user_id
    st.session_state._owner_users_cache_value = value
    st.session_state._owner_users_cache_at = time.monotonic()
    return value


def _cached_has_active_ai_subscription(user_id: str) -> bool:
    if not user_id:
        return False
    if (
        st.session_state.get("_ai_access_cache_user_id") == user_id
        and _cache_is_fresh("_ai_access_cache_at", _AI_ACCESS_CACHE_TTL_SECONDS)
    ):
        return bool(st.session_state.get("_ai_access_cache_value", False))
    value = bool(has_active_ai_subscription(user_id))
    st.session_state._ai_access_cache_user_id = user_id
    st.session_state._ai_access_cache_value = value
    st.session_state._ai_access_cache_at = time.monotonic()
    return value


def _store_financial_bundle(target_user_id: str, bundle: dict) -> None:
    for key, value in bundle.items():
        st.session_state[key] = value
    st.session_state._financial_data_user_id = target_user_id
    st.session_state._financial_data_loaded_at = time.monotonic()


def load_data(*, force: bool = False) -> None:
    if REAL_MODE:
        user = current_user()
        if not user:
            return
        session_user_id = str(user.id)
        target_user_id = active_user_id()
        if st.session_state.get("bootstrap_user_id") != session_user_id:
            bootstrap_user(user)
            st.session_state.bootstrap_user_id = session_user_id

        same_user = st.session_state.get("_financial_data_user_id") == target_user_id
        complete = all(key in st.session_state for key in _FINANCIAL_DATA_KEYS)
        fresh = _cache_is_fresh("_financial_data_loaded_at", _FINANCIAL_DATA_TTL_SECONDS)
        if force or not (same_user and complete and fresh):
            _store_financial_bundle(target_user_id, fetch_financial_data(target_user_id))
    else:
        if "transactions" not in st.session_state:
            st.session_state.transactions = demo_transactions()
        if "accounts" not in st.session_state:
            st.session_state.accounts = demo_accounts()
        if "cards" not in st.session_state:
            st.session_state.cards = demo_cards()
        if "budgets" not in st.session_state:
            st.session_state.budgets = demo_budgets()
        if "categories" not in st.session_state:
            st.session_state.categories = pd.DataFrame(
                [{"id": name, "name": name, "kind": "ambos", "is_active": True} for name in CATEGORIES]
            )


if REAL_MODE and not is_authenticated():
    render_auth()
    st.stop()

if REAL_MODE:
    session_user = current_user()
    session_user_id = str(session_user.id) if session_user else ""
    st.session_state.active_financial_user_id = session_user_id

    try:
        if session_user_id and _cached_is_owner(session_user_id):
            owner_users = _cached_owner_users(session_user_id)
            active_users = [row for row in owner_users if row.get("status") == "ativo"]
            owner_options = {
                f"{row.get('email', row.get('user_id'))} • {row.get('role', 'usuario')}": str(row.get("user_id"))
                for row in active_users
            }
            if owner_options:
                with st.sidebar:
                    st.caption("MODO DONO • ACESSO GLOBAL")
                    selected_owner_user = st.selectbox(
                        "Gerenciar dados de",
                        list(owner_options.keys()),
                        key="owner_global_target",
                    )
                st.session_state.active_financial_user_id = owner_options[selected_owner_user]
    except Exception:
        st.session_state.active_financial_user_id = session_user_id

try:
    load_data()
except Exception:
    st.error("Não foi possível carregar seus dados financeiros agora.")
    st.stop()


AI_FAB_CLICKED = floating_ai_button()


'''
text = text[:start] + replacement + text[end:]


# ---------------------------------------------------------------------------
# Modais de lançamento responsivos: mais espaço no desktop, tela cheia mobile,
# campos grandes e sem zoom involuntário no teclado do celular.
# ---------------------------------------------------------------------------
marker = "def _render_quick_transaction_dialog(kind_db: str) -> None:\n"
modal_helper = '''def _apply_transaction_dialog_ux() -> None:
    st.markdown(
        """
        <span class="renova-transaction-dialog-marker"></span>
        <style>
        div[role="dialog"]:has(.renova-transaction-dialog-marker){
          width:min(780px,calc(100vw - 36px))!important;
          max-width:780px!important;
          max-height:90dvh!important;
          border-radius:22px!important;
          overflow:hidden!important;
        }
        div[role="dialog"]:has(.renova-transaction-dialog-marker) > div{
          max-height:90dvh!important;
          overflow-y:auto!important;
          overscroll-behavior:contain!important;
          padding-bottom:18px!important;
        }
        div[role="dialog"]:has(.renova-transaction-dialog-marker) input,
        div[role="dialog"]:has(.renova-transaction-dialog-marker) textarea{
          font-size:16px!important;
        }
        div[role="dialog"]:has(.renova-transaction-dialog-marker) [data-baseweb="input"],
        div[role="dialog"]:has(.renova-transaction-dialog-marker) [data-baseweb="select"] > div{
          min-height:48px!important;
        }
        @media(max-width:768px){
          div[role="dialog"]:has(.renova-transaction-dialog-marker){
            inset:0!important;
            width:100vw!important;
            max-width:100vw!important;
            height:100dvh!important;
            max-height:100dvh!important;
            margin:0!important;
            border-radius:0!important;
            border:0!important;
          }
          div[role="dialog"]:has(.renova-transaction-dialog-marker) > div{
            height:100dvh!important;
            max-height:100dvh!important;
            padding-left:14px!important;
            padding-right:14px!important;
            padding-bottom:max(22px,env(safe-area-inset-bottom))!important;
          }
          div[role="dialog"]:has(.renova-transaction-dialog-marker) [data-testid="stHorizontalBlock"]{
            flex-wrap:wrap!important;
            gap:8px!important;
          }
          div[role="dialog"]:has(.renova-transaction-dialog-marker) [data-testid="column"]{
            flex:1 1 100%!important;
            width:100%!important;
            min-width:100%!important;
          }
          div[role="dialog"]:has(.renova-transaction-dialog-marker) button{
            min-height:48px!important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


'''
replace_once(marker, modal_helper + marker, "helper responsivo dos modais")
replace_once(
    'def _render_quick_transaction_dialog(kind_db: str) -> None:\n    is_income = kind_db == "receita"\n',
    'def _render_quick_transaction_dialog(kind_db: str) -> None:\n    _apply_transaction_dialog_ux()\n    is_income = kind_db == "receita"\n',
    "aplicar UX no modal rápido",
)
replace_once(
    'def open_edit_transaction_dialog(transaction_id: str) -> None:\n    tx = st.session_state.transactions\n',
    'def open_edit_transaction_dialog(transaction_id: str) -> None:\n    _apply_transaction_dialog_ux()\n    tx = st.session_state.transactions\n',
    "aplicar UX no modal de edição",
)


# ---------------------------------------------------------------------------
# Atualização imediata após gravações manuais para o cache nunca mostrar
# valores antigos depois de salvar.
# ---------------------------------------------------------------------------
replace_once(
    '                st.success(f"{kind_label} salva em {category_name}.")\n                st.rerun()\n',
    '                _refresh_active_financial_data(active_user_id())\n                st.success(f"{kind_label} salva em {category_name}.")\n                st.rerun()\n',
    "refresh lançamento rápido",
)
replace_once(
    '''def _refresh_categories() -> None:
    if not REAL_MODE:
        return
    refreshed = fetch_financial_data(active_user_id())
    st.session_state.categories = refreshed["categories"]
''',
    '''def _refresh_categories() -> None:
    if not REAL_MODE:
        return
    _refresh_active_financial_data(active_user_id())
''',
    "refresh de categorias",
)
replace_once(
    '                        create_account(active_user_id(), name, account_type, initial_balance)\n                        st.rerun()\n',
    '                        create_account(active_user_id(), name, account_type, initial_balance)\n                        _refresh_active_financial_data(active_user_id())\n                        st.rerun()\n',
    "refresh conta",
)
replace_once(
    '''                        create_card(
                            active_user_id(),
                            name,
                            limit_value,
                            int(closing_day),
                            int(due_day),
                            None if linked == "Sem vínculo" else accounts_map[linked],
                        )
                        st.rerun()
''',
    '''                        create_card(
                            active_user_id(),
                            name,
                            limit_value,
                            int(closing_day),
                            int(due_day),
                            None if linked == "Sem vínculo" else accounts_map[linked],
                        )
                        _refresh_active_financial_data(active_user_id())
                        st.rerun()
''',
    "refresh cartão",
)
replace_once(
    '''                            upsert_budget(
                                active_user_id(),
                                expense_categories[category_label],
                                date.today().replace(day=1),
                                planned,
                            )
                            st.rerun()
''',
    '''                            upsert_budget(
                                active_user_id(),
                                expense_categories[category_label],
                                date.today().replace(day=1),
                                planned,
                            )
                            _refresh_active_financial_data(active_user_id())
                            st.rerun()
''',
    "refresh orçamento",
)


# ---------------------------------------------------------------------------
# Cache de acesso à IA e refresh financeiro centralizado.
# ---------------------------------------------------------------------------
replace_once(
    '''def has_personalized_ai_training_access() -> bool:
    uid = session_user_id()
    if not uid:
        return False
    try:
        return bool(is_owner(uid) or has_active_ai_subscription(uid))
    except Exception:
        return False
''',
    '''def has_personalized_ai_training_access() -> bool:
    uid = session_user_id()
    if not uid:
        return False
    try:
        return bool(_cached_is_owner(uid) or _cached_has_active_ai_subscription(uid))
    except Exception:
        return False
''',
    "cache acesso IA",
)
replace_once(
    '''def _refresh_active_financial_data(user_id: str) -> None:
    refreshed = fetch_financial_data(user_id)
    for key, value in refreshed.items():
        st.session_state[key] = value
''',
    '''def _refresh_active_financial_data(user_id: str) -> None:
    _store_financial_bundle(user_id, fetch_financial_data(user_id))
''',
    "refresh financeiro centralizado",
)
replace_once(
    '''    if REAL_MODE and uid:
        try:
            owner = is_owner(uid)
            ai_active = owner or has_active_ai_subscription(uid)
        except Exception:
            pass
''',
    '''    if REAL_MODE and uid:
        try:
            owner = _cached_is_owner(uid)
            ai_active = owner or _cached_has_active_ai_subscription(uid)
        except Exception:
            pass
''',
    "cache sidebar",
)


# ---------------------------------------------------------------------------
# WhatsApp-like: histórico em ordem crescente, composer fixo já existente e
# autoscroll somente quando a quantidade de mensagens muda/ao abrir o chat.
# ---------------------------------------------------------------------------
scroll_helper = '''def _scroll_ai_chat_to_bottom(*, force: bool = False) -> None:
    messages_count = len(st.session_state.get("ai_messages") or [])
    last_count = int(st.session_state.get("_ai_last_autoscroll_count") or -1)
    should_scroll = force or bool(st.session_state.pop("_ai_force_scroll_bottom", False)) or messages_count != last_count
    if not should_scroll:
        return
    st.session_state._ai_last_autoscroll_count = messages_count
    components.html(
        """
        <script>
        (() => {
          const doc = window.parent.document;
          const moveToBottom = () => {
            const shell = doc.querySelector('.st-key-ai_chat_modal_shell');
            if (shell) shell.scrollTop = shell.scrollHeight;
            if (window.parent.matchMedia('(min-width: 769px)').matches) {
              const input = doc.querySelector('.st-key-ai_chat_composer textarea');
              if (input && doc.activeElement !== input) {
                try { input.focus({preventScroll:true}); } catch (_) {}
              }
            }
          };
          requestAnimationFrame(moveToBottom);
          setTimeout(moveToBottom, 70);
          setTimeout(moveToBottom, 220);
        })();
        </script>
        """,
        height=0,
        width=0,
    )


'''
replace_once(
    '@st.dialog("RENOVA IA", width="small")\ndef open_ai_dialog() -> None:\n',
    scroll_helper + '@st.dialog("RENOVA IA", width="small")\ndef open_ai_dialog() -> None:\n',
    "helper autoscroll",
)
replace_once(
    '          .st-key-ai_chat_composer{padding-bottom:max(10px,env(safe-area-inset-bottom))!important}\n',
    '          .st-key-ai_chat_composer{padding-bottom:max(10px,env(safe-area-inset-bottom))!important}\n          .st-key-ai_chat_composer [data-testid="stChatInput"] textarea{font-size:16px!important}\n',
    "input mobile 16px",
)
replace_once(
    '''    with st.container(key="ai_chat_composer"):
        render_ai_input("ai_modal_input", fragment_rerun=True)
        st.markdown('<div class="ai-disclaimer">A RENOVA IA pode cometer erros. Confira informações importantes.</div>', unsafe_allow_html=True)
''',
    '''    with st.container(key="ai_chat_composer"):
        render_ai_input("ai_modal_input", fragment_rerun=True)
        st.markdown('<div class="ai-disclaimer">A RENOVA IA pode cometer erros. Confira informações importantes.</div>', unsafe_allow_html=True)

    _scroll_ai_chat_to_bottom()
''',
    "autoscroll no modal",
)
replace_once(
    '''if AI_FAB_CLICKED:
    st.session_state.ai_chat_open = True
    st.session_state.ai_chat_minimized = False
''',
    '''if AI_FAB_CLICKED:
    st.session_state.ai_chat_open = True
    st.session_state.ai_chat_minimized = False
    st.session_state._ai_force_scroll_bottom = True
''',
    "forçar scroll ao abrir",
)

APP.write_text(text, encoding="utf-8")
print("Otimização de performance, modais e chat aplicada com sucesso.")
