# scripts/update_requirements.py
"""
Script para atualizar os requisitos do projeto.
Este script atualiza o arquivo requirements.txt com as dependências necessárias,
incluindo aquelas relacionadas à segurança.
"""
import os
import sys
import subprocess
import pkg_resources
from datetime import datetime

# Lista de pacotes básicos necessários para o projeto
REQUIRED_PACKAGES = [
    # Flask e extensões
    "flask>=2.3.3",
    "flask-wtf>=1.1.1",
    "flask-login>=0.6.2",
    "flask-migrate>=4.0.5",
    "flask-sqlalchemy>=3.1.1",
    "flask-session>=0.5.0",
    "flask-talisman>=1.0.0",  # Para segurança CSP
    "flask-limiter>=3.5.0",   # Para limitar requisições
    
    # Pacotes para segurança
    "cryptography>=41.0.4",
    "bcrypt>=4.0.1",
    "pyopenssl>=23.2.0",
    "email-validator>=2.0.0",
    
    # Pacotes para banco de dados
    "sqlalchemy>=2.0.21",
    "alembic>=1.12.0",
    
    # Pacotes para processamento de dados
    "pandas>=2.1.1",
    "numpy>=1.26.0",
    "matplotlib>=3.8.0",
    
    # Pacotes para PDF
    "reportlab>=4.0.5",
    "weasyprint>=60.1",
    
    # Utilidades
    "python-dotenv>=1.0.0",
    "click>=8.1.7",
    "itsdangerous>=2.1.2",
    "werkzeug>=2.3.7",
    "jinja2>=3.1.2",
    "markupsafe>=2.1.3",
    "pyyaml>=6.0.1",
    
    # Para testes
    "pytest>=7.4.2",
    "pytest-cov>=4.1.0",
    "coverage>=7.3.2",
]

def check_venv():
    """Verifica se o script está sendo executado em um ambiente virtual."""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def update_requirements():
    """Atualiza o arquivo requirements.txt com as dependências necessárias."""
    if not check_venv():
        print("AVISO: Este script deve ser executado dentro de um ambiente virtual.")
        choice = input("Deseja continuar mesmo assim? (s/n): ")
        if choice.lower() != 's':
            print("Operação cancelada.")
            return
    
    # Diretório do projeto
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    req_file = os.path.join(project_dir, "requirements.txt")
    
    # Backup do arquivo atual se existir
    if os.path.exists(req_file):
        backup_file = f"{req_file}.bak-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        try:
            with open(req_file, 'r') as src, open(backup_file, 'w') as dst:
                dst.write(src.read())
            print(f"Backup criado: {backup_file}")
        except Exception as e:
            print(f"Erro ao criar backup: {e}")
    
    # Instalar pacotes necessários
    print("Instalando pacotes necessários...")
    for package in REQUIRED_PACKAGES:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL)
            print(f"✓ {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Erro ao instalar {package}")
    
    # Gerar requirements.txt
    print("\nGerando arquivo requirements.txt...")
    try:
        installed_packages = [f"{dist.project_name}=={dist.version}" for dist in pkg_resources.working_set]
        with open(req_file, 'w') as f:
            f.write("# Sistema de Avaliação DISC - Requirements\n")
            f.write(f"# Gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for package in sorted(installed_packages):
                f.write(f"{package}\n")
        print(f"Arquivo requirements.txt gerado com sucesso: {req_file}")
    except Exception as e:
        print(f"Erro ao gerar requirements.txt: {e}")

def main():
    """Função principal."""
    print("=========================================")
    print("Atualização de Requisitos do Projeto DISC")
    print("=========================================")
    update_requirements()
    print("\nProcesso concluído!")

if __name__ == "__main__":
    main()