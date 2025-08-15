"""
Script para verificar as dependências necessárias para a API FastAPI.
"""
import sys
import subprocess
import pkg_resources

def check_python_version():
    """Verifica a versão do Python."""
    print("\n🔍 Verificando versão do Python...")
    print(f"Versão do Python: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Versão do Python inferior a 3.8. Por favor, atualize o Python.")
        return False
    print("✅ Versão do Python compatível.")
    return True

def check_package(package_name, min_version=None):
    """Verifica se um pacote está instalado e na versão correta."""
    try:
        version = pkg_resources.get_distribution(package_name).version
        if min_version and pkg_resources.parse_version(version) < pkg_resources.parse_version(min_version):
            print(f"⚠️  {package_name} está na versão {version}, mas a versão mínima recomendada é {min_version}")
            return False
        print(f"✅ {package_name} {version} está instalado.")
        return True
    except pkg_resources.DistributionNotFound:
        print(f"❌ {package_name} não está instalado.")
        return False

def install_package(package_name, min_version=None):
    """Instala um pacote usando pip."""
    print(f"\n📦 Instalando {package_name}...")
    try:
        if min_version:
            package_spec = f"{package_name}>={min_version}"
        else:
            package_spec = package_name
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_spec])
        print(f"✅ {package_name} instalado com sucesso.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Falha ao instalar {package_name}: {e}")
        return False

def check_database_connection():
    """Verifica a conexão com o banco de dados."""
    print("\n🔍 Verificando conexão com o banco de dados...")
    try:
        from Coleta_de_dados.database.config import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        print("✅ Conexão com o banco de dados bem-sucedida.")
        return True
    except Exception as e:
        print(f"❌ Falha na conexão com o banco de dados: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

def main():
    """Função principal para verificar as dependências."""
    print("🔍 Iniciando verificação de dependências...")
    
    # Verifica a versão do Python
    if not check_python_version():
        print("\n❌ Por favor, atualize o Python para a versão 3.8 ou superior.")
        return False
    
    # Lista de pacotes necessários com versões mínimas
    required_packages = [
        ("fastapi", "0.68.0"),
        ("uvicorn", "0.15.0"),
        ("sqlalchemy", "1.4.0"),
        ("psycopg2-binary", "2.9.0"),
        ("pydantic", "1.8.0"),
        ("python-multipart", "0.0.5"),
        ("python-jose", "3.3.0"),
        ("passlib", "1.7.4"),
        ("python-dotenv", "0.19.0"),
        ("requests", "2.26.0"),
        ("beautifulsoup4", "4.10.0"),
        ("alembic", "1.7.0"),
        ("pytest", "6.2.5"),
    ]
    
    # Verifica os pacotes necessários
    missing_packages = []
    for package, version in required_packages:
        if not check_package(package, version):
            missing_packages.append((package, version))
    
    # Instala os pacotes ausentes
    if missing_packages:
        print("\n📦 Instalando pacotes ausentes...")
        for package, version in missing_packages:
            install_package(package, version)
    else:
        print("\n✅ Todos os pacotes necessários estão instalados.")
    
    # Verifica a conexão com o banco de dados
    check_database_connection()
    
    print("\n🔍 Verificação de dependências concluída.")
    return True

if __name__ == "__main__":
    main()
