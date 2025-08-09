#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar e corrigir problemas de codificação no PostgreSQL
"""
import psycopg2
import sys
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def conectar_banco(host='localhost', user='postgres', password='@Eduardo123', 
                 port=5432, database='postgres'):
    """Conecta ao banco de dados PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            database=database,
            client_encoding='LATIN1'  # Tenta forçar LATIN1 para evitar erros iniciais
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return None

def verificar_encoding_banco(conn, dbname):
    """Verifica a codificação de um banco de dados específico"""
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT pg_encoding_to_char(encoding) FROM pg_database WHERE datname = %s",
                (dbname,)
            )
            result = cur.fetchone()
            if result:
                return result[0]
            return None
    except Exception as e:
        print(f"❌ Erro ao verificar encoding do banco {dbname}: {e}")
        return None

def listar_bancos_dados(conn):
    """Lista todos os bancos de dados no servidor"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.datname, pg_encoding_to_char(d.encoding) as encoding
                FROM pg_database d
                WHERE d.datistemplate = false
                ORDER BY d.datname;
            """)
            return cur.fetchall()
    except Exception as e:
        print(f"❌ Erro ao listar bancos de dados: {e}")
        return []

def listar_encodings_disponiveis(conn):
    """Lista todas as codificações disponíveis no PostgreSQL"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name, description FROM pg_catalog.pg_encoding")
            return cur.fetchall()
    except Exception as e:
        print(f"❌ Erro ao listar codificações disponíveis: {e}")
        return []

def corrigir_encoding_banco(conn, dbname, novo_encoding='UTF8'):
    """Altera a codificação de um banco de dados"""
    try:
        with conn.cursor() as cur:
            print(f"\n🔧 Alterando a codificação do banco '{dbname}' para {novo_encoding}...")
            
            # Primeiro, desconecta todos os usuários do banco
            cur.execute("""
                SELECT pg_terminate_backend(pid) 
                FROM pg_stat_activity 
                WHERE datname = %s AND pid <> pg_backend_pid();
            """, (dbname,))
            
            # Altera a codificação do banco
            cur.execute(
                sql.SQL("ALTER DATABASE {} ENCODING '{}' LC_COLLATE 'pt_BR.UTF-8' LC_CTYPE 'pt_BR.UTF-8' TEMPLATE template0").format(
                    sql.Identifier(dbname),
                    sql.SQL(novo_encoding)
                )
            )
            
            print(f"✅ Codificação do banco '{dbname}' alterada para {novo_encoding} com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao alterar codificação do banco '{dbname}': {e}")
        return False

def main():
    print("=== Verificador de Codificação PostgreSQL ===\n")
    
    # Conecta ao banco de dados postgres padrão
    conn = conectar_banco()
    if not conn:
        print("❌ Não foi possível conectar ao servidor PostgreSQL.")
        return
    
    try:
        # Lista os bancos de dados
        print("📊 Bancos de dados no servidor:")
        bancos = listar_bancos_dados(conn)
        if not bancos:
            print("❌ Nenhum banco de dados encontrado.")
            return
        
        for i, (dbname, encoding) in enumerate(bancos, 1):
            print(f"{i}. {dbname} (Encoding: {encoding or 'Desconhecido'})")
        
        # Seleciona um banco para verificar
        while True:
            try:
                opcao = input("\n🔍 Selecione o número do banco para verificar (ou 's' para sair): ").strip().lower()
                if opcao == 's':
                    return
                
                idx = int(opcao) - 1
                if 0 <= idx < len(bancos):
                    db_selecionado = bancos[idx][0]
                    break
                print("❌ Opção inválida. Tente novamente.")
            except ValueError:
                print("❌ Por favor, digite um número válido ou 's' para sair.")
        
        print(f"\n🔍 Verificando banco de dados: {db_selecionado}")
        
        # Verifica o encoding atual
        encoding_atual = verificar_encoding_banco(conn, db_selecionado)
        print(f"🔤 Encoding atual: {encoding_atual or 'Não identificado'}")
        
        # Lista encodings disponíveis
        print("\n📝 Codificações disponíveis:")
        encodings = listar_encodings_disponiveis(conn)
        for name, desc in encodings:
            print(f"- {name}: {desc}")
        
        # Opção para corrigir o encoding
        if input("\n🔧 Deseja corrigir o encoding deste banco? (s/n): ").strip().lower() == 's':
            novo_encoding = input("Digite o nome da nova codificação (ex: UTF8, LATIN1, etc): ").strip().upper()
            if novo_encoding:
                if corrigir_encoding_banco(conn, db_selecionado, novo_encoding):
                    print("\n✅ Operação concluída com sucesso!")
                    print("⚠️ Recomenda-se reiniciar o servidor PostgreSQL para aplicar as alterações.")
                else:
                    print("\n❌ Não foi possível alterar a codificação do banco.")
    
    finally:
        conn.close()
        print("\n👋 Conexão encerrada.")

if __name__ == "__main__":
    main()
