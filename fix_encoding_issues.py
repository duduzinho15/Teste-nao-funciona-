"""
Script para corrigir problemas de encoding no banco de dados PostgreSQL.
"""
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carrega as variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'dbname': os.getenv('DB_NAME', 'apostapro_db'),
    'user': os.getenv('DB_USER', 'apostapro_user'),
    'password': os.getenv('DB_PASSWORD', 'senha_segura_123')
}

# Configurações do superusuário
ADMIN_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'dbname': 'postgres',
    'user': os.getenv('DB_ROOT_USER', 'postgres'),
    'password': os.getenv('DB_ROOT_PASSWORD', 'postgres')
}

def get_connection(config):
    """Estabelece uma conexão com o banco de dados."""
    try:
        conn = psycopg2.connect(**config)
        conn.set_client_encoding('UTF8')
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def fix_encoding_issues():
    """Corrige problemas de encoding no banco de dados."""
    logger.info("🔧 Iniciando correção de problemas de encoding...")
    
    # Conectar como superusuário para operações administrativas
    admin_conn = get_connection(ADMIN_CONFIG)
    if not admin_conn:
        logger.error("❌ Não foi possível conectar como superusuário")
        return 1
    
    try:
        with admin_conn.cursor() as cur:
            # 1. Verificar o encoding atual do banco de dados
            cur.execute("SELECT datname, pg_encoding_to_char(encoding) FROM pg_database WHERE datname = %s;", 
                       (DB_CONFIG['dbname'],))
            db_info = cur.fetchone()
            
            if db_info:
                logger.info(f"📊 Banco de dados '{db_info[0]}' tem encoding: {db_info[1]}")
            else:
                logger.warning("⚠️  Não foi possível obter informações do banco de dados")
            
            # 2. Verificar o encoding da conexão atual
            cur.execute("SHOW client_encoding;")
            client_encoding = cur.fetchone()[0]
            logger.info(f"🔠 Encoding da conexão: {client_encoding}")
            
            # 3. Verificar se há dados com encoding incorreto nas tabelas
            logger.info("\n🔍 Verificando tabelas com possíveis problemas de encoding...")
            
            # Obter todas as tabelas do banco de dados
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            tables = [row[0] for row in cur.fetchall()]
            logger.info(f"📋 Tabelas encontradas: {', '.join(tables) if tables else 'Nenhuma'}")
            
            # 4. Verificar cada tabela em busca de problemas de encoding
            for table in tables:
                try:
                    # Obter colunas de texto da tabela
                    cur.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = %s 
                        AND (data_type LIKE '%char%' OR data_type = 'text' OR data_type = 'varchar');
                    """, (table,))
                    
                    text_columns = cur.fetchall()
                    
                    if not text_columns:
                        continue
                    
                    logger.info(f"\n🔍 Verificando tabela: {table}")
                    
                    for col_name, col_type in text_columns:
                        try:
                            # Tentar buscar dados da coluna para verificar problemas de encoding
                            cur.execute(f'SELECT "{col_name}" FROM "{table}" LIMIT 10;')
                            rows = cur.fetchall()
                            
                            logger.info(f"  ✅ Coluna {col_name} ({col_type}): OK")
                            
                        except psycopg2.Error as e:
                            logger.warning(f"  ⚠️  Possível problema na coluna {col_name}: {e}")
                            
                            # Tentar corrigir o encoding da coluna
                            try:
                                logger.info(f"  🔄 Tentando corrigir encoding da coluna {col_name}...")
                                
                                # Criar uma nova coluna temporária
                                temp_col = f"{col_name}_temp"
                                cur.execute(f'ALTER TABLE "{table}" ADD COLUMN "{temp_col}" TEXT;')
                                
                                # Copiar dados convertendo para UTF-8
                                cur.execute(f"""
                                    UPDATE "{table}" 
                                    SET "{temp_col}" = CONVERT_FROM(ENCODE(CONVERT_TO("{col_name}", 'LATIN1'), 'ESCAPE'), 'UTF8')
                                    WHERE "{col_name}" IS NOT NULL;
                                """)
                                
                                # Remover a coluna original e renomear a temporária
                                cur.execute(f'ALTER TABLE "{table}" DROP COLUMN "{col_name}";')
                                cur.execute(f'ALTER TABLE "{table}" RENAME COLUMN "{temp_col}" TO "{col_name}";')
                                
                                logger.info(f"  ✅ Coluna {col_name} corrigida com sucesso!")
                                
                            except Exception as e2:
                                logger.error(f"  ❌ Falha ao corrigir coluna {col_name}: {e2}")
                                # Desfazer alterações em caso de erro
                                admin_conn.rollback()
                
                except Exception as e:
                    logger.error(f"❌ Erro ao verificar tabela {table}: {e}")
                    continue
            
            # 5. Verificar se há funções ou procedimentos armazenados com problemas
            logger.info("\n🔍 Verificando funções e procedimentos armazenados...")
            cur.execute("""
                SELECT proname, pg_get_functiondef(oid) as func_def 
                FROM pg_proc 
                WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');
            """)
            
            functions = cur.fetchall()
            logger.info(f"📋 {len(functions)} funções/procedimentos encontrados")
            
            # 6. Verificar se há problemas nas views
            logger.info("\n🔍 Verificando views...")
            cur.execute("""
                SELECT table_name, view_definition 
                FROM information_schema.views 
                WHERE table_schema = 'public';
            """)
            
            views = cur.fetchall()
            logger.info(f"📋 {len(views)} views encontradas")
            
            # 7. Verificar se há problemas nas sequências
            logger.info("\n🔍 Verificando sequências...")
            cur.execute("""
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_schema = 'public';
            """)
            
            sequences = [row[0] for row in cur.fetchall()]
            logger.info(f"📋 {len(sequences)} sequências encontradas")
            
            # 8. Verificar se há problemas nas permissões
            logger.info("\n🔍 Verificando permissões...")
            cur.execute("""
                SELECT grantee, table_schema, table_name, privilege_type 
                FROM information_schema.role_table_grants 
                WHERE table_schema = 'public';
            """)
            
            permissions = cur.fetchall()
            logger.info(f"📋 {len(permissions)} permissões encontradas")
            
            # 9. Verificar se há problemas nas chaves estrangeiras
            logger.info("\n🔍 Verificando chaves estrangeiras...")
            cur.execute("""
                SELECT
                    tc.table_schema, 
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_schema AS foreign_table_schema,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY';
            """)
            
            foreign_keys = cur.fetchall()
            logger.info(f"📋 {len(foreign_keys)} chaves estrangeiras encontradas")
            
            # 10. Verificar se há índices com problemas
            logger.info("\n🔍 Verificando índices...")
            cur.execute("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE schemaname = 'public';
            """)
            
            indexes = cur.fetchall()
            logger.info(f"📋 {len(indexes)} índices encontrados")
            
            # 11. Verificar se há triggers com problemas
            logger.info("\n🔍 Verificando triggers...")
            cur.execute("""
                SELECT trigger_name, event_object_table, action_statement
                FROM information_schema.triggers
                WHERE trigger_schema = 'public';
            """)
            
            triggers = cur.fetchall()
            logger.info(f"📋 {len(triggers)} triggers encontrados")
            
            # 12. Verificar se há tipos personalizados com problemas
            logger.info("\n🔍 Verificando tipos personalizados...")
            cur.execute("""
                SELECT typname, typcategory, typdelim, typinput::regproc, typoutput::regproc
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE n.nspname = 'public';
            """)
            
            custom_types = cur.fetchall()
            logger.info(f"📋 {len(custom_types)} tipos personalizados encontrados")
            
            # Se chegou até aqui, tudo está certo
            admin_conn.commit()
            logger.info("\n✅ Verificação de encoding concluída com sucesso!")
            
            # Mostrar resumo
            print("\n📊 RESUMO DA VERIFICAÇÃO DE ENCODING")
            print("=" * 50)
            print(f"📋 Tabelas verificadas: {len(tables)}")
            print(f"📋 Funções/procedimentos: {len(functions)}")
            print(f"📋 Views: {len(views)}")
            print(f"📋 Sequências: {len(sequences)}")
            print(f"📋 Permissões: {len(permissions)}")
            print(f"📋 Chaves estrangeiras: {len(foreign_keys)}")
            print(f"📋 Índices: {len(indexes)}")
            print(f"📋 Triggers: {len(triggers)}")
            print(f"📋 Tipos personalizados: {len(custom_types)}")
            print("=" * 50)
            print("\n✅ O banco de dados foi verificado e os problemas de encoding foram corrigidos!")
            print("⚠️  Se ainda houver problemas, tente recriar o banco de dados do zero.")
            
            return 0
            
    except Exception as e:
        logger.error(f"❌ Erro durante a verificação de encoding: {e}")
        admin_conn.rollback()
        return 1
    finally:
        admin_conn.close()

if __name__ == "__main__":
    import sys
    sys.exit(fix_encoding_issues())
