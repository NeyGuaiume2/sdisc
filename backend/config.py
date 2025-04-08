# --- START OF FILE config.py ---

# backend/config.py
import os
import secrets
from dotenv import load_dotenv

# Determina o diretório base do projeto
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Carrega variáveis de .env na raiz do projeto (IMPORTANTE: FAZER ISSO PRIMEIRO)
load_dotenv(os.path.join(basedir, '.env'))

# Determina o diretório 'instance' na raiz do projeto
instance_dir = os.path.join(basedir, 'instance')

# --- CORREÇÃO PYLANCE: Pré-calcular o caminho do DB de desenvolvimento ---
# Isso ajuda o Pylance a ter certeza de que estamos usando uma string no os.path.join abaixo
_DEV_DB_PATH = os.path.join(instance_dir, "dev.db")
# ----------------------------------------------------------------------

class BaseConfig:
    """Configuração base da qual as outras herdam."""
    SECRET_KEY = os.environ.get('SECRET_KEY') # Lê do ambiente (pode ser None)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

class DevelopmentConfig(BaseConfig):
    """Configuração para o ambiente de desenvolvimento local."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False # Geralmente não se usa HTTPS localmente
    REMEMBER_COOKIE_SECURE = False

    # --- CORREÇÃO PYLANCE: Usa o caminho pré-calculado ---
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{_DEV_DB_PATH}'
    # ----------------------------------------------------

    # Gera chave temporária se não estiver no .env
    if not BaseConfig.SECRET_KEY:
        print("AVISO: SECRET_KEY não definida no ambiente/'.env'. Gerando chave temporária para desenvolvimento.")
        SECRET_KEY = secrets.token_hex(16) # Sobrescreve o None da BaseConfig


class TestingConfig(BaseConfig):
    """Configuração para o ambiente de testes."""
    TESTING = True
    SECRET_KEY = 'testing-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(BaseConfig):
    """Configuração para o ambiente de produção (Render)."""
    # DEBUG e TESTING já são False pela BaseConfig
    # SESSION/REMEMBER cookies já são secure/httponly pela BaseConfig

    # Apenas lê a URL do banco de dados. A verificação será feita em create_app.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # A SECRET_KEY é herdada da BaseConfig. A verificação será feita em create_app.


# Mapeamento para carregar a configuração correta em create_app
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# --- FIM DO FILE config.py ---