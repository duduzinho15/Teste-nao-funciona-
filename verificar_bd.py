"""
Script simples para verificar as tabelas no banco de dados.
"""
from sqlalchemy import create_engine, inspect
from Coleta_de_dados.database.config import db_manager

def main():
    print("🔍 Verificando tabelas no banco de dados...")
    
    try:
        # Obter a URL de conexão do banco de dados
        db_url = db_manager.settings.database_url or f"postgresql://{db_manager.settings.db_user}:{db_manager.settings.db_password}@{db_manager.settings.db_host}:{db_manager.settings.db_port}/{db_manager.settings.db_name}"
        
        # Criar engine
        engine = create_engine(db_url)
        
        # Criar inspetor
        inspector = inspect(engine)
        
        # Listar todas as tabelas
        print("\n📋 Tabelas no banco de dados:")
        print("-" * 50)
        for table_name in sorted(inspector.get_table_names()):
            print(f"- {table_name}")
        
        # Verificar se a tabela noticias_clubes existe
        if 'noticias_clubes' in inspector.get_table_names():
            print("\n✅ Tabela 'noticias_clubes' encontrada!")
            
            # Mostrar colunas
            print("\n📝 Colunas da tabela 'noticias_clubes':")
            print("-" * 50)
            for column in inspector.get_columns('noticias_clubes'):
                print(f"- {column['name']}: {column['type']} (nullable={column['nullable']})")
            
            # Mostrar índices
            print("\n🔍 Índices da tabela 'noticias_clubes':")
            print("-" * 50)
            for index in inspector.get_indexes('noticias_clubes'):
                print(f"- {index['name']}: {index['column_names']} (unique={index.get('unique', False)})")
            
            # Mostrar chaves estrangeiras
            print("\n🔗 Chaves estrangeiras da tabela 'noticias_clubes':")
            print("-" * 50)
            for fk in inspector.get_foreign_keys('noticias_clubes'):
                print(f"- {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        else:
            print("\n❌ Tabela 'noticias_clubes' NÃO encontrada!")
        
    except Exception as e:
        print(f"\n❌ Erro ao acessar o banco de dados: {e}")
    
    print("\n✅ Verificação concluída!")

if __name__ == "__main__":
    main()
