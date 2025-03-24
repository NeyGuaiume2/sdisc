"""
Arquivo de inicialização do pacote backend.
Configura a aplicação Flask e as extensões necessárias.
"""

from flask import Flask
from flask_cors import CORS
from backend.db import init_db, db
import os

def create_app(testing=False):
    """
    Factory de aplicação - cria e configura a aplicação Flask
    
    Args:
        testing: Boolean indicando se a aplicação está em modo de teste
        
    Returns:
        Uma instância configurada da aplicação Flask
    """
    # Inicializa a aplicação Flask
    app = Flask(__name__)
    
    # Habilita CORS para todas as rotas
    CORS(app)
    
    # Configurações do ambiente
    if testing:
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    else:
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-dev')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
            'DATABASE_URL', 'sqlite:///disc_app.db'
        )
    
    # Inicializa o banco de dados
    init_db(app)
    
    # Importa e registra as rotas
    from backend.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app