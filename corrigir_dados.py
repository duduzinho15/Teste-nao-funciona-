"""
Script para verificar e corrigir problemas de encoding nos dados
"""

import psycopg2
from psycopg2 import sql
import logging
from typing import List, Dict, Any, Optional
import re

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('correcao_encoding.log'),
        logging.StreamHandler()
    ]
)

class DatabaseFixer:
    def __init__(self, connection_string: str):
        """Inicializa o corretor de banco de dados."""
        self.connection_string = connection_string
        self.conn = None
        self.encoding_issues = {}
        
    def connect(self) -> bool:
        """Estabelece conexão com o banco de dados."""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            self.conn.set_client_encoding('LATIN1')  # Forçar LATIN1 para leitura
            logging.info("✅ Conexão estabelecida com sucesso!")
            return True
        except Exception as e:
            logging.error(f"❌ Erro ao conectar ao banco de dados: {e}")
            return False
    
    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()
            logging.info("Conexão fechada.")
    
    def list_tables(self) -> List[str]:
        """Lista todas as tabelas do banco de dados."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                return [row[0] for row in cur.fetchall()]
        except Exception as e:
            logging.error(f"Erro ao listar tabelas: {e}")
            return []
    
    def check_column_encoding(self, table: str, column: str) -> bool:
        """Verifica se há problemas de encoding em uma coluna."""
        try:
            with self.conn.cursor() as cur:
                query = sql.SQL("""
                    SELECT {column} 
                    FROM {table} 
                    WHERE {column} IS NOT NULL
                    LIMIT 1000
                ").format(
                    column=sql.Identifier(column),
                    table=sql.Identifier(table)
                )
                
                try:
                    cur.execute(query)
                    for row in cur.fetchall():
                        try:
                            # Tenta converter para string e codificar/decodificar
                            str(row[0]).encode('latin1').decode('utf-8')
                        except UnicodeError:
                            return True  # Problema de encoding encontrado
                    return False
                except Exception as e:
                    logging.warning(f"  ⚠️  Erro ao verificar coluna {column}: {e}")
                    return False
                    
        except Exception as e:
            logging.error(f"Erro ao verificar encoding da coluna {column}: {e}")
            return False
    
    def fix_encoding_issues(self, table: str, columns: List[str]):
        """Tenta corrigir problemas de encoding nos dados."""
        try:
            with self.conn.cursor() as cur:
                for column in columns:
                    logging.info(f"  🔄 Corrigindo encoding na coluna {column}...")
                    
                    # Atualizar cada registro problemático
                    update_query = sql.SQL("""
                        UPDATE {table} 
                        SET {column} = CONVERT(FROM(""" + column + """::bytea, 'LATIN1'), 'UTF8')
                        WHERE {column} IS NOT NULL
                        AND {column} != ''
                        AND {column} ~ '[^\x00-\x7F]'
                    """).format(
                        table=sql.Identifier(table),
                        column=sql.Identifier(column)
                    )
                    
                    try:
                        cur.execute(update_query)
                        self.conn.commit()
                        logging.info(f"  ✅ Coluna {column} atualizada com sucesso!")
                    except Exception as e:
                        self.conn.rollback()
                        logging.error(f"  ❌ Erro ao atualizar coluna {column}: {e}")
                        
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Erro ao corrigir encoding na tabela {table}: {e}")
    
    def analyze_database(self):
        """Analisa todo o banco de dados em busca de problemas de encoding."""
        if not self.conn:
            if not self.connect():
                return
        
        tables = self.list_tables()
        if not tables:
            logging.warning("Nenhuma tabela encontrada no banco de dados.")
            return
        
        logging.info(f"🔍 Analisando {len(tables)} tabelas em busca de problemas de encoding...")
        
        for table in tables:
            logging.info(f"\n📊 Tabela: {table}")
            
            # Obter colunas de texto da tabela
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = %s 
                    AND data_type IN ('character varying', 'text', 'character', 'varchar')
                """, (table,))
                
                text_columns = [row[0] for row in cur.fetchall()]
                
                if not text_columns:
                    logging.info("  ℹ️  Nenhuma coluna de texto encontrada.")
                    continue
                
                logging.info(f"  🔍 Verificando {len(text_columns)} colunas de texto...")
                
                # Verificar cada coluna
                columns_with_issues = []
                for column in text_columns:
                    if self.check_column_encoding(table, column):
                        logging.warning(f"  ⚠️  Possível problema de encoding encontrado na coluna: {column}")
                        columns_with_issues.append(column)
                
                # Se houver colunas com problemas, tentar corrigir
                if columns_with_issues:
                    logging.info(f"  🛠️  Tentando corrigir {len(columns_with_issues)} colunas com problemas...")
                    self.fix_encoding_issues(table, columns_with_issues)
                else:
                    logging.info("  ✅ Nenhum problema de encoding encontrado.")

def main():
    print("""
🔧 CORRETOR DE ENCODING PARA POSTGRESQL
==================================
Este script irá verificar e tentar corrigir problemas de encoding no banco de dados.
""")
    
    # Configuração de conexão
    db_config = {
        'host': 'localhost',
        'port': '5432',
        'dbname': 'apostapro_utf8',
        'user': 'postgres',
        'password': 'Canjica@@2025'
    }
    
    # Criar string de conexão
    conn_string = f"host={db_config['host']} port={db_config['port']} dbname={db_config['dbname']} user={db_config['user']} password={db_config['password']}"
    
    # Inicializar corretor
    fixer = DatabaseFixer(conn_string)
    
    try:
        # Conectar e analisar
        if fixer.connect():
            fixer.analyze_database()
            print("\n✅ Análise concluída! Verifique o arquivo 'correcao_encoding.log' para detalhes.")
    except Exception as e:
        logging.error(f"Erro durante a execução: {e}")
    finally:
        fixer.close()

if __name__ == "__main__":
    main()
