# backend/app.py

import sys
import os
# --- IMPORTAR load_dotenv PRIMEIRO ---
from dotenv import load_dotenv
# ------------------------------------
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import json
import hashlib
from datetime import datetime
import secrets
import logging

# --- CARREGAR VARIÁVEIS DE AMBIENTE DO ARQUIVO .env ---
# Determina o caminho para a raiz do projeto (um nível acima de backend/)
project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(project_root_dir, '.env')

# Verifica se o arquivo .env existe antes de tentar carregar
if os.path.exists(dotenv_path):
    # Carrega as variáveis. override=True faz com que .env sobrescreva vars já existentes no ambiente.
    load_dotenv(dotenv_path=dotenv_path, override=True)
    print(f"INFO: Variáveis de ambiente carregadas de: {dotenv_path}") # Use print aqui pois logging pode não estar config ainda
else:
    print(f"WARN: Arquivo .env não encontrado em {dotenv_path}. Variáveis de ambiente não carregadas a partir dele.")
# ----------------------------------------------------

# --- Configurar logging básico ---
# Fazer isso *depois* de carregar .env, caso .env defina algo sobre logging no futuro
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
# ---------------------------------

# Adicionar o diretório do backend ao path (pode não ser estritamente necessário com imports relativos)
# project_root_backend = os.path.abspath(os.path.dirname(__file__))
# sys.path.insert(0, project_root_backend)

# Importação relativa das rotas (preferível)
try:
    from .routes import main_bp
except ImportError as e:
    logging.error(f"Falha na importação relativa de routes: {e}. Tentando absoluta.")
    try:
        from routes import main_bp
    except ImportError as e2:
         logging.critical(f"Falha fatal ao importar 'routes'. Verifique a estrutura e PYTHONPATH. Erro: {e2}")
         sys.exit("Erro: Não foi possível importar as rotas.") # Sair se não puder importar rotas

# Context Processor para o Ano Atual (mantido)
def inject_current_year():
    """Injeta o ano atual no contexto dos templates."""
    return {'current_year': datetime.now().year}

# --- Factory Function para criar a App ---
def create_app(testing=False):
    """Cria e configura uma instância da aplicação Flask."""

    # __name__ é o nome do módulo atual (app)
    # static_folder e template_folder relativos a este arquivo (backend/)
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates',
                static_url_path='/static') # URL base para arquivos estáticos

    # --- CARREGAMENTO DE CONFIGURAÇÃO BASEADO NO AMBIENTE ---
    # Lê FLASK_ENV do ambiente (que pode ter sido definido pelo .env)
    # Default para 'development' se não definido
    flask_env = os.environ.get('FLASK_ENV', 'development').lower()
    logging.info(f"FLASK_ENV detectado/definido como: '{flask_env}'")

    if testing:
        try:
            # Tenta carregar de uma classe de configuração em backend/config.py
            app.config.from_object('backend.config.TestingConfig')
            logging.info("Carregando configuração de TESTE de backend.config.TestingConfig.")
        except ImportError:
             logging.warning("backend.config.TestingConfig não encontrado. Use config básica.")
             app.config['TESTING'] = True
             app.config['SECRET_KEY'] = 'test-secret-fallback' # Chave básica para testes
             app.config['DEBUG'] = False # Geralmente debug é false em testes
             app.config['DATABASE_URI'] = 'sqlite:///:memory:' # DB em memória para testes
        except Exception as e:
             logging.error(f"Erro ao carregar TestingConfig: {e}")

    elif flask_env == 'production':
        prod_config_path = os.path.join(project_root_dir, 'prod_config.py')
        try:
            # Carrega do arquivo prod_config.py na raiz do projeto
            # silent=False fará Flask reclamar se o arquivo não existir
            app.config.from_pyfile(prod_config_path, silent=False)
            logging.info(f"Carregando configuração de PRODUÇÃO de {prod_config_path}.")
        except FileNotFoundError:
            logging.error(f"ERRO CRÍTICO: Arquivo de configuração de produção ({prod_config_path}) não encontrado!")
            # A aplicação pode não funcionar corretamente sem config de produção
        except Exception as e:
             logging.error(f"Erro ao carregar prod_config.py: {e}")

        # Garante que DEBUG e TESTING estejam desligados em produção
        app.config['DEBUG'] = False
        app.config['TESTING'] = False

    else: # development (ou qualquer outro valor não 'production'/'testing')
        try:
             # Carrega de backend/config.py (assumindo que existe classe DevelopmentConfig)
            app.config.from_object('backend.config.DevelopmentConfig')
            logging.info("Carregando configuração de DESENVOLVIMENTO de backend.config.DevelopmentConfig.")
        except ImportError:
             logging.warning("backend.config.DevelopmentConfig não encontrado. Usando padrões de desenvolvimento.")
             # Define padrões razoáveis para desenvolvimento se config.py não existir
             app.config['DEBUG'] = True
             app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-fallback') # Lê do .env ou usa fallback
             db_path = os.path.join(project_root_dir, 'instance', 'dev_fallback.db')
             os.makedirs(os.path.dirname(db_path), exist_ok=True)
             app.config['DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}') # Lê do .env ou usa fallback
        except Exception as e:
             logging.error(f"Erro ao carregar DevelopmentConfig: {e}")
        # Garante modo debug em desenvolvimento se não especificado no arquivo
        app.config.setdefault('DEBUG', True)
        app.config.setdefault('TESTING', False) # Garante testing=False

    # --- Configuração da Secret Key (Prioriza Variável de Ambiente) ---
    # Tenta carregar da variável de ambiente PRIMEIRO (pode vir do .env ou do sistema)
    env_secret_key = os.environ.get('FLASK_SECRET_KEY')
    if env_secret_key:
        app.config['SECRET_KEY'] = env_secret_key
        logging.info("SECRET_KEY carregada da variável de ambiente (ou .env).")
    elif not app.config.get('SECRET_KEY'):
        # Se não veio do arquivo de config E não veio do ambiente (.env ou sistema)
        app.config['SECRET_KEY'] = secrets.token_hex(16) # Gera uma temporária
        if flask_env == 'production':
             # Isso é um problema sério em produção!
             logging.critical("ALERTA DE SEGURANÇA: Nenhuma SECRET_KEY definida via arquivo ou variável de ambiente em PRODUÇÃO! Usando chave temporária insegura.")
        else:
             logging.warning("Nenhuma SECRET_KEY definida via config ou env. Usando chave temporária para desenvolvimento.")
    # ----------------------------------------------------------------

    # --- Configuração do Banco de Dados (Prioriza Variável de Ambiente DATABASE_URL) ---
    # Adapte 'SQLALCHEMY_DATABASE_URI' se sua extensão de DB usar outra chave
    db_config_key = 'SQLALCHEMY_DATABASE_URI' # Chave padrão para Flask-SQLAlchemy
    env_db_url = os.environ.get('DATABASE_URL')

    if env_db_url:
        app.config[db_config_key] = env_db_url
        logging.info(f"{db_config_key} carregada da variável de ambiente DATABASE_URL (ou .env).")
    elif not app.config.get(db_config_key):
        # Define um fallback se não veio do arquivo de config NEM do ambiente
        fallback_db_name = 'prod_fallback.db' if flask_env == 'production' else 'dev_fallback.db'
        fallback_db_path = os.path.join(project_root_dir, 'instance', fallback_db_name)
        os.makedirs(os.path.dirname(fallback_db_path), exist_ok=True) # Cria pasta instance
        app.config[db_config_key] = f'sqlite:///{fallback_db_path}'
        logging.warning(f"Nenhuma DATABASE_URL (ou {db_config_key} na config) definida. Usando fallback SQLite em: {fallback_db_path}")

    # Boa prática para SQLAlchemy
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    # ----------------------------------------------------------------------

    # --- Inicializar Extensões (Exemplo com SQLAlchemy, ajuste conforme necessário) ---
    # try:
    #     from .db import db # Supondo que você tenha backend/db.py
    #     db.init_app(app)
    #     logging.info("Extensão SQLAlchemy inicializada.")
    #     # Criar tabelas se necessário (geralmente feito com Flask-Migrate ou comando separado)
    #     # with app.app_context():
    #     #     db.create_all()
    # except ImportError:
    #     logging.warning("Arquivo backend/db.py não encontrado. SQLAlchemy não inicializado.")
    # except Exception as e:
    #     logging.error(f"Erro ao inicializar SQLAlchemy: {e}")
    # ---------------------------------------------------------------------------------


    # Registrar o context processor para o ano
    app.context_processor(inject_current_year)

    # Configurar CORS (Considere origens específicas para produção)
    if flask_env == 'production':
         # Exemplo: permitir apenas seu domínio frontend
         # allowed_origins = ["https://seudominiofrontend.com", "https://www.seudominiofrontend.com"]
         # CORS(app, origins=allowed_origins, supports_credentials=True)
         CORS(app) # Temporário: permite tudo em prod, ajuste depois!
         logging.info("CORS configurado para produção (TODO: restringir origens).")
    else:
         CORS(app) # Permite tudo em desenvolvimento
         logging.info("CORS configurado para desenvolvimento (permitindo todas as origens).")


    # Registrar o Blueprint das rotas
    app.register_blueprint(main_bp)
    logging.info("Blueprint 'main_bp' registrado.")

    # --- Rotas Específicas da App (como favicon) ---
    @app.route('/favicon.ico')
    def favicon():
        # app.root_path é o diretório 'backend' neste caso
        # os.path.join vai para backend/static/images
        return send_from_directory(
            os.path.join(app.root_path, 'static', 'images'),
            'favicon.ico',
            mimetype='image/vnd.microsoft.icon'
        )

    # --- Error Handlers ---
    @app.errorhandler(404)
    def not_found_error(error):
        # Tenta renderizar um template customizado
        try:
            return render_template('errors/404.html'), 404 # Ex: templates/errors/404.html
        except Exception:
             # Fallback simples se o template falhar
             return "<h1>404 Not Found</h1><p>A página que você procura não existe.</p>", 404

    @app.errorhandler(500)
    def internal_error(error):
        # Loga a exceção completa para depuração
        logging.exception("Erro interno do servidor (500) não tratado.")
        # Tenta renderizar um template customizado
        try:
            # Não passe o 'error' diretamente para o template em produção por segurança
            return render_template('errors/500.html'), 500 # Ex: templates/errors/500.html
        except Exception:
            # Fallback simples se o template falhar
            return "<h1>500 Internal Server Error</h1><p>Ocorreu um erro inesperado.</p>", 500

    logging.info("Criação da aplicação Flask concluída.")
    return app

# --- Ponto de Entrada Principal ---
# Verifica se o script está sendo executado diretamente
if __name__ == '__main__':
    # Cria a aplicação usando a factory
    app = create_app()
    # Obtém configurações da app já carregada
    is_debug = app.config.get('DEBUG', False) # Default False se não definido
    # Tenta obter a porta da config ou do ambiente, default 5000
    port = int(os.environ.get('PORT', app.config.get('PORT', 5000)))

    logging.info(f"Iniciando servidor Flask diretamente (Debug: {is_debug}) na porta {port}...")
    # app.run() é adequado para desenvolvimento, NÃO use para produção.
    # Use host='0.0.0.0' para ser acessível na rede local.
    app.run(host='0.0.0.0', port=port, debug=is_debug)

else:
    # Se importado por um servidor WSGI (como Gunicorn ou uWSGI em produção)
    # O servidor procurará por uma variável 'app' ou chamará create_app()
    # Apenas cria a instância da app para o servidor WSGI usar
    logging.info("Script importado, criando instância 'app' para servidor WSGI...")
    app = create_app()
# --- Fim do Arquivo ---