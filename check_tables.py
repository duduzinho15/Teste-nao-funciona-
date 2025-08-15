import os
import psycopg2
from tabulate import tabulate

def check_tables():
    # Configurações do banco de dados
    db_config = {
        'host': 'localhost',
        'database': 'apostapro_db',
        'user': 'apostapro_user',
        'password': 'senha_segura_123',
        'port': '5432'
    }
    
    try:
        # Conecta ao banco de dados
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # Lista todas as tabelas no esquema público
        print("🔍 Tabelas no banco de dados:")
        print("=" * 50)
        
        # Obtém a lista de tabelas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cur.fetchall()]
        print("\n".join([f"- {table}" for table in tables]))
        
        # Função para verificar o conteúdo de uma tabela
        def check_table(table_name, limit=5):
            print(f"\n📋 Conteúdo da tabela '{table_name}':")
            print("=" * 50)
            
            try:
                # Obtém a estrutura da tabela
                cur.execute(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """)
                
                columns = cur.fetchall()
                print("\nEstrutura:")
                for col in columns:
                    print(f"- {col[0]}: {col[1]} (nullable: {col[2]})")
                
                # Obtém os dados da tabela
                cur.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
                rows = cur.fetchall()
                
                if rows:
                    print(f"\nPrimeiros {min(len(rows), limit)} registros:")
                    # Obtém os nomes das colunas
                    col_names = [desc[0] for desc in cur.description]
                    # Exibe os dados em formato de tabela
                    print(tabulate(rows, headers=col_names, tablefmt="grid"))
                    
                    # Conta o total de registros
                    cur.execute(f"SELECT COUNT(*) FROM {table_name};")
                    total = cur.fetchone()[0]
                    print(f"\nTotal de registros: {total}")
                else:
                    print("\nA tabela está vazia.")
                    
            except Exception as e:
                print(f"❌ Erro ao verificar a tabela {table_name}: {e}")
        
        # Verifica as tabelas relevantes para o endpoint /matches
        relevant_tables = [
            'paises_clubes', 'clubes', 'competicoes', 'estadios', 
            'partidas', 'estatisticas_partidas'
        ]
        
        for table in relevant_tables:
            if table in tables:
                check_table(table)
            else:
                print(f"\n❌ A tabela '{table}' não existe no banco de dados.")
        
        # Verifica as restrições de chave estrangeira para partidas
        print("\n🔍 Verificando restrições de chave estrangeira para a tabela 'partidas':")
        print("=" * 50)
        
        cur.execute("""
            SELECT
                tc.constraint_name, 
                kcu.column_name, 
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
            WHERE 
                tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = 'partidas';
        """)
        
        fks = cur.fetchall()
        
        if fks:
            print("\nRestrições de chave estrangeira:")
            for fk in fks:
                print(f"- {fk[1]} → {fk[2]}({fk[3]}) [constraint: {fk[0]}]")
        else:
            print("\nNenhuma restrição de chave estrangeira encontrada.")
        
        # Verifica se existem dados suficientes para testar o endpoint /matches
        print("\n🔍 Verificando dados para o endpoint /matches:")
        print("=" * 50)
        
        # Verifica se existem partidas
        cur.execute("SELECT COUNT(*) FROM partidas;")
        total_partidas = cur.fetchone()[0]
        print(f"Total de partidas: {total_partidas}")
        
        if total_partidas > 0:
            # Verifica se existem partidas com estatísticas
            cur.execute("""
                SELECT COUNT(*) 
                FROM partidas p
                JOIN estatisticas_partidas ep ON p.id = ep.partida_id;
            """)
            partidas_com_estatisticas = cur.fetchone()[0]
            print(f"Partidas com estatísticas: {partidas_com_estatisticas}")
            
            # Verifica se existem partidas finalizadas
            cur.execute("""
                SELECT COUNT(*) 
                FROM partidas 
                WHERE status = 'Finalizada';
            """)
            partidas_finalizadas = cur.fetchone()[0]
            print(f"Partidas finalizadas: {partidas_finalizadas}")
            
            # Verifica se existem partidas agendadas
            cur.execute("""
                SELECT COUNT(*) 
                FROM partidas 
                WHERE status = 'Agendada';
            """)
            partidas_agendadas = cur.fetchone()[0]
            print(f"Partidas agendadas: {partidas_agendadas}")
            
            # Verifica se existem clubes e competições
            cur.execute("SELECT COUNT(*) FROM clubes;")
            total_clubes = cur.fetchone()[0]
            print(f"\nTotal de clubes: {total_clubes}")
            
            cur.execute("SELECT COUNT(*) FROM competicoes;")
            total_competicoes = cur.fetchone()[0]
            print(f"Total de competições: {total_competicoes}")
            
            cur.execute("SELECT COUNT(*) FROM estadios;")
            total_estadios = cur.fetchone()[0]
            print(f"Total de estádios: {total_estadios}")
            
            # Verifica se existem dados suficientes para o endpoint /matches
            if total_partidas > 0 and total_clubes > 0 and total_competicoes > 0 and total_estadios > 0:
                print("\n✅ Dados suficientes para testar o endpoint /matches!")
                
                # Exemplo de consulta para o endpoint /matches
                print("\n📋 Exemplo de resposta do endpoint /matches:")
                cur.execute("""
                    SELECT 
                        p.id,
                        p.data_partida,
                        c1.nome AS clube_casa,
                        c2.nome AS clube_visitante,
                        comp.nome AS competicao,
                        p.rodada,
                        p.temporada,
                        p.gols_casa,
                        p.gols_visitante,
                        p.status,
                        e.nome AS estadio
                    FROM partidas p
                    JOIN clubes c1 ON p.clube_casa_id = c1.id
                    JOIN clubes c2 ON p.clube_visitante_id = c2.id
                    JOIN competicoes comp ON p.competicao_id = comp.id
                    LEFT JOIN estadios e ON p.estadio_id = e.id
                    ORDER BY p.data_partida
                    LIMIT 5;
                """)
                
                rows = cur.fetchall()
                if rows:
                    col_names = [desc[0] for desc in cur.description]
                    print(tabulate(rows, headers=col_names, tablefmt="grid"))
                else:
                    print("Nenhuma partida encontrada.")
            else:
                print("\n❌ Dados insuficientes para testar o endpoint /matches.")
        else:
            print("\n❌ Não há partidas cadastradas no banco de dados.")
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False
        cur.close()
    if 'conn' in locals():
        conn.close()

if __name__ == "__main__":
    check_tables()
