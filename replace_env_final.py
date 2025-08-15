"""
Script para substituir o arquivo .env corretamente
"""
import os
import shutil

def main():
    try:
        # Fazer backup do arquivo .env atual
        if os.path.exists('.env'):
            shutil.copy2('.env', '.env.bak')
            print("✅ Backup do arquivo .env criado como .env.bak")
        
        # Conteúdo do novo arquivo .env
        env_content = """# PostgreSQL Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=apostapro_db
DB_USER=apostapro_user
DB_PASSWORD=senha_segura_123

# PostgreSQL Admin Configuration
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
        # Escrever o novo conteúdo no arquivo .env
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Arquivo .env criado/atualizado com sucesso!")
        print("\n📝 Conteúdo do arquivo .env:")
        print("-" * 50)
        print(env_content)
        print("-" * 50)
        
        return 0
    except Exception as e:
        print(f"❌ Erro ao substituir o arquivo .env: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
