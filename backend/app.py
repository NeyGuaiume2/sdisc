# --- START OF FILE app.py ---

# backend/app.py

import sys
import os
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime
import secrets # Mantido caso a chave de dev seja gerada em config.py
import logging

# --- Configurar logging básico ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
# ---------------------------------

# --- Importar config e db ---
try:
    from .config import config
    from .db import db
    logging.info("Configurações e instância 'db' importadas de backend.config e backend.db.")
except ImportError as e:
    logging.critical(f"Falha fatal ao importar 'config' ou 'db': {e}. Verifique backend/config.py e backend/db.py.")
    sys.exit(f"Erro Crítico: Não foi possível importar config/db. Detalhes: {e}")
# --- Fim da importação ---

# --- Importação das Rotas ---
try:
    from .routes import main_bp
    logging.info("Importação relativa de 'backend.routes.main_bp' bem-sucedida.")
except ImportError as e:
     logging.critical(f"Falha fatal ao importar 'main_bp' de routes. Erro: {e}")
     sys.exit(f"Erro Crítico: Não foi possível importar as rotas (main_bp). Detalhes: {e}")
# -----------------------------

# Context Processor
def inject_current_year():
    return {'current_year': datetime.now().year}

# --- Factory Function ---
def create_app(config_name=None):
    project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(__name__,
                static_folder='static',       # Garante que app.static_folder seja 'static'
                template_folder='templates',
                static_url_path='/static',
                instance_path=os.path.join(project_root_dir, 'instance'))
    os.makedirs(app.instance_path, exist_ok=True)

    # --- CARREGAMENTO DE CONFIGURAÇÃO CENTRALIZADO ---
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'production') # Padrão 'production'

    if os.getenv('FLASK_ENV') == 'development' and not os.getenv('FLASK_CONFIG'):
           logging.warning("FLASK_CONFIG não definida, usando 'development' baseado em FLASK_ENV.")
           config_name = 'development'

    try:
        app.config.from_object(config[config_name])
        logging.info(f"Configuração '{config_name}' carregada com sucesso de backend.config.")
        logging.debug(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    except KeyError:
         logging.critical(f"ERRO CRÍTICO: Configuração inválida: '{config_name}'. Válidas: {list(config.keys())}")
         sys.exit(f"Erro Crítico: Configuração '{config_name}' não encontrada.")
    except Exception as e:
        logging.critical(f"Erro inesperado ao carregar configuração '{config_name}': {e}")
        sys.exit(f"Erro Crítico: Falha no carregamento da configuração. Detalhes: {e}")
    # --- FIM DO CARREGAMENTO ---

    # --- VERIFICAÇÕES PÓS-CARREGAMENTO ---
    if config_name == 'production':
        if not app.config.get('SECRET_KEY'):
            logging.critical("ERRO CRÍTICO (Produção): SECRET_KEY não definida nas variáveis de ambiente!")
            sys.exit("Erro Crítico: SECRET_KEY de produção faltando.")
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
            logging.critical("ERRO CRÍTICO (Produção): DATABASE_URL não definida nas variáveis de ambiente!")
            sys.exit("Erro Crítico: DATABASE_URL de produção faltando.")
    # --- FIM DAS VERIFICAÇÕES ---

    # --- Inicializar Extensões ---
    try:
        db.init_app(app)
        logging.info("Extensão SQLAlchemy inicializada.")
        with app.app_context():
             try:
                 from .models import disc_result
                 logging.info("Modelos importados dentro do contexto da aplicação para Migrate.")
             except ImportError as e:
                 logging.error(f"Erro ao importar modelos para Flask-Migrate: {e}.")
        migrate = Migrate(app, db)
        logging.info("Extensão Flask-Migrate inicializada.")
    except Exception as e:
        logging.error(f"Erro ao inicializar SQLAlchemy ou Flask-Migrate: {e}")

    # Configurar CORS
    if app.config.get('DEBUG') or app.config.get('TESTING'):
        CORS(app)
        logging.info(f"CORS configurado para '{config_name}' (permitindo todas as origens).")
    else: # Produção
        CORS(app) # Temporário
        logging.warning("CORS configurado para produção PERMITINDO TODAS AS ORIGENS. Configure origens específicas!")

    # --- Registrar Blueprints, Context Processors, Error Handlers ---
    app.context_processor(inject_current_year)
    app.jinja_env.globals['hasattr'] = hasattr

    try:
        app.register_blueprint(main_bp)
        logging.info("Blueprint 'main_bp' registrado.")
    except Exception as e:
        logging.critical(f"Falha ao registrar o blueprint 'main_bp': {e}")
        sys.exit(f"Erro Crítico: Falha ao registrar blueprint principal: {e}")

    # Rota Favicon
    @app.route('/favicon.ico')
    def favicon():
        # --- CORREÇÃO PYLANCE ---
        # Garante que static_folder é uma string antes de usar em os.path.join
        static_folder_path = app.static_folder
        if static_folder_path is None:
             logging.error("Erro crítico: app.static_folder não está definido!")
             # Retorna um erro 500 genérico, pois é um problema de configuração
             return "Internal Server Error", 500

        # Agora Pylance sabe que static_folder_path é uma string
        favicon_dir = os.path.join(static_folder_path, 'images')
        # --- FIM DA CORREÇÃO ---
        try:
            return send_from_directory(
                favicon_dir, # Usa a variável verificada
                'favicon.ico',
                mimetype='image/vnd.microsoft.icon'
            )
        except FileNotFoundError:
            logging.warning(f"Favicon não encontrado em {favicon_dir}.")
            return '', 204
        except Exception as e:
            logging.error(f"Erro ao servir favicon.ico: {e}", exc_info=True)
            return "Internal Server Error", 500

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        logging.info(f"Rota não encontrada (404): {request.path}")
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error='Recurso não encontrado'), 404
        try:
            return render_template('errors/404.html'), 404
        except Exception:
             logging.exception("Template errors/404.html não encontrado ou erro ao renderizar.")
             return "<h1>404 Not Found</h1>", 404

    @app.errorhandler(500)
    def internal_error(error):
        logging.exception(f"Erro interno do servidor (500) na rota {request.path}.")
        try:
            db.session.rollback()
            logging.info("Sessão do banco de dados revertida (rollback) devido a erro 500.")
        except Exception as rollback_err:
            logging.error(f"Erro adicional ao tentar reverter a sessão do banco de dados: {rollback_err}")

        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
             error_message = "Erro interno do servidor."
             if app.config.get('DEBUG'):
                 error_message = str(error)
             return jsonify(error=error_message), 500
        try:
            return render_template('errors/500.html'), 500
        except Exception:
            logging.exception("Template errors/500.html não encontrado ou erro ao renderizar.")
            return "<h1>500 Internal Server Error</h1>", 500

    # Log final da criação
    final_env = config_name
    logging.info(f"Criação da aplicação Flask ('{app.name}') concluída para o ambiente '{final_env}'.")
    logging.info(f"Debug mode: {app.config.get('DEBUG')}")
    logging.info(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    logging.info(f"Instance Path: {app.instance_path}")
    return app

# --- Ponto de Entrada Principal ---
if __name__ == '__main__':
    app_instance = create_app()
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    is_debug = app_instance.config.get('DEBUG', False)

    logging.info(f"Iniciando servidor Flask diretamente (__name__ == '__main__')")
    logging.info(f"Ambiente Config: {app_instance.config.get('ENV', app_instance.config.get('FLASK_ENV', 'desconhecido'))}, Debug: {is_debug}")
    logging.info(f"Rodando em http://{host}:{port}/")

    try:
        app_instance.run(host=host, port=port, debug=is_debug)
    except OSError as e:
         if "address already in use" in str(e).lower() or "somente uma utilização" in str(e).lower():
              logging.error(f"ERRO FATAL: A porta {port} já está em uso.")
         else:
             logging.error(f"Erro de sistema ao iniciar o servidor Flask: {e}", exc_info=True)
         sys.exit(1)
    except Exception as e:
         logging.exception(f"Erro inesperado ao iniciar o servidor Flask diretamente: {e}")
         sys.exit(1)

# --- FIM DO FILE app.py ---