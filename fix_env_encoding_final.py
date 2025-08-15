"""
Script para corrigir o arquivo .env com encoding UTF-8 puro (sem BOM)
"""
import os

def main():
    # Conteúdo correto do arquivo .env
    env_content = """# PostgreSQL Configuration
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
    # Fazer backup do arquivo .env atual se existir
    if os.path.exists('.env'):
        try:
            os.rename('.env', '.env.bak')
            print("✅ Backup do arquivo .env criado como .env.bak")
        except Exception as e:
            print(f"⚠️ Erro ao fazer backup do arquivo .env: {e}")
    
    # Escrever o novo conteúdo no arquivo .env
    try:
        with open('.env', 'wb') as f:
            f.write(env_content.encode('utf-8'))
        print("✅ Arquivo .env corrigido com sucesso!")
        return 0
    except Exception as e:
        print(f"❌ Erro ao escrever o arquivo .env: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
