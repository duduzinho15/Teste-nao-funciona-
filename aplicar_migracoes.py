import os
import sys
from alembic.config import Config
from alembic import command
from dotenv import load_dotenv

def aplicar_migracoes():
    print("=== Aplicando Migrações do Alembic ===")
    
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    # Configura o Alembic
    alembic_cfg = Config("alembic.ini")
    
    try:
        # 1. Mostra a versão atual
        print("\nVersão atual do banco de dados:")
        command.current(alembic_cfg)
        
        # 2. Aplica todas as migrações pendentes
        print("\nAplicando migrações pendentes...")
        command.upgrade(alembic_cfg, "head")
        
        # 3. Mostra a versão atualizada
        print("\nVersão após aplicação das migrações:")
        command.current(alembic_cfg)
        
        print("\nMigrações aplicadas com sucesso!")
        
    except Exception as e:
        print(f"\nErro ao aplicar migrações: {e}")
        print("\nPossíveis causas:")
        print("1. O arquivo alembic.ini não foi encontrado")
        print("2. As configurações de banco de dados no alembic.ini estão incorretas")
        print("3. O usuário não tem permissões suficientes no banco de dados")
        print(f"\nDetalhes do erro: {str(e)}")
        
        # Se houver um erro, tenta mostrar mais detalhes
        try:
            print("\nTentando obter mais detalhes do erro...")
            command.upgrade(alembic_cfg, "head", sql=True)
        except Exception as e2:
            print(f"Erro ao obter detalhes: {e2}")

if __name__ == "__main__":
    aplicar_migracoes()
