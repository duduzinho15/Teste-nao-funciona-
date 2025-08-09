#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script mínimo para testar conexão com PostgreSQL
"""
import psycopg2
import sys

def main():
    print("=== Teste Mínimo de Conexão PostgreSQL ===\n")
    
    # Configuração de conexão
    config = {
        "host": "localhost",
        "database": "postgres",
        "user": "postgres",
        "password": "@Eduardo123",
        "port": "5432"
    }
    
    print("Tentando conectar com as seguintes configurações:")
    for k, v in config.items():
        print(f"{k}: {v}")
    
    try:
        # Tenta conectar sem especificar encoding
        print("\nTentando conexão sem especificar encoding...")
        conn = psycopg2.connect(**config)
        print("✅ Conexão bem-sucedida sem especificar encoding!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Falha na conexão sem especificar encoding: {e}")
    
    try:
        # Tenta conectar forçando LATIN1
        print("\nTentando conexão forçando LATIN1...")
        conn = psycopg2.connect(
            host=config["host"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
            port=config["port"],
            client_encoding='LATIN1'
        )
        print("✅ Conexão bem-sucedida com LATIN1!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Falha na conexão com LATIN1: {e}")
    
    try:
        # Tenta conectar forçando SQL_ASCII (sem conversão de encoding)
        print("\nTentando conexão forçando SQL_ASCII...")
        conn = psycopg2.connect(
            host=config["host"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
            port=config["port"],
            client_encoding='SQL_ASCII'
        )
        print("✅ Conexão bem-sucedida com SQL_ASCII!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Falha na conexão com SQL_ASCII: {e}")
    
    print("\n❌ Não foi possível estabelecer conexão com nenhum dos métodos testados.")
    return False

if __name__ == "__main__":
    main()
    input("\nPressione Enter para sair...")
