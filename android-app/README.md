# Minhas Finanças RENOVA — Android

Base Android nativa para distribuição do MF-RNV na Google Play.

## Identidade

- App: **Minhas Finanças RENOVA**
- Application ID: `br.com.ecossistemarenova.minhasfinancas`
- URL principal: `https://minhas-financas-renova.streamlit.app/`
- `compileSdk`: 36
- `targetSdk`: 36
- `minSdk`: 26
- Java/JDK: 17

## Arquitetura

O aplicativo Android funciona como uma camada mobile nativa segura sobre o MF-RNV online. A lógica financeira, autenticação e dados continuam no Streamlit/Supabase; o Android cuida da experiência de instalação, splash, navegação, conectividade, upload e integração futura com serviços nativos.

### Recursos já preparados

- Splash screen RENOVA.
- WebView restrita ao domínio oficial do MF-RNV.
- HTTPS obrigatório; cleartext HTTP desativado.
- Links externos abertos fora do app.
- Upload de arquivos pelo seletor Android.
- Pull-to-refresh.
- Tratamento nativo do botão voltar.
- Tela offline com tentativa de reconexão.
- Deep link do domínio `minhas-financas-renova.streamlit.app`.
- Build de release com minificação e remoção de recursos não usados.

## Abrir no Android Studio

Abra a pasta `android-app` como projeto Android. Use JDK 17 e instale o Android SDK 36.

A configuração usa Android Gradle Plugin 8.11.1, compatível com API 36. Antes de gerar um bundle de produção, gere/atualize o Gradle Wrapper pelo Android Studio para Gradle 8.13.

## Release Play Store

Antes da publicação pública ainda precisamos:

1. Substituir o ícone temporário pelo ícone oficial final do Minhas Finanças RENOVA.
2. Criar a chave de assinatura de produção e configurar Play App Signing.
3. Criar o app no Google Play Console com o mesmo package name.
4. Implementar a estratégia de assinatura de R$ 9,90 compatível com as políticas do Google Play (Play Billing e/ou programa alternativo aplicável no Brasil).
5. Preparar Política de Privacidade e declaração de Segurança dos dados.
6. Criar screenshots, feature graphic, descrição curta/completa e classificação indicativa.
7. Testar login, recuperação de senha, pagamentos, upload, relatórios e RENOVA IA em aparelhos Android reais.
8. Gerar o `.aab` assinado e enviar primeiro para teste interno/fechado.

## Observação de segurança

Nenhuma chave secreta, service role do Supabase, credencial do Mercado Pago ou chave de assinatura Android deve ser versionada no GitHub.
