"""
Script para verificar as restrições da tabela 'clubes'.
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from Coleta_de_dados.database.config import DatabaseSettings

def check_unique_constraint():
    """Verifica se a restrição UNIQUE na coluna 'nome' da tabela 'clubes' existe."""
    try:
        # Configura a conexão com o banco de dados
        settings = DatabaseSettings()
        engine = create_engine(settings.database_url)
        
        # Cria uma sessão
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Consulta para verificar a restrição UNIQUE
        query = """
        SELECT con.conname, pg_get_constraintdef(con.oid)
        FROM pg_constraint con
        JOIN pg_class rel ON rel.oid = con.conrelid
        WHERE rel.relname = 'clubes' 
        AND con.contype = 'u';
        """
        
        result = session.execute(text(query)).fetchall()
        
        if result:
            print("Restrições UNIQUE encontradas na tabela 'clubes':")
            for constraint in result:
                print(f"- Nome: {constraint[0]}, Definição: {constraint[1]}")
        else:
            print("Nenhuma restrição UNIQUE encontrada na tabela 'clubes'.")
            
        session.close()
        return True
        
    except Exception as e:
        print(f"Erro ao verificar restrições: {e}")
        return False

if __name__ == "__main__":
    check_unique_constraint()
