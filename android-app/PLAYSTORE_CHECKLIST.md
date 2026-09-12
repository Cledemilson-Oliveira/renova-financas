# Checklist Google Play — Minhas Finanças RENOVA

## 1. Aplicativo Android

- [x] Projeto Android criado.
- [x] Package name definido: `br.com.ecossistemarenova.minhasfinancas`.
- [x] `targetSdk 36` / Android 16.
- [x] HTTPS obrigatório.
- [x] Splash screen.
- [x] Tratamento offline.
- [x] Botão voltar Android.
- [x] Upload de arquivos.
- [x] CI de compilação Android.
- [ ] Ícone oficial final 512x512 e adaptive icon.
- [ ] Testes em aparelhos Android reais.
- [ ] Testar telas pequenas, médias e tablets.

## 2. Segurança e dados

- [ ] Política de Privacidade pública.
- [ ] Termos de Uso.
- [ ] Página para exclusão de conta/dados, quando aplicável.
- [ ] Inventário dos dados coletados por MF-RNV, Supabase, IA e pagamentos.
- [ ] Preencher formulário Segurança dos dados no Play Console.
- [ ] Revisar logs para não armazenar informações financeiras sensíveis desnecessariamente.
- [ ] Confirmar que nenhuma chave secreta está no APK/GitHub.

## 3. Assinatura RENOVA IA

A assinatura digital de R$ 9,90 não deve ser publicada sem adequação às regras do Google Play.

- [ ] Criar produto/assinatura no Play Console ou aderir ao fluxo alternativo permitido e aplicável ao Brasil.
- [ ] Criar entitlement único no Supabase para evitar divergência entre web e Android.
- [ ] Validar compra no servidor antes de liberar IA.
- [ ] Implementar restauração de compra/assinatura.
- [ ] Tratar cancelamento, expiração, reembolso e período de carência.

## 4. Conta Play Console

- [ ] Criar/validar conta Google Play Developer.
- [ ] Criar o app "Minhas Finanças RENOVA".
- [ ] Usar exatamente o application ID definido no projeto.
- [ ] Ativar Play App Signing.
- [ ] Gerar upload key e guardar fora do GitHub.

## 5. Ficha da loja

- [ ] Nome: Minhas Finanças RENOVA.
- [ ] Descrição curta.
- [ ] Descrição completa.
- [ ] Ícone 512x512.
- [ ] Feature graphic 1024x500.
- [ ] Screenshots de celular.
- [ ] E-mail e página de suporte.
- [ ] Categoria apropriada.
- [ ] Classificação indicativa.

## 6. Testes e publicação

- [ ] Teste interno.
- [ ] Teste fechado quando exigido pela conta.
- [ ] Corrigir ANRs, crashes e problemas do relatório pré-lançamento.
- [ ] Gerar Android App Bundle `.aab` de produção.
- [ ] Enviar para revisão.

## Regra de arquitetura

O Android é a camada de distribuição e experiência mobile. A regra financeira continua centralizada no MF-RNV/Supabase para evitar duas fontes de verdade.
