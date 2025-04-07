# backend/config.py
import os
import secrets

# Determina o diretório base do projeto (um nível acima de 'backend')
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Determina o diretório de dados dentro de 'backend'
backend_data_dir = os.path.join(os.path.dirname(__file__), 'data')
# Determina o diretório 'instance' na raiz do projeto
instance_dir = os.path.join(basedir, 'instance')


class BaseConfig:
    """Configuração base da qual as outras herdam."""
    # Secret Key: Lida primariamente pelo app.py a partir de env var ou .env
    # Não definimos um valor aqui para forçar o uso de env var ou fallback seguro do app.py
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') # app.py tem fallback melhor

    # Configurações gerais
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Caminho para a pasta de dados brutos (ex: assessments.json)
    # Assumindo que está em backend/data/
    DATA_DIR = backend_data_dir

    # URI do Banco de Dados: Também lida primariamente pelo app.py a partir de DATABASE_URL
    # Não definimos um valor aqui, app.py proverá o fallback se DATABASE_URL não existir
    # SQLALCHEMY_DATABASE_URI = None


class DevelopmentConfig(BaseConfig):
    """Configuração para o ambiente de desenvolvimento."""
    DEBUG = True
    # Exemplo: Definir um fallback SQLite *específico para desenvolvimento*
    # Este será usado pelo app.py SOMENTE SE DATABASE_URL não estiver no .env/ambiente
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(instance_dir, "dev.db")}'
    # Nota: Se você definir DATABASE_URL no seu .env, ele terá prioridade sobre esta linha.

    # Poderia adicionar aqui outras configs de dev, como servidor de email de debug, etc.
    # Ex: MAIL_SERVER = 'localhost'
    # Ex: MAIL_PORT = 1025


class TestingConfig(BaseConfig):
    """Configuração para o ambiente de testes."""
    TESTING = True
    DEBUG = False # Frequentemente útil ter debug=False em testes para simular prod
    # Use uma chave secreta fixa e simples para testes
    SECRET_KEY = 'testing-secret-key'
    # Use um banco de dados em memória para testes rápidos e isolados
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Desabilitar CSRF em formulários durante testes (se usar WTForms)
    # WTF_CSRF_ENABLED = False


# Classe de Produção (opcional aqui, já que usamos prod_config.py)
# class ProductionConfig(BaseConfig):
#     """Configuração para o ambiente de produção."""
#     # DEBUG e TESTING já são False por padrão na BaseConfig
#     # Configurações de produção virão de prod_config.py e variáveis de ambiente
#     pass

# Mapeamento para facilitar (opcional)
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    # 'production': ProductionConfig, # Descomente se quiser carregar via from_object também
    'default': DevelopmentConfig
}