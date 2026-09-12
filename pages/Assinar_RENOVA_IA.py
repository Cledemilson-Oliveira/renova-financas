from __future__ import annotations

from textwrap import dedent

import streamlit as st

from src.repository import get_ai_plan, has_active_ai_subscription
from src.supabase_client import current_user, is_authenticated, is_configured
from src.theme import apply_renova_theme, brand_block
from src.theme_modes import current_theme_mode


st.set_page_config(
    page_title="RENOVA IA Personal • Minhas Finanças",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_renova_theme()


if is_authenticated():
    with st.sidebar:
        brand_block()
        st.page_link("app.py", label="Voltar ao RENOVA Finanças", icon="🏠", use_container_width=True)
else:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapseButton"]{display:none!important}
        </style>
        """,
        unsafe_allow_html=True,
    )

if not is_configured():
    st.error("O Supabase ainda não está configurado neste ambiente.")
    st.stop()

user = current_user() if is_authenticated() else None
uid = str(user.id) if user and getattr(user, "id", None) else ""

try:
    if uid and has_active_ai_subscription(uid):
        st.success("✅ Sua RENOVA IA Personalizada já está ativa.")
        st.page_link("pages/Treinamento_IA.py", label="🧠 Ir para o treinamento da minha IA", use_container_width=True)
        st.page_link("app.py", label="🏠 Voltar ao painel", use_container_width=True)
        st.stop()
except Exception:
    pass

try:
    plan = get_ai_plan() or {}
except Exception:
    # A oferta pública precisa carregar mesmo quando a política RLS não expõe a tabela ao visitante anônimo.
    plan = {}
price = float(plan.get("price") or 9.90)
price_label = f"{price:.2f}".replace(".", ",")
normal_price = 29.90
normal_price_label = f"{normal_price:.2f}".replace(".", ",")
promo_active = price < normal_price
theme_mode = current_theme_mode()
theme_class = f"theme-{theme_mode}" if theme_mode in {"light", "dark"} else "theme-system"

if promo_active:
    offer_badge = "OFERTA DE LANÇAMENTO • PRIMEIROS 100 ASSINANTES"
    offer_old_price = f'<div class="old">Preço normal: <s>R$ {normal_price_label}/mês</s></div>'
    offer_terms = (
        "Oferta válida para os primeiros 100 clientes que assinarem ou até o encerramento da campanha, "
        "o que ocorrer primeiro. O prazo promocional não tem data de término definida e pode ser encerrado "
        "a qualquer momento. Quem assinar por este valor e mantiver a assinatura ativa preserva R$ "
        f"{price_label}/mês. Em caso de cancelamento e nova assinatura futura, valerá o preço vigente."
    )
else:
    offer_badge = "RENOVA IA PERSONAL"
    offer_old_price = ""
    offer_terms = "Assinatura mensal no preço vigente. Cancele quando quiser."

st.markdown(
    dedent(
        """
        <style>
        .renova-sales-wrap{max-width:1180px;margin:0 auto;padding:8px 4px 56px}
        .renova-sales-hero{
          position:relative;overflow:hidden;border-radius:30px;padding:58px 48px;
          border:1px solid rgba(0,127,184,.18);
          background:
            radial-gradient(circle at 88% 12%,rgba(0,174,239,.18),transparent 34%),
            radial-gradient(circle at 8% 100%,rgba(255,215,90,.22),transparent 32%),
            linear-gradient(135deg,#FFFFFF 0%,#EAF6FB 56%,#F8FBFD 100%);
          box-shadow:0 24px 62px rgba(31,67,86,.13);
        }
        .renova-sales-kicker{font-size:.78rem;font-weight:900;letter-spacing:.18em;color:#9A7000;text-transform:uppercase}
        .renova-sales-hero h1{font-size:clamp(2.35rem,5vw,4.9rem);line-height:1.00;margin:.5rem 0 1rem;color:#102D3E;max-width:920px}
        .renova-sales-hero h1 strong{color:#A97800;text-shadow:none}
        .renova-sales-lead{font-size:clamp(1rem,2vw,1.28rem);line-height:1.68;color:#526F80;max-width:850px}
        .renova-trust{display:flex;gap:18px;flex-wrap:wrap;margin-top:26px;color:#557283;font-size:.90rem}
        .renova-trust span{padding:8px 12px;border-radius:999px;background:rgba(255,255,255,.72);border:1px solid rgba(0,127,184,.11)}
        .renova-section{padding:58px 0 6px}
        .renova-section .eyebrow{font-size:.76rem;font-weight:950;letter-spacing:.16em;color:#A97800;text-transform:uppercase;margin-bottom:7px}
        .renova-section h2{font-size:clamp(1.8rem,3.8vw,3rem);line-height:1.08;margin:.2rem 0 .8rem;color:#102D3E}
        .renova-section h2 strong{color:#A97800}
        .renova-section-intro{font-size:1.05rem;line-height:1.65;max-width:850px;color:#5B7484}
        .renova-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:26px}
        .renova-value-card{
          padding:23px;border-radius:22px;border:1px solid rgba(0,127,184,.16);
          background:linear-gradient(145deg,#FFFFFF,#EDF7FB);
          box-shadow:0 14px 32px rgba(31,67,86,.09);
        }
        .renova-value-card .ico{font-size:1.65rem;margin-bottom:8px}
        .renova-value-card h3{margin:.25rem 0 .45rem;font-size:1.08rem;color:#17364A}
        .renova-value-card p{margin:0;line-height:1.55;color:#607989}
        .renova-action-panel{
          margin-top:28px;padding:30px;border-radius:26px;
          background:
            radial-gradient(circle at 90% 5%,rgba(0,174,239,.15),transparent 34%),
            linear-gradient(135deg,#F8FCFE,#E6F4FA 58%,#F7FBFD);
          border:1px solid rgba(0,127,184,.20);
          box-shadow:0 20px 46px rgba(31,67,86,.11);
        }
        .renova-action-panel h3{font-size:1.55rem;margin:.1rem 0 1rem;color:#17364A}
        .renova-action-panel p{line-height:1.65;color:#577181}
        .renova-command-list{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:18px}
        .renova-command{
          padding:14px 16px;border-radius:15px;background:rgba(255,255,255,.82);
          border:1px solid rgba(0,127,184,.14);font-weight:700;color:#23485C;
          box-shadow:0 8px 18px rgba(31,67,86,.06);
        }
        .renova-compare{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:26px}
        .renova-compare-card{
          padding:28px;border-radius:24px;border:1px solid rgba(0,127,184,.16);
          background:linear-gradient(145deg,#FFFFFF,#F3F9FC);box-shadow:0 12px 28px rgba(31,67,86,.07);
        }
        .renova-compare-card.featured{
          border:1px solid rgba(184,132,0,.38);
          box-shadow:0 18px 48px rgba(184,132,0,.11);
          background:linear-gradient(145deg,#FFF9E5,#EBF7FC);
        }
        .renova-compare-card h3{margin:.1rem 0 .6rem;font-size:1.35rem;color:#17364A}
        .renova-compare-card ul{padding-left:0;list-style:none;line-height:1.95;margin:.9rem 0 0;color:#516D7D}
        .renova-price-box{
          scroll-margin-top:24px;margin-top:46px;padding:42px;border-radius:30px;
          border:1px solid rgba(184,132,0,.36);
          background:
            radial-gradient(circle at 84% 10%,rgba(0,174,239,.18),transparent 37%),
            radial-gradient(circle at 10% 100%,rgba(255,215,90,.24),transparent 35%),
            linear-gradient(145deg,#FFFFFF,#EAF6FB 68%,#FFF9E7);
          box-shadow:0 26px 64px rgba(31,67,86,.14);text-align:center;
        }
        .renova-price-box h2{color:#102D3E;margin:.35rem auto .8rem;max-width:780px}
        .renova-price-box .old{color:#738997;font-size:1rem}
        .renova-price-box .price{font-size:clamp(3rem,7vw,5.4rem);font-weight:950;line-height:1;color:#A97800;margin:12px 0}
        .renova-price-box .price small{font-size:1rem;color:#607989;font-weight:700}
        .renova-price-box p{max-width:760px;margin:0 auto 18px;line-height:1.65;color:#526F80}
        .renova-offer-note{
          max-width:830px;margin:20px auto 0;padding:16px 18px;border-radius:17px;
          border:1px solid rgba(184,132,0,.22);background:rgba(255,248,218,.72);
          color:#725500;line-height:1.6;font-size:.94rem
        }
        .renova-guarantee{margin-top:16px;font-size:.88rem;color:#607989}
        .renova-faq{margin-top:14px;padding:22px;border-radius:20px;background:linear-gradient(145deg,#FFFFFF,#F2F8FB);border:1px solid rgba(0,127,184,.13);color:#536E7D}
        .renova-faq strong{color:#17364A}
        .renova-final-copy{text-align:center;margin:44px auto 14px;max-width:820px}
        .renova-final-copy h3{font-size:clamp(1.55rem,3vw,2.3rem);margin:.2rem 0 .5rem;color:#102D3E}
        .renova-final-copy p{color:#5B7484;line-height:1.6}

        .theme-dark .renova-sales-hero,
        .theme-dark .renova-action-panel,
        .theme-dark .renova-price-box{
          border-color:rgba(255,208,74,.30);
          background:
            radial-gradient(circle at 88% 12%,rgba(0,174,239,.25),transparent 34%),
            radial-gradient(circle at 8% 100%,rgba(255,204,0,.14),transparent 32%),
            linear-gradient(135deg,#061725,#0A3551 60%,#071B29);
          box-shadow:0 25px 64px rgba(0,0,0,.30);
        }
        .theme-dark .renova-sales-hero h1,
        .theme-dark .renova-section h2,
        .theme-dark .renova-action-panel h3,
        .theme-dark .renova-price-box h2,
        .theme-dark .renova-final-copy h3{color:#F4FAFE}
        .theme-dark .renova-sales-hero h1 strong,
        .theme-dark .renova-section h2 strong,
        .theme-dark .renova-sales-kicker,
        .theme-dark .renova-section .eyebrow,
        .theme-dark .renova-price-box .price{color:#FFD45A}
        .theme-dark .renova-sales-lead,
        .theme-dark .renova-trust,
        .theme-dark .renova-section-intro,
        .theme-dark .renova-action-panel p,
        .theme-dark .renova-price-box p,
        .theme-dark .renova-price-box .old,
        .theme-dark .renova-guarantee,
        .theme-dark .renova-final-copy p{color:#C9DDE8}
        .theme-dark .renova-trust span{background:rgba(255,255,255,.06);border-color:rgba(170,223,255,.13)}
        .theme-dark .renova-value-card,
        .theme-dark .renova-compare-card,
        .theme-dark .renova-faq{
          background:linear-gradient(145deg,rgba(7,31,47,.97),rgba(5,21,33,.98));
          color:#EDF8FF;border-color:rgba(0,174,239,.18)
        }
        .theme-dark .renova-compare-card.featured{
          background:linear-gradient(145deg,rgba(52,43,9,.75),rgba(6,34,52,.97));
          border-color:rgba(255,208,74,.34)
        }
        .theme-dark .renova-value-card h3,
        .theme-dark .renova-compare-card h3,
        .theme-dark .renova-faq strong{color:#F4FAFE}
        .theme-dark .renova-value-card p,
        .theme-dark .renova-compare-card ul,
        .theme-dark .renova-faq{color:#C9DDE8}
        .theme-dark .renova-command{
          background:rgba(255,255,255,.065);border-color:rgba(170,223,255,.14);color:#F2F8FC;box-shadow:none
        }
        .theme-dark .renova-offer-note{
          background:rgba(255,213,79,.10);border-color:rgba(255,213,79,.28);color:#FFE59A
        }

        @media(prefers-color-scheme:dark){
          .theme-system .renova-sales-hero,
          .theme-system .renova-action-panel,
          .theme-system .renova-price-box{
            border-color:rgba(255,208,74,.30);
            background:
              radial-gradient(circle at 88% 12%,rgba(0,174,239,.25),transparent 34%),
              radial-gradient(circle at 8% 100%,rgba(255,204,0,.14),transparent 32%),
              linear-gradient(135deg,#061725,#0A3551 60%,#071B29);
            box-shadow:0 25px 64px rgba(0,0,0,.30);
          }
          .theme-system .renova-sales-hero h1,
          .theme-system .renova-section h2,
          .theme-system .renova-action-panel h3,
          .theme-system .renova-price-box h2,
          .theme-system .renova-final-copy h3{color:#F4FAFE}
          .theme-system .renova-sales-hero h1 strong,
          .theme-system .renova-section h2 strong,
          .theme-system .renova-sales-kicker,
          .theme-system .renova-section .eyebrow,
          .theme-system .renova-price-box .price{color:#FFD45A}
          .theme-system .renova-sales-lead,
          .theme-system .renova-trust,
          .theme-system .renova-section-intro,
          .theme-system .renova-action-panel p,
          .theme-system .renova-price-box p,
          .theme-system .renova-price-box .old,
          .theme-system .renova-guarantee,
          .theme-system .renova-final-copy p{color:#C9DDE8}
          .theme-system .renova-trust span{background:rgba(255,255,255,.06);border-color:rgba(170,223,255,.13)}
          .theme-system .renova-value-card,
          .theme-system .renova-compare-card,
          .theme-system .renova-faq{background:linear-gradient(145deg,rgba(7,31,47,.97),rgba(5,21,33,.98));color:#EDF8FF;border-color:rgba(0,174,239,.18)}
          .theme-system .renova-compare-card.featured{background:linear-gradient(145deg,rgba(52,43,9,.75),rgba(6,34,52,.97));border-color:rgba(255,208,74,.34)}
          .theme-system .renova-value-card h3,
          .theme-system .renova-compare-card h3,
          .theme-system .renova-faq strong{color:#F4FAFE}
          .theme-system .renova-value-card p,
          .theme-system .renova-compare-card ul,
          .theme-system .renova-faq{color:#C9DDE8}
          .theme-system .renova-command{background:rgba(255,255,255,.065);border-color:rgba(170,223,255,.14);color:#F2F8FC;box-shadow:none}
          .theme-system .renova-offer-note{background:rgba(255,213,79,.10);border-color:rgba(255,213,79,.28);color:#FFE59A}
        }

        @media(max-width:800px){
          .renova-sales-hero{padding:36px 22px;border-radius:22px}
          .renova-grid{grid-template-columns:1fr}
          .renova-compare{grid-template-columns:1fr}
          .renova-command-list{grid-template-columns:1fr}
          .renova-price-box{padding:30px 18px}
          .renova-section{padding-top:42px}
        }
        </style>
        """
    ),
    unsafe_allow_html=True,
)

sales_html = f"""
<div class="renova-sales-wrap {theme_class}">
  <section class="renova-sales-hero">
    <div class="renova-sales-kicker">RENOVA IA PERSONAL • MENOS REPETIÇÃO, MAIS CONTROLE</div>
    <h1>Você cuida da sua vida.<br><strong>A IA cuida do trabalho repetitivo.</strong></h1>
    <p class="renova-sales-lead">
      Pare de perder tempo procurando telas, repetindo regras e reorganizando as mesmas informações.
      Com a RENOVA IA Personal, você ensina como prefere trabalhar uma vez e passa a conversar com
      sua gestão financeira de um jeito muito mais rápido e pessoal.
    </p>
    <div class="renova-trust">
      <span>✓ Minhas Finanças continua gratuito</span>
      <span>✓ IA Padrão continua disponível</span>
      <span>✓ Personal adiciona memória e treinamento próprio</span>
    </div>
  </section>

  <section class="renova-section" id="como-funciona">
    <div class="eyebrow">GANHE TEMPO TODOS OS DIAS</div>
    <h2>Quanto menos você repete,<br><strong>mais a IA trabalha do seu jeito.</strong></h2>
    <p class="renova-section-intro">
      A versão Personal foi pensada para diminuir microtarefas financeiras: lembrar preferências,
      interpretar seu vocabulário, reutilizar regras e transformar pedidos simples em ações no sistema.
    </p>

    <div class="renova-grid">
      <article class="renova-value-card"><div class="ico">🧠</div><h3>Memória das suas regras</h3><p>Ensine categorias, prioridades, nomes e preferências para não precisar explicar tudo novamente.</p></article>
      <article class="renova-value-card"><div class="ico">⚡</div><h3>Comandos em linguagem natural</h3><p>Peça lançamentos, consultas e organização financeira sem procurar cada função manualmente.</p></article>
      <article class="renova-value-card"><div class="ico">🔁</div><h3>Rotinas recorrentes</h3><p>Crie recorrências e deixe o sistema preparar lançamentos repetitivos conforme as regras cadastradas.</p></article>
      <article class="renova-value-card"><div class="ico">🎯</div><h3>Prioridades pessoais</h3><p>Ensine o que é mais importante para você e faça a IA considerar esse contexto nas análises e orientações.</p></article>
      <article class="renova-value-card"><div class="ico">📚</div><h3>Conhecimento privado</h3><p>Adicione regras e conteúdos por links de PDF ou YouTube para criar uma base vinculada à sua conta.</p></article>
      <article class="renova-value-card"><div class="ico">📊</div><h3>Decisões com contexto</h3><p>Combine seus dados financeiros com suas próprias regras para receber respostas mais úteis e coerentes com sua rotina.</p></article>
    </div>

    <div class="renova-action-panel">
      <h3>Em vez de clicar em várias telas, você pode simplesmente pedir.</h3>
      <p>
        A RENOVA IA continua respeitando permissões e confirmações do sistema.
        A diferença é que suas preferências pessoais acompanham os próximos pedidos.
      </p>
      <div class="renova-command-list">
        <div class="renova-command">“Registre R$ 180 de energia com vencimento dia 15.”</div>
        <div class="renova-command">“Quando eu disser pensão, use a categoria Família.”</div>
        <div class="renova-command">“Crie essa despesa como recorrente todos os meses.”</div>
        <div class="renova-command">“Como fica meu caixa nos próximos meses?”</div>
        <div class="renova-command">“Marque a conta de internet como paga.”</div>
        <div class="renova-command">“Quais são minhas urgências financeiras agora?”</div>
      </div>
    </div>
  </section>

  <section class="renova-section">
    <div class="eyebrow">GRÁTIS X PERSONAL</div>
    <h2>Você não paga para usar o financeiro.<br><strong>Paga para deixar a IA com o seu jeito.</strong></h2>
    <div class="renova-compare">
      <article class="renova-compare-card">
        <h3>🤖 IA Padrão • Gratuita</h3>
        <ul>
          <li>✓ Lançamentos e consultas financeiras</li>
          <li>✓ Análises e urgências</li>
          <li>✓ Contas, cartões e orçamentos</li>
          <li>✓ Execução das funções essenciais</li>
          <li>— Sem memória personalizada avançada</li>
        </ul>
      </article>
      <article class="renova-compare-card featured">
        <h3>🧠 RENOVA IA Personal</h3>
        <ul>
          <li>✓ Tudo que já existe no gratuito</li>
          <li>✓ Regras e preferências permanentes</li>
          <li>✓ Vocabulário e contexto próprio</li>
          <li>✓ Treinamento privado da sua conta</li>
          <li>✓ Conteúdos por PDF/YouTube via link</li>
          <li>✓ Menos repetição nos próximos comandos</li>
        </ul>
      </article>
    </div>
  </section>

  <section class="renova-section">
    <div class="eyebrow">O QUE VOCÊ REALMENTE COMPRA</div>
    <h2>Não é só mais uma função.<br><strong>É menos trabalho manual todos os dias.</strong></h2>
    <div class="renova-grid">
      <article class="renova-value-card"><div class="ico">⏱️</div><h3>Menos tempo operacional</h3><p>Reduza cliques, repetições e buscas por telas para tarefas financeiras comuns.</p></article>
      <article class="renova-value-card"><div class="ico">🧩</div><h3>Seu jeito de organizar</h3><p>Treine regras, categorias e vocabulário para o sistema se adaptar à sua rotina.</p></article>
      <article class="renova-value-card"><div class="ico">🔎</div><h3>Mais clareza para decidir</h3><p>Use seus dados e suas próprias prioridades para fazer perguntas com contexto.</p></article>
    </div>
  </section>

  <section class="renova-price-box" id="oferta">
    <div class="renova-sales-kicker">{offer_badge}</div>
    <h2>Transforme sua IA em um assistente financeiro pessoal.</h2>
    {offer_old_price}
    <div class="price">R$ {price_label}<small>/mês</small></div>
    <p>
      Seu financeiro gratuito continua funcionando. A assinatura libera memória, regras,
      treinamento privado e contexto personalizado da RENOVA IA.
    </p>
    <div class="renova-offer-note">{offer_terms}</div>
    <div class="renova-guarantee">🔐 Pagamento processado no ambiente seguro do Mercado Pago.</div>
  </section>

  <section class="renova-section">
    <div class="eyebrow">SEM PEGADINHA</div>
    <h2>Uma assinatura simples.<br><strong>Um objetivo claro: economizar seu tempo.</strong></h2>
    <div class="renova-faq"><strong>O Minhas Finanças deixa de ser gratuito?</strong><br>Não. A conta gratuita e a IA Padrão continuam disponíveis.</div>
    <div class="renova-faq"><strong>Quando a RENOVA IA Personal é liberada?</strong><br>Após a confirmação da assinatura recebida pelo sistema via Mercado Pago.</div>
    <div class="renova-faq"><strong>O valor promocional aumenta para quem já assinou?</strong><br>Não enquanto a assinatura promocional permanecer ativa. Se ela for cancelada e contratada novamente no futuro, será aplicado o preço vigente naquele momento.</div>
    <div class="renova-faq"><strong>A IA faz qualquer coisa sozinha?</strong><br>Ela executa ações operacionais quando você pede e respeita as confirmações de segurança. Rotinas recorrentes cadastradas podem ser geradas automaticamente pelo sistema.</div>
  </section>

  <div class="renova-final-copy">
    <div class="renova-sales-kicker">AGORA SIM: A OFERTA</div>
    <h3>Se fizer sentido para sua rotina, ative sua RENOVA IA Personal.</h3>
    <p>Você já viu o que muda na prática. O próximo passo só acontece quando você decidir assinar.</p>
  </div>
</div>
"""
st.markdown(dedent(sales_html), unsafe_allow_html=True)

st.caption("🔐 O próximo passo abre o checkout. Seus dados de acesso e pagamento são informados somente na etapa de contratação.")

if st.button(
    f"💳 IR PARA O CHECKOUT SEGURO • R$ {price_label}/MÊS",
    type="primary",
    use_container_width=True,
):
    st.switch_page("pages/Checkout_Assinatura.py")
