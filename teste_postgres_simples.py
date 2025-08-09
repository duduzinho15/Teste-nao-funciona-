#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para testar a conexão com o PostgreSQL
"""
import psycopg2
import sys

def main():
    print("=== Teste de Conexão PostgreSQL ===")
    
    # Configuração de conexão
    config = {
        "host": "localhost",
        "database": "postgres",
        "user": "postgres",
        "password": "@Eduardo123",
        "port": "5432"
    }
    
    print("\nTentando conectar ao PostgreSQL...")
    print(f"Host: {config['host']}")
    print(f"Database: {config['database']}")
    print(f"User: {config['user']}")
    print(f"Port: {config['port']}")
    
    try:
        # Tenta conectar
        conn = psycopg2.connect(**config)
        print("\n✅ Conexão bem-sucedida!")
        
        # Obtém informações do servidor
        with conn.cursor() as cur:
            # Versão do PostgreSQL
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"\n📋 Versão do PostgreSQL: {version}")
            
            # Lista os bancos de dados
            cur.execute("""
                SELECT datname 
                FROM pg_database 
                WHERE datistemplate = false
                ORDER BY datname;
            """)
            
            dbs = cur.fetchall()
            print("\n📊 Bancos de dados disponíveis:")
            for db in dbs:
                print(f"- {db[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao conectar ao PostgreSQL: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
    input("\nPressione Enter para sair...")
