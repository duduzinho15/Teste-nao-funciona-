import os
import sys
from alembic.config import Config
from alembic import command
from dotenv import load_dotenv

def verificar_migracoes():
    print("=== Verificando Migrações do Alembic ===")
    
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    # Configura o Alembic
    alembic_cfg = Config("alembic.ini")
    
    try:
        # 1. Mostra o histórico de migrações
        print("\nHistórico de migrações:")
        command.history(alembic_cfg)
        
        # 2. Mostra a versão atual
        print("\nVersão atual do banco de dados:")
        command.current(alembic_cfg)
        
        # 3. Lista as migrações pendentes
        print("\nMigrações pendentes:")
        command.heads(alembic_cfg)
        
        # 4. Verifica se há migrações pendentes
        print("\nVerificando migrações pendentes...")
        command.check(alembic_cfg)
        
    except Exception as e:
        print(f"\nErro ao verificar migrações: {e}")
        print("\nPossíveis causas:")
        print("1. O arquivo alembic.ini não foi encontrado")
        print("2. As configurações de banco de dados no alembic.ini estão incorretas")
        print("3. O Alembic não está instalado no ambiente Python")
        print(f"\nDetalhes do erro: {str(e)}")

if __name__ == "__main__":
    verificar_migracoes()
