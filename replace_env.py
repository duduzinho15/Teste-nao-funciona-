"""
Script para substituir o arquivo .env por uma versão corrigida.
"""
import os
import shutil

def main():
    try:
        # Verificar se o arquivo .env.fixed existe
        if not os.path.exists('.env.fixed'):
            print("❌ Arquivo .env.fixed não encontrado!")
            return 1
        
        # Fazer backup do arquivo .env atual se ele existir
        if os.path.exists('.env'):
            shutil.copy2('.env', '.env.bak')
            print("✅ Backup do arquivo .env criado como .env.bak")
        
        # Copiar o arquivo .env.fixed para .env
        shutil.copy2('.env.fixed', '.env')
        print("✅ Arquivo .env substituído com sucesso!")
        
        # Mostrar as primeiras linhas do novo arquivo .env
        print("\n📝 Conteúdo do novo arquivo .env:")
        print("-" * 50)
        with open('.env', 'r') as f:
            for i, line in enumerate(f):
                if i < 20:  # Mostrar apenas as primeiras 20 linhas
                    print(line.strip())
                else:
                    print("...")
                    break
        print("-" * 50)
        
        print("\n✅ Próximos passos:")
        print("1. Verifique se as credenciais no arquivo .env estão corretas")
        print("2. Execute o script de reset do banco de dados:")
        print("   python reset_database.py")
        
        return 0
    except Exception as e:
        print(f"❌ Erro ao substituir o arquivo .env: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
