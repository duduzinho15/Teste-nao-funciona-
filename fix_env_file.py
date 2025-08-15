"""
Script para substituir o arquivo .env por uma versão limpa.
"""
import os
import shutil

def main():
    # Caminho para o arquivo .env atual e backup
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    backup_path = os.path.join(os.path.dirname(__file__), '.env.bak')
    clean_path = os.path.join(os.path.dirname(__file__), '.env.clean')
    
    # Conteúdo limpo para o arquivo .env
    clean_content = """# PostgreSQL Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=apostapro_db
DB_USER=apostapro_user
DB_PASSWORD=senha_segura_123

# PostgreSQL Admin Configuration (for reset operations)
DB_ROOT_USER=postgres
DB_ROOT_PASSWORD=postgres

# Application Settings
DEBUG=True
ENVIRONMENT=development
SECRET_KEY=change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Settings
API_RELOAD=True
API_HOST=0.0.0.0
API_PORT=8000

# FBRef Settings
FBREF_BASE_URL=https://fbref.com

# API Rate Limiting
API_RATE_LIMIT=1000
API_RATE_LIMIT_PERIOD=60
"""
    
    try:
        # Fazer backup do arquivo .env atual se ele existir
        if os.path.exists(env_path):
            shutil.copy2(env_path, backup_path)
            print(f"✅ Backup criado: {backup_path}")
        
        # Escrever o novo conteúdo no arquivo .env
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(clean_content)
        
        print(f"✅ Arquivo .env atualizado com sucesso!")
        print("\nPróximos passos:")
        print("1. Verifique se as credenciais no arquivo .env estão corretas")
        print("2. Execute o script de reset do banco de dados:")
        print("   python reset_database.py")
        
        return 0
    except Exception as e:
        print(f"❌ Erro ao atualizar o arquivo .env: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
