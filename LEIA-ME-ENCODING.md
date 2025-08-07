# 📝 Instruções para Corrigir Problemas de Encoding no PostgreSQL

Este guia contém instruções passo a passo para corrigir problemas de encoding no banco de dados PostgreSQL do projeto ApostaPro.

## 📋 Pré-requisitos

- PostgreSQL 17 instalado e em execução
- Acesso de administrador ao PostgreSQL
- Python 3.8+ instalado
- Pacotes Python necessários: `psycopg2-binary`

## 🔄 Passo a Passo

### 1. 🔑 Redefinir Senha do PostgreSQL

1. Feche todos os programas que possam estar usando o PostgreSQL
2. Clique com o botão direito em `reset_password.ps1` e selecione "Executar como Administrador"
3. O script irá:
   - Parar o serviço PostgreSQL
   - Redefinir a senha para `Canjica@@2025`
   - Reiniciar o serviço

### 2. 🆕 Criar Novo Banco de Dados com Encoding Correto

1. Abra o Prompt de Comando como Administrador
2. Navegue até a pasta do projeto
3. Execute:
   ```
   psql -U postgres -f criar_banco_utf8.sql
   ```
4. Verifique se o banco `apostapro_utf8` foi criado com sucesso

### 3. 📤 Exportar e Importar Dados

1. Execute o arquivo `exportar_importar_dados.bat`
   - Clique duas vezes no arquivo ou execute pelo prompt de comando
2. O script irá:
   - Fazer backup do banco antigo
   - Importar para o novo banco com encoding correto

### 4. 🔍 Verificar e Corrigir Dados

1. Instale as dependências necessárias:
   ```
   pip install psycopg2-binary
   ```
2. Execute o script de correção:
   ```
   python corrigir_dados.py
   ```
3. O script irá:
   - Analisar todas as tabelas
   - Identificar problemas de encoding
   - Tentar corrigir automaticamente
   - Gerar um log `correcao_encoding.log`

## 🔧 Solução de Problemas

### Erro de Autenticação
- Verifique se a senha está correta
- Confirme se o usuário tem permissões adequadas

### Erro de Conexão
- Verifique se o PostgreSQL está em execução
- Confirme a porta de conexão (padrão: 5432)

### Erros de Encoding Persistem
- Verifique o arquivo de log gerado
- Execute o script de verificação:
  ```
  python verificar_encoding.py
  ```

## 📊 Verificação Final

Após executar todos os passos, verifique se:

1. O banco `apostapro_utf8` foi criado
2. Os dados foram migrados corretamente
3. Não há mais erros de encoding
4. A aplicação está se conectando ao novo banco

## 🔄 Atualizar Aplicação

Atualize o arquivo de configuração da aplicação para usar o novo banco:

```python
# No arquivo config.py
DATABASE_URL = "postgresql+psycopg2://postgres:Canjica@@2025@localhost:5432/apostapro_utf8"
```

## 📞 Suporte

Em caso de problemas, consulte os logs gerados ou entre em contato com a equipe de desenvolvimento.
