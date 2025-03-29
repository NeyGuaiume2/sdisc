import sys
import os

# Adicionar o diretório do backend ao path
project_root = os.path.abspath(os.path.dirname(__file__))
backend_root = os.path.abspath(os.path.join(project_root, '..', 'backend'))
sys.path.insert(0, project_root)
sys.path.insert(0, backend_root)

# Resto do arquivo permanece igual ao original
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import json
import hashlib
from datetime import datetime

# Importação absoluta corrigida
from score_calculator import calculate_disc_scores, get_profile_summary, generate_detailed_report
from backend.routes import main_bp


def create_app(testing=False):
    app = Flask(__name__, 
                static_folder='static', 
                static_url_path='/static')
    CORS(app)  # Habilita CORS para todas as rotas
    app.register_blueprint(main_bp) # Registre o Blueprint

    # Rota específica para favicon
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, 'static', 'images'), 
            'favicon.ico', 
            mimetype='image/vnd.microsoft.icon'
        )
    return app


# Instância da aplicação para execução direta
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)