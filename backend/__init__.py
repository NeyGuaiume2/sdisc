from flask import Flask
from backend.routes import main_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_bp)  # Registrar as rotas
    return app
