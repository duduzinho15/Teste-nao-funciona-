import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def check_alembic_state():
    print("=== Verificando o estado do Alembic e do banco de dados ===\n")
    
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    # Configurações de conexão
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'apostapro_db'),
        'user': os.getenv('DB_USER', 'apostapro_user'),
        'password': os.getenv('DB_PASSWORD', 'senha_segura_123')
    }
    
    # Cria a URL de conexão
    db_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    
    try:
        # Conecta ao banco de dados
        print(f"Conectando ao banco de dados {db_config['database']} em {db_config['host']}:{db_config['port']}...")
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Verifica se a tabela alembic_version existe
            print("\nVerificando a tabela alembic_version...")
            try:
                result = conn.execute(text("SELECT * FROM alembic_version;"))
                current_version = result.scalar()
                print(f"✅ Versão atual do Alembic no banco: {current_version}")
            except Exception as e:
                print(f"❌ Erro ao acessar a tabela alembic_version: {e}")
                print("A tabela alembic_version não existe ou há um problema de permissão.")
                current_version = None
            
            # Lista todas as tabelas no esquema público
            print("\nListando tabelas no esquema público...")
            try:
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name;
                "))
                tables = [row[0] for row in result]
                
                if not tables:
                    print("Nenhuma tabela encontrada no esquema público.")
                else:
                    print("Tabelas encontradas:")
                    for table in tables:
                        print(f"- {table}")
                        
                    # Verifica se a tabela posts_redes_sociais existe
                    if 'posts_redes_sociais' in tables:
                        print("\n✅ A tabela 'posts_redes_sociais' existe no banco de dados.")
                    else:
                        print("\n❌ A tabela 'posts_redes_sociais' NÃO foi encontrada no banco de dados.")
                        
            except Exception as e:
                print(f"❌ Erro ao listar tabelas: {e}")
            
            # Verifica as migrações aplicadas
            if current_version:
                print(f"\nVerificando migrações aplicadas...")
                try:
                    # Lista todos os arquivos de migração na pasta versions
                    versions_dir = os.path.join(os.path.dirname(__file__), 'alembic', 'versions')
                    if os.path.exists(versions_dir):
                        migration_files = [f for f in os.listdir(versions_dir) 
                                        if f.endswith('.py') and f != '__init__.py']
                        
                        print(f"\nArquivos de migração encontrados ({len(migration_files)}):")
                        for file in sorted(migration_files):
                            # Extrai o ID da revisão do nome do arquivo
                            rev_id = file.split('_')[0]
                            status = "✅ APLICADA" if current_version == rev_id else "  "
                            print(f"{status} {file}")
                    else:
                        print(f"❌ Diretório de migrações não encontrado: {versions_dir}")
                        
                except Exception as e:
                    print(f"❌ Erro ao verificar migrações: {e}")
        
        print("\n=== Verificação concluída ===")
        
    except Exception as e:
        print(f"\n❌ Erro ao conectar ao banco de dados: {e}")
        print("\nVerifique se:")
        print("1. O servidor PostgreSQL está em execução")
        print("2. O banco de dados e o usuário existem")
        print("3. A senha está correta")
        print("4. O PostgreSQL está configurado para aceitar conexões TCP/IP")
        print(f"\nDetalhes do erro: {str(e)}")

if __name__ == "__main__":
    check_alembic_state()
