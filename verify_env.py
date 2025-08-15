"""
Script para verificar a integridade do arquivo .env
"""
import os

def check_env_file():
    required_vars = [
        'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
        'DB_ROOT_USER', 'DB_ROOT_PASSWORD', 'DEBUG', 'ENVIRONMENT',
        'SECRET_KEY', 'ALGORITHM', 'ACCESS_TOKEN_EXPIRE_MINUTES',
        'API_RELOAD', 'API_HOST', 'API_PORT', 'FBREF_BASE_URL',
        'API_RATE_LIMIT', 'API_RATE_LIMIT_PERIOD'
    ]
    
    if not os.path.exists('.env'):
        print("❌ Arquivo .env não encontrado!")
        return False
    
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se há caracteres não-ASCII ou problemas de encoding
        try:
            content.encode('ascii')
        except UnicodeEncodeError:
            print("⚠️  Aviso: O arquivo .env contém caracteres não-ASCII")
        
        # Verificar linhas vazias no meio do arquivo
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        for i in range(1, len(lines)):
            if not lines[i].startswith('#') and '=' not in lines[i]:
                print(f"⚠️  Aviso: Linha {i+1} parece estar corrompida: {lines[i][:50]}...")
        
        # Verificar variáveis obrigatórias
        env_vars = {}
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        
        missing_vars = [var for var in required_vars if var not in env_vars]
        if missing_vars:
            print(f"❌ Variáveis obrigatórias faltando: {', '.join(missing_vars)}")
        else:
            print("✅ Todas as variáveis obrigatórias estão presentes")
        
        # Verificar valores vazios
        empty_vars = [key for key, value in env_vars.items() if not value]
        if empty_vars:
            print(f"⚠️  Aviso: Variáveis com valores vazios: {', '.join(empty_vars)}")
        
        # Mostrar estatísticas
        print(f"\n📊 Estatísticas do arquivo .env:")
        print(f"- Total de linhas: {len(content.split('\n'))}")
        print(f"- Linhas não vazias: {len(lines)}")
        print(f"- Variáveis definidas: {len(env_vars)}")
        print(f"- Seções: {len([l for l in content.split('\n') if l.startswith('#') and ':' in l])}")
        
        return len(missing_vars) == 0
        
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo .env: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando integridade do arquivo .env...\n")
    success = check_env_file()
    if success:
        print("\n✅ Verificação concluída com sucesso!")
    else:
        print("\n❌ Foram encontrados problemas no arquivo .env")
