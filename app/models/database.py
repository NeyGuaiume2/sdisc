from flask_sqlalchemy import SQLAlchemy

# Inicializa o objeto de banco de dados
db = SQLAlchemy()

def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas definidas
    """
    db.create_all()
