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
        # Nome do arquivo temporário
        temp_file = 'temp_env_file.txt'
        
        # Escrever o conteúdo no arquivo temporário em modo binário
        with open(temp_file, 'wb') as f:
            f.write(env_content)
        
        # Verificar se o arquivo temporário foi criado corretamente
        if os.path.exists(temp_file):
            # Ler o conteúdo do arquivo temporário
            with open(temp_file, 'rb') as f:
                saved_content = f.read()
            
            # Verificar se o conteúdo está correto
            if saved_content == env_content:
                # Remover o arquivo .env existente se existir
                if os.path.exists('.env'):
                    os.remove('.env')
                
                # Renomear o arquivo temporário para .env
                os.rename(temp_file, '.env')
                
                print("✅ Arquivo .env criado com sucesso!")
                print("\n📝 Conteúdo do arquivo .env:")
                print("-" * 50)
                print(env_content.decode('utf-8').strip())
                print("-" * 50)
                return 0
            else:
                print("❌ Erro: O conteúdo salvo não corresponde ao conteúdo esperado.")
                print(f"Tamanho esperado: {len(env_content)}, Tamanho salvo: {len(saved_content)}")
                return 1
        else:
            print("❌ Erro: Falha ao criar o arquivo temporário.")
            return 1
            
    except Exception as e:
        print(f"❌ Erro ao processar o arquivo .env: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
