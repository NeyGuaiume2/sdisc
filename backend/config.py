import os

class Config:
    # Configuração básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao'
    
    # Diretório de dados
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    
    # Configurações do SQLite (para futuras implementações)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(DATA_DIR, "disc.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def init_app(app):
        # Criar diretório de dados se não existir
        if not os.path.exists(Config.DATA_DIR):
            os.makedirs(Config.DATA_DIR)# Configurações do banco de dados 
