# wsgi.py

# Importa a função factory que cria a instância da aplicação Flask
from backend.app import create_app
import os

# Cria a instância da aplicação Flask.
# A função create_app deve ser responsável por carregar a configuração
# apropriada (ex: lendo variáveis de ambiente como FLASK_ENV ou DATABASE_URL)
app = create_app()

# REMOVEU-SE O BLOCO if __name__ == "__main__": app.run()