"""
Script para redefinir a senha do usuário postgres no PostgreSQL.
"""
import os
import subprocess
import sys
import getpass

def main():
    print("🔑 Redefinição de senha do PostgreSQL")
    print("=" * 50)
    
    # Solicita a senha atual (se houver)
    current_password = getpass.getpass("Digite a senha atual do usuário postgres (pressione Enter se não houver): ")
    
    # Solicita a nova senha
    while True:
        new_password = getpass.getpass("Digite a nova senha para o usuário postgres: ")
        confirm_password = getpass.getpass("Confirme a nova senha: ")
        
        if new_password == confirm_password:
            break
        print("❌ As senhas não coincidem. Tente novamente.")
    
    print("\n🔧 Configurando a nova senha...")
    
    try:
        # Configura o comando psql para alterar a senha
        cmd = [
            'psql',
            '-h', 'localhost',
            '-p', '5432',
            '-U', 'postgres',
            '-d', 'postgres',
            '-c', f'ALTER USER postgres WITH PASSWORD \'{new_password}\';'
        ]
        
        # Configura o ambiente com a senha atual (se fornecida)
        env = os.environ.copy()
        if current_password:
            env["PGPASSWORD"] = current_password
        
        # Executa o comando
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            print("\n✅ Senha alterada com sucesso!")
            
            # Atualiza o arquivo .env com a nova senha
            update_env_file(new_password)
            
            return True
        else:
            print("\n❌ Falha ao alterar a senha:")
            if result.stderr:
                print(f"   Erro: {result.stderr.strip()}")
            print("\nPossíveis soluções:")
            print("1. Verifique se o PostgreSQL está em execução")
            print("2. Verifique se a senha atual está correta")
            print("3. Tente executar como administrador")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return False

def update_env_file(new_password):
    """Atualiza o arquivo .env com a nova senha do PostgreSQL."""
    env_file = ".env"
    
    try:
        # Verifica se o arquivo .env existe
        if not os.path.exists(env_file):
            print(f"⚠️ Arquivo {env_file} não encontrado. Crie um arquivo .env com as configurações do banco de dados.")
            return False
        
        # Lê o conteúdo atual do arquivo
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Atualiza a linha da senha ou adiciona uma nova
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('DB_PASSWORD='):
                lines[i] = f'DB_PASSWORD={new_password}\n'
                updated = True
                break
        
        # Se não encontrou a linha, adiciona
        if not updated:
            lines.append(f'DB_PASSWORD={new_password}\n')
        
        # Faz backup do arquivo atual
        import shutil
        shutil.copy2(env_file, f"{env_file}.backup")
        
        # Escreve as alterações
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ Arquivo {env_file} atualizado com a nova senha.")
        print(f"   Backup salvo como {env_file}.backup")
        return True
        
    except Exception as e:
        print(f"⚠️ Não foi possível atualizar o arquivo {env_file}: {e}")
        return False

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
