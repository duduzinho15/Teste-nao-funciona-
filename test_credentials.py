#!/usr/bin/env python3
"""
Script para testar várias combinações de credenciais do PostgreSQL
"""
import psycopg2
from psycopg2 import sql
import os
from itertools import product

# Configurações de teste
HOSTS = ['localhost', '127.0.0.1']
PORTS = [5432, 5433]
DB_NAMES = ['postgres', 'apostapro_db', 'template1']
USERS = ['postgres', 'apostapro_user', 'postgres_user']
PASSWORDS = ['postgres', 'senha_segura_123', 'password', '']

def test_connection(host, port, dbname, user, password):
    """Testa uma combinação de credenciais"""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        
        # Se chegou aqui, a conexão foi bem-sucedida
        print(f"✅ Conexão bem-sucedida!")
        print(f"   Host: {host}")
        print(f"   Porta: {port}")
        print(f"   Banco: {dbname}")
        print(f"   Usuário: {user}")
        print(f"   Senha: {'*' * len(password) if password else '(vazio)'}")
        
        # Verifica se é superusuário
        with conn.cursor() as cur:
            cur.execute("SELECT current_user, current_database(), version();")
            user, db, version = cur.fetchone()
            print(f"   Usuário atual: {user}")
            print(f"   Banco atual: {db}")
            print(f"   Versão: {version.split(',')[0]}")
            
            # Verifica se é superusuário
            cur.execute("SELECT usesuper FROM pg_user WHERE usename = current_user;")
            is_superuser = cur.fetchone()[0]
            print(f"   Superusuário: {'Sim' if is_superuser else 'Não'}")
            
            # Lista bancos de dados
            print("\n📋 Bancos de dados:")
            cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
            for db in cur.fetchall():
                print(f"   - {db[0]}")
            
            # Lista usuários
            print("\n👥 Usuários:")
            cur.execute("SELECT usename, usesuper FROM pg_user;")
            for user, is_super in cur.fetchall():
                print(f"   - {user} {'(super)' if is_super else ''}")
            
        conn.close()
        return True
        
    except Exception as e:
        # Ignora falhas de conexão
        return False

def main():
    print("🔍 Testando combinações de credenciais do PostgreSQL...")
    print("Isso pode levar alguns segundos...\n")
    
    # Testa combinações comuns primeiro
    common_combinations = [
        # Formato: (host, port, dbname, user, password)
        ('localhost', 5432, 'postgres', 'postgres', 'postgres'),
        ('localhost', 5432, 'postgres', 'postgres', 'password'),
        ('localhost', 5432, 'postgres', 'postgres', ''),
        ('localhost', 5432, 'apostapro_db', 'apostapro_user', 'senha_segura_123'),
        ('127.0.0.1', 5432, 'postgres', 'postgres', 'postgres'),
    ]
    
    found = False
    
    # Testa combinações comuns primeiro
    for combo in common_combinations:
        host, port, dbname, user, pwd = combo
        print(f"Testando: {user}@{host}:{port}/{dbname}...")
        if test_connection(host, port, dbname, user, pwd):
            found = True
            break
    
    # Se não encontrou, testa todas as combinações possíveis
    if not found:
        print("\n🔍 Nenhuma combinação comum funcionou. Testando todas as possibilidades...")
        for host, port, dbname, user, pwd in product(HOSTS, PORTS, DB_NAMES, USERS, PASSWORDS):
            if test_connection(host, port, dbname, user, pwd):
                found = True
                break
    
    if not found:
        print("\n❌ Nenhuma combinação de credenciais funcionou.")
        print("\nSugestões:")
        print("1. Verifique se o serviço PostgreSQL está em execução")
        print("2. Confirme a porta correta do PostgreSQL (geralmente 5432)")
        print("3. Verifique o arquivo pg_hba.conf para as configurações de autenticação")
        print("4. Tente reiniciar o serviço PostgreSQL")
        print("5. Verifique se o usuário tem permissões adequadas")

if __name__ == "__main__":
    main()
