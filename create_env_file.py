"""
Script para criar o arquivo .env de forma confiável
"""
import os

def main():
    # Conteúdo em bytes para evitar problemas de codificação
    env_content = b"""# PostgreSQL Configuration
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
    
    try:
        # Fazer backup do arquivo .env atual se existir
        if os.path.exists('.env'):
            with open('.env.bak', 'wb') as f_backup:
                with open('.env', 'rb') as f_original:
                    f_backup.write(f_original.read())
            print("✅ Backup do arquivo .env criado como .env.bak")
        
        # Escrever o novo conteúdo no arquivo .env em modo binário
        with open('.env', 'wb') as f:
            f.write(env_content)
        
        print("✅ Arquivo .env criado/atualizado com sucesso!")
        
        # Verificar se o arquivo foi salvo corretamente
        with open('.env', 'rb') as f:
            saved_content = f.read()
        
        if saved_content == env_content:
            print("✅ Verificação de integridade: O arquivo foi salvo corretamente!")
            print("\n📝 Conteúdo do arquivo .env:")
            print("-" * 50)
            print(saved_content.decode('utf-8').strip())
            print("-" * 50)
            return 0
        else:
            print("❌ Erro: O conteúdo salvo não corresponde ao conteúdo esperado.")
            print(f"Tamanho esperado: {len(env_content)}, Tamanho salvo: {len(saved_content)}")
            return 1
            
    except Exception as e:
        print(f"❌ Erro ao processar o arquivo .env: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
