"""
Script para verificar a conexão com o PostgreSQL e testar credenciais.
"""
import psycopg2
import os
import sys
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

def test_connection(db_params):
    """Testa a conexão com o banco de dados."""
    try:
        conn = psycopg2.connect(**db_params)
        conn.close()
        return True, "Conexão bem-sucedida!"
    except psycopg2.Error as e:
        return False, f"Erro de conexão: {e}"

def main():
    # Configurações de conexão para testar
    test_cases = [
        {
            "name": "Superusuário (postgres)",
            "params": {
                "host": os.getenv('DB_HOST', 'localhost'),
                "port": os.getenv('DB_PORT', '5432'),
                "dbname": "postgres",
                "user": "postgres",
                "password": os.getenv('DB_ROOT_PASSWORD', "postgres")
            }
        },
        {
            "name": "Usuário da aplicação",
            "params": {
                "host": os.getenv('DB_HOST', 'localhost'),
                "port": os.getenv('DB_PORT', '5432'),
                "dbname": os.getenv('DB_NAME', 'apostapro_db'),
                "user": os.getenv('DB_USER', 'apostapro_user'),
                "password": os.getenv('DB_PASSWORD', 'senha_segura_123')
            }
        },
        {
            "name": "Sem senha (trust)",
            "params": {
                "host": os.getenv('DB_HOST', 'localhost'),
                "port": os.getenv('DB_PORT', '5432'),
                "dbname": "postgres",
                "user": "postgres",
                "password": ""
            }
        }
    ]

    print("🔍 Testando conexões com o PostgreSQL...\n")
    
    # Testar cada configuração
    for test in test_cases:
        print(f"🧪 Testando {test['name']}...")
        success, message = test_connection(test['params'])
        
        if success:
            print(f"✅ {message}")
            print(f"   Host: {test['params']['host']}")
            print(f"   Porta: {test['params']['port']}")
            print(f"   Usuário: {test['params']['user']}")
            print(f"   Banco: {test['params']['dbname']}")
            
            # Se for o superusuário, atualizar as variáveis de ambiente
            if test['name'] == "Superusuário (postgres)" and success:
                print("\n🔑 Atualizando variáveis de ambiente com credenciais do superusuário...")
                with open('.env', 'a') as f:
                    f.write("\n# Credenciais do superusuário para operações administrativas\n")
                    f.write(f"DB_ROOT_USER={test['params']['user']}\n")
                    f.write(f"DB_ROOT_PASSWORD={test['params']['password']}\n")
                print("✅ Variáveis de ambiente atualizadas!")
                
                # Retornar com sucesso se conseguirmos conectar como superusuário
                return True
        else:
            print(f"❌ {message}")
        
        print()  # Linha em branco para separar os testes
    
    return False

if __name__ == "__main__":
    if main():
        print("\n🎉 Tudo pronto! Agora você pode executar o script de reset do banco de dados.")
        print("Execute: python reset_database.py")
    else:
        print("\n❌ Não foi possível estabelecer uma conexão bem-sucedida com o PostgreSQL.")
        print("Por favor, verifique:")
        print("1. Se o serviço do PostgreSQL está em execução")
        print("2. Se as credenciais no arquivo .env estão corretas")
        print("3. Se o usuário tem permissões de superusuário")
        print("\nVocê pode tentar executar manualmente com: psql -U postgres -f manual_db_setup.sql")
