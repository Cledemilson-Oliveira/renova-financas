# Controle de acesso — RENOVA Finanças

O projeto usa Supabase Auth para autenticação e a tabela `public.user_access` para autorização.

## Papéis

- `dono`: controle máximo do sistema e gestão de acessos.
- `admin`: reservado para delegação futura de funções administrativas.
- `usuario`: acesso normal aos próprios dados financeiros.

## Status

- `ativo`: pode acessar os próprios dados financeiros.
- `suspenso`: permanece cadastrado, mas o acesso aos dados financeiros é bloqueado pelas políticas RLS.

## Conta do dono

O e-mail do dono é configurado exclusivamente na tabela privada `private.owner_config` no Supabase e não é hardcoded no repositório público.

Quando uma conta é criada no Supabase Auth com o e-mail configurado como dono, um trigger cria automaticamente o registro correspondente em `public.user_access` com:

- `role = 'dono'`
- `status = 'ativo'`

Senhas nunca são armazenadas no GitHub, em migrations ou em tabelas próprias da aplicação. O gerenciamento de senha fica exclusivamente com o Supabase Auth.

## Gestão manual

O dono pode consultar todos os registros de `public.user_access` e alterar `role` e `status` de contas que não sejam a própria conta de dono. As políticas impedem que o dono seja rebaixado ou suspenso por essa interface de atualização.

Uma tela administrativa dentro do app pode consumir essas permissões sem usar `service_role` ou chave secreta no frontend.
