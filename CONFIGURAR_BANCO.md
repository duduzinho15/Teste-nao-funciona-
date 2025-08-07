# Configuração do Banco de Dados - ApostaPro

Este guia explica como configurar corretamente o banco de dados PostgreSQL para o projeto ApostaPro.

## 📋 Pré-requisitos

- PostgreSQL 17 instalado e em execução
- Acesso de administrador ao PostgreSQL
- Python 3.8+ instalado
- Ambiente virtual Python configurado (recomendado)

## 🔄 Passo a Passo

### 1. Configurar o Banco de Dados

1. **Execute o script de configuração** como administrador:
   ```powershell
   .\configurar_banco.ps1
   ```
   Este script irá:
   - Criar o usuário do banco de dados (se não existir)
   - Criar o banco de dados com encoding correto
   - Configurar permissões

### 2. Executar Migrações

1. **Execute as migrações do Alembic** para criar as tabelas:
   ```powershell
   .\executar_migracoes.ps1
   ```
   Este script irá:
   - Verificar migrações pendentes
   - Aplicar todas as migrações necessárias
   - Verificar se as tabelas foram criadas

### 3. Verificar a Configuração

1. **Verifique se as tabelas foram criadas**:
   ```powershell
   & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U apostapro_user -d apostapro_db -c "\dt"
   ```

2. **Verifique os dados iniciais** (se aplicável):
   ```powershell
   & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U apostapro_user -d apostapro_db -c "SELECT * FROM informacoes_uteis LIMIT 5;"
   ```

## 🔧 Solução de Problemas

### Erro de Autenticação
- Verifique se a senha no arquivo `.env` está correta
- Confirme se o usuário tem permissões no banco de dados

### Erro de Conexão
- Verifique se o PostgreSQL está em execução
- Confirme se a porta está correta (padrão: 5432)
- Verifique se o firewall permite conexões no PostgreSQL

### Erro de Permissão
- Execute os scripts como administrador
- Verifique se o usuário tem privilégios suficientes

## 📊 Verificação Final

Após executar todos os passos, verifique se:

1. O banco de dados `apostapro_db` foi criado
2. As tabelas foram criadas corretamente
3. O usuário `apostapro_user` tem acesso ao banco
4. A aplicação consegue se conectar ao banco

## 📞 Suporte

Em caso de problemas, consulte os logs gerados ou entre em contato com a equipe de desenvolvimento.
