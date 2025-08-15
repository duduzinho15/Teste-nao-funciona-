"""
Script para corrigir problemas de encoding no arquivo .env
"""
import os

def main():
    try:
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
        # Fazer backup do arquivo .env atual
        if os.path.exists('.env'):
            with open('.env.bak', 'w', encoding='utf-8') as f_bak:
                with open('.env', 'r', encoding='utf-8', errors='ignore') as f_src:
                    f_bak.write(f_src.read())
            print("✅ Backup do arquivo .env criado como .env.bak")
        
        # Escrever o novo conteúdo no arquivo .env
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Arquivo .env corrigido com sucesso!")
        print("\n📝 Conteúdo do novo arquivo .env:")
        print("-" * 50)
        print(env_content)
        print("-" * 50)
        
        return 0
    except Exception as e:
        print(f"❌ Erro ao corrigir o arquivo .env: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
