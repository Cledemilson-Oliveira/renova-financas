from __future__ import annotations

from html import escape

import streamlit as st

from src.mercado_pago_checkout import create_subscription_checkout
from src.repository import get_ai_plan, has_active_ai_subscription
from src.supabase_client import current_user, is_authenticated, is_configured
from src.theme import apply_renova_theme, brand_block


st.set_page_config(
    page_title="RENOVA IA Personal • Minhas Finanças",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_renova_theme()


with st.sidebar:
    brand_block()
    st.page_link("app.py", label="Voltar ao RENOVA Finanças", icon="🏠", use_container_width=True)

if not is_configured():
    st.error("O Supabase ainda não está configurado neste ambiente.")
    st.stop()

if not is_authenticated():
    st.session_state["nav_page"] = "Assinar RENOVA IA"
    st.switch_page("app.py")

user = current_user()
uid = str(user.id) if user and getattr(user, "id", None) else ""

try:
    if uid and has_active_ai_subscription(uid):
        st.success("✅ Sua RENOVA IA Personalizada já está ativa.")
        st.page_link("pages/Treinamento_IA.py", label="🧠 Ir para o treinamento da minha IA", use_container_width=True)
        st.page_link("app.py", label="🏠 Voltar ao painel", use_container_width=True)
        st.stop()
except Exception:
    pass

plan = get_ai_plan() or {}
price = float(plan.get("price") or 9.90)
price_label = f"{price:.2f}".replace(".", ",")

st.markdown(
    """
    <style>
    .renova-sales-wrap{max-width:1180px;margin:0 auto;padding:8px 4px 56px}
    .renova-sales-hero{
      position:relative;overflow:hidden;border-radius:30px;padding:54px 46px;
      border:1px solid rgba(0,174,239,.30);
      background:
        radial-gradient(circle at 88% 15%,rgba(0,174,239,.30),transparent 33%),
        radial-gradient(circle at 8% 90%,rgba(255,204,0,.20),transparent 30%),
        linear-gradient(135deg,rgba(3,18,30,.98),rgba(5,50,82,.96) 58%,rgba(1,22,36,.99));
      box-shadow:0 28px 70px rgba(0,0,0,.28);
    }
    .renova-sales-kicker{font-size:.78rem;font-weight:900;letter-spacing:.18em;color:#FFD45A;text-transform:uppercase}
    .renova-sales-hero h1{font-size:clamp(2.35rem,5vw,4.9rem);line-height:1.00;margin:.5rem 0 1rem;color:#F7FBFF;max-width:920px}
    .renova-sales-hero h1 strong{color:#FFD45A;text-shadow:0 0 28px rgba(255,212,90,.18)}
    .renova-sales-lead{font-size:clamp(1rem,2vw,1.28rem);line-height:1.65;color:#D7E8F2;max-width:830px}
    .renova-sales-hero-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}
    .renova-sales-anchor{display:inline-flex;align-items:center;justify-content:center;min-height:50px;padding:0 24px;border-radius:15px;text-decoration:none!important;font-weight:900}
    .renova-sales-anchor.primary{background:linear-gradient(120deg,#FFD54F,#F0AA00);color:#071521!important;box-shadow:0 10px 32px rgba(255,190,0,.26)}
    .renova-sales-anchor.secondary{border:1px solid rgba(164,222,255,.34);background:rgba(3,27,45,.68);color:#F7FBFF!important}
    .renova-trust{display:flex;gap:18px;flex-wrap:wrap;margin-top:24px;color:#AFCBDC;font-size:.90rem}
    .renova-section{padding:58px 0 6px}
    .renova-section .eyebrow{font-size:.76rem;font-weight:950;letter-spacing:.16em;color:#C69300;text-transform:uppercase;margin-bottom:7px}
    .renova-section h2{font-size:clamp(1.8rem,3.8vw,3rem);line-height:1.08;margin:.2rem 0 .8rem;color:var(--text-color,#102A3B)}
    .renova-section h2 strong{color:#B27B00}
    .renova-section-intro{font-size:1.05rem;line-height:1.65;max-width:840px;opacity:.82}
    .renova-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:26px}
    .renova-value-card{padding:23px;border-radius:22px;border:1px solid rgba(0,174,239,.20);background:linear-gradient(145deg,rgba(255,255,255,.86),rgba(234,247,255,.72));box-shadow:0 15px 34px rgba(6,31,48,.08)}
    .renova-value-card .ico{font-size:1.65rem;margin-bottom:8px}.renova-value-card h3{margin:.25rem 0 .45rem;font-size:1.08rem}.renova-value-card p{margin:0;line-height:1.55;opacity:.78}
    .renova-dark-panel{margin-top:28px;padding:30px;border-radius:26px;background:linear-gradient(135deg,#071925,#073B5E 62%,#082333);border:1px solid rgba(255,208,74,.32);box-shadow:0 24px 55px rgba(0,0,0,.24);color:#EEF8FF}
    .renova-dark-panel h3{font-size:1.55rem;margin:.1rem 0 1rem;color:#FFD45A}.renova-dark-panel p{line-height:1.65;color:#CFE2ED}
    .renova-command-list{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:18px}.renova-command{padding:14px 16px;border-radius:15px;background:rgba(255,255,255,.07);border:1px solid rgba(170,223,255,.14);font-weight:700}
    .renova-compare{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:26px}
    .renova-compare-card{padding:28px;border-radius:24px;border:1px solid rgba(0,174,239,.18);background:rgba(255,255,255,.78)}
    .renova-compare-card.featured{border:1px solid rgba(255,185,0,.58);box-shadow:0 18px 48px rgba(255,177,0,.13);background:linear-gradient(145deg,rgba(255,249,223,.96),rgba(237,248,255,.92))}
    .renova-compare-card h3{margin:.1rem 0 .6rem;font-size:1.35rem}.renova-compare-card ul{padding-left:0;list-style:none;line-height:1.95;margin:.9rem 0 0}
    .renova-price-box{scroll-margin-top:24px;margin-top:46px;padding:38px;border-radius:28px;border:1px solid rgba(255,188,0,.55);background:radial-gradient(circle at 80% 12%,rgba(0,174,239,.18),transparent 38%),linear-gradient(145deg,#061826,#0B3754 72%,#071B29);box-shadow:0 28px 72px rgba(0,0,0,.28);color:#F7FBFF;text-align:center}
    .renova-price-box .old{opacity:.66;font-size:.95rem}.renova-price-box .price{font-size:clamp(3rem,7vw,5.4rem);font-weight:950;line-height:1;color:#FFD34F;margin:10px 0}.renova-price-box .price small{font-size:1rem;color:#D9E9F3;font-weight:700}.renova-price-box p{max-width:720px;margin:0 auto 18px;line-height:1.6;color:#D5E7F0}
    .renova-guarantee{margin-top:16px;font-size:.88rem;color:#AFCAD8}
    .renova-faq{margin-top:28px;padding:22px;border-radius:20px;background:rgba(255,255,255,.62);border:1px solid rgba(0,174,239,.15)}
    @media(max-width:800px){
      .renova-sales-hero{padding:34px 22px;border-radius:22px}.renova-grid{grid-template-columns:1fr}.renova-compare{grid-template-columns:1fr}.renova-command-list{grid-template-columns:1fr}.renova-price-box{padding:28px 18px}.renova-section{padding-top:42px}
    }
    @media(prefers-color-scheme:dark){
      .renova-value-card,.renova-compare-card,.renova-faq{background:linear-gradient(145deg,rgba(7,31,47,.95),rgba(5,21,33,.96));color:#EDF8FF}
      .renova-compare-card.featured{background:linear-gradient(145deg,rgba(52,43,9,.78),rgba(6,34,52,.96))}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="renova-sales-wrap">
      <section class="renova-sales-hero">
        <div class="renova-sales-kicker">RENOVA IA PERSONAL • MENOS REPETIÇÃO, MAIS CONTROLE</div>
        <h1>Você cuida da sua vida.<br><strong>A IA cuida do trabalho repetitivo.</strong></h1>
        <p class="renova-sales-lead">
          Pare de perder tempo procurando telas, repetindo regras e reorganizando as mesmas informações.
          Com a RENOVA IA Personal, você ensina como prefere trabalhar uma vez e passa a conversar com
          sua gestão financeira de um jeito muito mais rápido e pessoal.
        </p>
        <div class="renova-sales-hero-actions">
          <a class="renova-sales-anchor primary" href="#oferta">VER O PREÇO</a>
          <a class="renova-sales-anchor secondary" href="#como-funciona">VER COMO A IA AJUDA</a>
        </div>
        <div class="renova-trust">
          <span>✓ Minhas Finanças continua gratuito</span>
          <span>✓ IA Padrão continua disponível</span>
          <span>✓ Premium adiciona memória e treinamento pessoal</span>
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
          <article class="renova-value-card"><div class="ico">🔁</div><h3>Rotinas recorrentes</h3><p>Crie recorrências e deixe o sistema preparar automaticamente lançamentos repetitivos conforme as regras cadastradas.</p></article>
          <article class="renova-value-card"><div class="ico">🎯</div><h3>Prioridades pessoais</h3><p>Ensine o que é mais importante para você e faça a IA considerar esse contexto nas análises e orientações.</p></article>
          <article class="renova-value-card"><div class="ico">📚</div><h3>Conhecimento privado</h3><p>Adicione regras e conteúdos por links de PDF ou YouTube para criar uma base de conhecimento vinculada à sua conta.</p></article>
          <article class="renova-value-card"><div class="ico">📊</div><h3>Decisões com contexto</h3><p>Combine seus dados financeiros com suas próprias regras para receber respostas mais úteis e coerentes com sua rotina.</p></article>
        </div>

        <div class="renova-dark-panel">
          <h3>Em vez de clicar em várias telas, você pode simplesmente pedir.</h3>
          <p>A RENOVA IA continua respeitando permissões e confirmações do sistema. A diferença é que suas preferências pessoais passam a acompanhar os próximos pedidos.</p>
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

      <section class="renova-price-box" id="oferta">
        <div class="renova-sales-kicker">OFERTA DE LANÇAMENTO</div>
        <h2>Transforme sua IA em um assistente financeiro pessoal.</h2>
        <div class="price">R$ {price_label}<small>/mês</small></div>
        <p>
          Cancele quando quiser. Seu financeiro gratuito continua funcionando; a assinatura controla somente
          os recursos premium de memória e treinamento personalizado da RENOVA IA.
        </p>
        <div class="renova-guarantee">🔐 Pagamento processado no ambiente seguro do Mercado Pago.</div>
      </section>

      <section class="renova-section">
        <div class="eyebrow">SEM PEGADINHA</div>
        <h2>Uma assinatura simples.<br><strong>Um objetivo claro: economizar seu tempo.</strong></h2>
        <div class="renova-faq"><strong>O Minhas Finanças deixa de ser gratuito?</strong><br>Não. A conta gratuita e a IA Padrão continuam disponíveis.</div>
        <div class="renova-faq"><strong>Quando o Premium é liberado?</strong><br>Após a confirmação do Mercado Pago recebida pelo sistema.</div>
        <div class="renova-faq"><strong>A IA faz qualquer coisa sozinha?</strong><br>Ela executa ações operacionais quando você pede e respeita as confirmações de segurança. Rotinas recorrentes cadastradas podem ser geradas automaticamente pelo sistema.</div>
      </section>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Pronto para economizar tempo?")
st.caption("Ao continuar, o checkout será criado para sua conta e você será direcionado ao Mercado Pago.")

if st.button(
    f"✨ ASSINAR RENOVA IA PERSONAL • R$ {price_label}/MÊS",
    type="primary",
    use_container_width=True,
):
    try:
        with st.spinner("Preparando seu checkout seguro..."):
            checkout = create_subscription_checkout("renova_ia")

        if checkout.get("already_active"):
            st.success("Sua assinatura já está ativa.")
            st.page_link("pages/Treinamento_IA.py", label="🧠 Ir para minha IA Personalizada", use_container_width=True)
        else:
            checkout_url = str(checkout.get("checkout_url") or "").strip()
            if not checkout_url:
                st.error("O Mercado Pago não devolveu o endereço do checkout.")
            else:
                safe_url = escape(checkout_url, quote=True)
                st.success("Checkout criado. Continue no Mercado Pago para concluir a assinatura.")
                st.markdown(
                    f'<a href="{safe_url}" target="_self" rel="noopener" '
                    'style="display:flex;align-items:center;justify-content:center;min-height:56px;'
                    'border-radius:16px;text-decoration:none;font-weight:950;font-size:1.02rem;'
                    'background:linear-gradient(120deg,#FFD54F,#F0AA00);color:#071521;'
                    'box-shadow:0 14px 36px rgba(255,190,0,.26);margin-top:10px;">'
                    'ABRIR CHECKOUT SEGURO NO MERCADO PAGO →</a>',
                    unsafe_allow_html=True,
                )
    except Exception as exc:
        st.error(str(exc))
        st.caption("Se ocorrer uma falha, nenhuma assinatura parcial é considerada concluída.")
