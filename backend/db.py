"""
Configuração do banco de dados para a aplicação DISC.
"""

from flask_sqlalchemy import SQLAlchemy

# Inicializa a extensão SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """
    Inicializa o banco de dados com a aplicação Flask
    
    Args:
        app: Instância da aplicação Flask
    """
    # Configuração do SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///disc_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializa o banco de dados com a aplicação
    db.init_app(app)
    
    # Cria todas as tabelas se não existirem
    with app.app_context():
        db.create_all()
        
    return db