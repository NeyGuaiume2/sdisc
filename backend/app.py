# backend/app.py

import sys
import os
# --- IMPORTAR load_dotenv PRIMEIRO ---
from dotenv import load_dotenv
# ------------------------------------
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
# >>> ADIÇÃO: Importar Migrate <<<
from flask_migrate import Migrate
import json
import hashlib
from datetime import datetime
import secrets
import logging
# import pytest # REMOVER este import se ele existir acidentalmente

# --- CARREGAR VARIÁVEIS DE AMBIENTE DO ARQUIVO .env ---
# Determina o caminho para a raiz do projeto (um nível acima de backend/)
project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(project_root_dir, '.env')

# Verifica se o arquivo .env existe antes de tentar carregar
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path, override=True)
    # Usar print aqui é seguro antes do logging estar configurado
    print(f"INFO: Variáveis de ambiente carregadas de: {dotenv_path}")
else:
    print(f"WARN: Arquivo .env não encontrado em {dotenv_path}. Variáveis de ambiente não carregadas a partir dele.")
# ----------------------------------------------------

# --- Configurar logging básico ---
# Configurar ANTES de qualquer log ser chamado
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
# ---------------------------------

# >>> ADIÇÃO: Importar db <<<
try:
    from .db import db # Importa a instância db
    logging.info("Instância 'db' (SQLAlchemy) importada de backend.db.")
except ImportError:
    logging.critical("Falha fatal ao importar 'db' de backend.db. Verifique se o arquivo existe e está correto.")
    sys.exit("Erro Crítico: Não foi possível importar a instância 'db' do SQLAlchemy.")
# >>> FIM DA ADIÇÃO <<<

# --- Importação das Rotas ---
try:
    from .routes import main_bp
    logging.info("Importação relativa de 'backend.routes.main_bp' bem-sucedida.")
except ImportError as e_rel:
    logging.warning(f"Falha na importação relativa de routes (.routes): {e_rel}. Tentando absoluta...")
    try:
        from routes import main_bp
        logging.info("Importação absoluta de 'routes.main_bp' bem-sucedida (fallback).")
    except ImportError as e_abs:
         logging.critical(f"Falha fatal ao importar 'main_bp' de routes (relativo e absoluto falharam). Verifique a estrutura e PYTHONPATH. Erro: {e_abs}")
         sys.exit(f"Erro Crítico: Não foi possível importar as rotas necessárias (main_bp). Detalhes: {e_abs}")
# -----------------------------

# Context Processor para o Ano Atual (mantido)
def inject_current_year():
    """Injeta o ano atual no contexto dos templates."""
    return {'current_year': datetime.now().year}

# --- Factory Function para criar a App ---
def create_app(testing=False):
    """Cria e configura uma instância da aplicação Flask."""

    app = Flask(__name__,
                static_folder='static',
                template_folder='templates',
                static_url_path='/static',
                instance_path=os.path.join(project_root_dir, 'instance') # Define o instance_path corretamente
               )
    app.instance_path = os.path.join(project_root_dir, 'instance') # Garante que instance_path está correto
    os.makedirs(app.instance_path, exist_ok=True) # Cria a pasta instance se não existir

    flask_env = os.environ.get('FLASK_ENV', 'development').lower()
    logging.info(f"Ambiente inicial detectado/definido como: '{flask_env}'. Parâmetro testing={testing}")

    # --- CARREGAMENTO DE CONFIGURAÇÃO ---

    if testing:
        logging.info("Aplicando configuração de TESTE diretamente na factory.")
        # >>> CORREÇÃO: Definir instance_path também para testes <<<
        test_instance_path = os.path.join(project_root_dir, 'instance_test') # Pasta separada para testes
        os.makedirs(test_instance_path, exist_ok=True)
        app.instance_path = test_instance_path
        # >>> FIM DA CORREÇÃO <<<
        app.config.update(
            TESTING=True,
            DEBUG=False,
            ENV='testing',
            SECRET_KEY=os.environ.get('FLASK_TEST_SECRET_KEY', 'test-secret-fallback'),
            # >>> CORREÇÃO: Usar um DB de teste no disco se :memory: causar problemas com migrate <<<
            # SQLALCHEMY_DATABASE_URI=os.environ.get('TEST_DATABASE_URL', 'sqlite:///:memory:'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('TEST_DATABASE_URL', f'sqlite:///{os.path.join(test_instance_path, "test.db")}'),
            # >>> FIM DA CORREÇÃO <<<
            SERVER_NAME='localhost.localdomain:5000',
            WTF_CSRF_ENABLED=False,
            SESSION_COOKIE_SECURE=False,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        app.config['ENV'] = 'testing'

    elif flask_env == 'production':
        logging.info("Tentando carregar configuração de PRODUÇÃO.")
        prod_config_path = os.path.join(project_root_dir, 'prod_config.py')
        try:
            app.config.from_pyfile(prod_config_path, silent=False)
            logging.info(f"Configuração de PRODUÇÃO carregada de {prod_config_path}.")
        except FileNotFoundError:
            logging.error(f"ERRO CRÍTICO: Arquivo de configuração de produção ({prod_config_path}) não encontrado!")
        except Exception as e:
             logging.error(f"Erro ao carregar prod_config.py: {e}")
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        app.config['ENV'] = 'production'
        app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    else: # development
        logging.info("Tentando carregar configuração de DESENVOLVIMENTO.")
        dev_config_module = 'backend.config'
        dev_config_class = 'DevelopmentConfig'
        config_py_path = os.path.join(os.path.dirname(__file__), 'config.py')
        config_loaded_from_file = False
        if os.path.exists(config_py_path):
            try:
                app.config.from_object(f'{dev_config_module}.{dev_config_class}')
                logging.info(f"Configuração de DESENVOLVIMENTO carregada de {dev_config_module}.{dev_config_class}.")
                config_loaded_from_file = True
            except (ImportError, AttributeError) as e:
                 logging.warning(f"Falha ao carregar {dev_config_module}.{dev_config_class} (Erro: {e}). Verificando fallbacks.")
            except Exception as e:
                 logging.error(f"Erro inesperado ao carregar config de desenvolvimento: {e}. Verificando fallbacks.")
        else:
            logging.warning(f"Arquivo {config_py_path} não encontrado.")

        if not config_loaded_from_file:
            logging.warning("Usando configurações padrão de DESENVOLVIMENTO (fallbacks).")
            app.config.setdefault('DEBUG', os.environ.get('FLASK_DEBUG', '1') == '1')
            app.config.setdefault('ENV', 'development')
            app.config.setdefault('SECRET_KEY', os.environ.get('FLASK_SECRET_KEY', 'dev-secret-fallback-in-app'))
            # --- Fallback DATABASE_URL ---
            # Usa DATABASE_URL do .env se disponível, senão usa o fallback de config.py (dev.db) ou um último fallback
            dev_db_fallback_path = os.path.join(app.instance_path, "dev.db") # Usa instance_path
            # Verifica se DATABASE_URL está no ambiente E não está vazio
            db_url_from_env = os.environ.get('DATABASE_URL')
            if db_url_from_env:
                app.config.setdefault('SQLALCHEMY_DATABASE_URI', db_url_from_env)
                logging.info(f"Usando DATABASE_URL do ambiente: {db_url_from_env}")
            else:
                 # Se não estiver no env, usa o fallback definido em config.py (se existir na classe)
                 # ou o fallback final (dev.db na instance)
                 fallback_uri = getattr(DevelopmentConfig, 'SQLALCHEMY_DATABASE_URI', f'sqlite:///{dev_db_fallback_path}')
                 app.config.setdefault('SQLALCHEMY_DATABASE_URI', fallback_uri)
                 logging.info(f"Usando fallback para SQLALCHEMY_DATABASE_URI: {fallback_uri}")
            # ------------------------------
            app.config.setdefault('SERVER_NAME', os.environ.get('FLASK_SERVER_NAME', '127.0.0.1:5000'))

        app.config.setdefault('DEBUG', True)
        app.config.setdefault('TESTING', False)
        app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)


    # --- Configurações Pós-Carregamento (Garantir valores essenciais) ---
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = secrets.token_hex(16)
        logging.warning("Nenhuma SECRET_KEY definida via config ou env. Usando chave temporária gerada.")

    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        fallback_db_name = 'final_fallback.db'
        fallback_db_path_full = os.path.join(app.instance_path, fallback_db_name) # Usa instance_path
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{fallback_db_path_full}'
        logging.warning(f"Nenhuma URI de DB definida via config ou env. Usando fallback final: {app.config['SQLALCHEMY_DATABASE_URI']}")

    if not app.config.get('SERVER_NAME'):
        app.config['SERVER_NAME'] = '127.0.0.1:5000'
        logging.warning(f"Nenhum SERVER_NAME definido via config ou env. Usando fallback final: {app.config['SERVER_NAME']}")


    # --- Inicializar Extensões ---
    # >>> DESCOMENTADO E ATIVADO <<<
    try:
        db.init_app(app) # Inicializa SQLAlchemy com a app
        logging.info("Extensão SQLAlchemy inicializada.")
        # >>> ADIÇÃO: Inicializar Flask-Migrate <<<
        # Importar o modelo aqui é necessário para o Migrate reconhecê-lo
        # Faça isso *depois* de db.init_app(app)
        with app.app_context():
             # Importar modelos DENTRO do contexto da aplicação
             # Ajuste o caminho se seus modelos estiverem em outro lugar
             try:
                 from .models import disc_result # Ou from .models.disc_result import DISCResult
                 logging.info("Modelos importados dentro do contexto da aplicação para Migrate.")
             except ImportError as e:
                 logging.error(f"Erro ao importar modelos para Flask-Migrate: {e}. Verifique backend/models/__init__.py e os arquivos de modelo.")
                 # Não necessariamente fatal, mas migrate pode não funcionar corretamente
        migrate = Migrate(app, db) # Inicializa Flask-Migrate
        logging.info("Extensão Flask-Migrate inicializada.")
        # >>> FIM DA ADIÇÃO <<<
    except NameError:
        logging.error("Erro: A variável 'db' não foi importada corretamente antes de db.init_app().")
    except Exception as e:
        logging.error(f"Erro ao inicializar SQLAlchemy ou Flask-Migrate: {e}")
    # >>> FIM DAS MODIFICAÇÕES <<<

    # --- Registrar Blueprints, Context Processors, Error Handlers ---
    app.context_processor(inject_current_year)
    app.jinja_env.globals['hasattr'] = hasattr
    logging.info("Função 'hasattr' adicionada ao ambiente global do Jinja.")

    if app.config.get('ENV') in ['development', 'testing'] or app.config.get('DEBUG'):
        CORS(app)
        logging.info(f"CORS configurado para {app.config.get('ENV', 'desconhecido')} (permitindo todas as origens).")
    else:
        CORS(app) # Temporário: permite tudo - REVISAR PARA PRODUÇÃO!
        logging.warning("CORS configurado para produção PERMITINDO TODAS AS ORIGENS. ISSO É INSEGURO!")

    try:
        app.register_blueprint(main_bp)
        logging.info("Blueprint 'main_bp' registrado.")
    except Exception as e:
        logging.critical(f"Falha ao registrar o blueprint 'main_bp': {e}")
        sys.exit(f"Erro Crítico: Falha ao registrar blueprint principal: {e}")

    # Rota Favicon
    @app.route('/favicon.ico')
    def favicon():
        try:
            return send_from_directory(
                os.path.join(app.static_folder, 'images'), # Usar app.static_folder
                'favicon.ico',
                mimetype='image/vnd.microsoft.icon'
            )
        except FileNotFoundError:
            logging.warning(f"Arquivo favicon.ico não encontrado em {os.path.join(app.static_folder, 'images')}.")
            # Retorna 204 No Content em vez de 404 para evitar erros no console do browser
            return '', 204
        except Exception as e:
            logging.error(f"Erro ao servir favicon.ico: {e}")
            return "Internal Server Error", 500

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        logging.info(f"Rota não encontrada (404): {request.path}")
        try:
            return render_template('errors/404.html'), 404
        except Exception:
             logging.exception("Template errors/404.html não encontrado ou erro ao renderizar.")
             return "<h1>404 Not Found</h1><p>A página que você procura não existe.</p>", 404

    @app.errorhandler(500)
    def internal_error(error):
        # >>> ADIÇÃO: Rollback da sessão do DB em caso de erro 500 <<<
        try:
            db.session.rollback()
            logging.info("Sessão do banco de dados revertida (rollback) devido a erro 500.")
        except Exception as rollback_err:
            logging.error(f"Erro ao tentar reverter a sessão do banco de dados: {rollback_err}")
        # >>> FIM DA ADIÇÃO <<<

        logging.exception(f"Erro interno do servidor (500) na rota {request.path}.")
        try:
            return render_template('errors/500.html'), 500
        except Exception:
            logging.exception("Template errors/500.html não encontrado ou erro ao renderizar fallback.")
            return "<h1>500 Internal Server Error</h1><p>Ocorreu um erro inesperado no servidor.</p>", 500

    # Log final da criação
    final_env = 'testing' if app.config.get('TESTING') else app.config.get('ENV', 'development')
    logging.info(f"Criação da aplicação Flask ('{app.name}') concluída para o ambiente '{final_env}'.")
    logging.info(f"Debug mode: {app.config.get('DEBUG')}")
    logging.info(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    logging.info(f"Server Name: {app.config.get('SERVER_NAME')}")
    logging.info(f"Instance Path: {app.instance_path}") # Log do instance_path
    return app

# --- Ponto de Entrada Principal (para execução direta) ---
if __name__ == '__main__':
    app_instance = create_app(testing=False)
    is_debug = app_instance.config.get('DEBUG', False)
    effective_host = '0.0.0.0'
    port = 5000

    try:
        raw_server_name = app_instance.config.get('SERVER_NAME')
        server_name = raw_server_name if raw_server_name else '127.0.0.1:5000'
        logging.info(f"Processando SERVER_NAME: {server_name!r}")

        if ':' in server_name:
            host_from_config, port_str_from_config = server_name.rsplit(':', 1)
            if host_from_config:
                effective_host = '0.0.0.0' if host_from_config in ['localhost', '127.0.0.1', ''] else host_from_config
            else:
                logging.warning(f"Host vazio em SERVER_NAME ('{server_name}'). Usando host padrão {effective_host}.")
            try:
                port = int(port_str_from_config)
            except ValueError:
                 logging.warning(f"Porta inválida em SERVER_NAME ('{port_str_from_config}'). Usando porta padrão {port}.")
        else:
            host_from_config = server_name
            effective_host = '0.0.0.0' if host_from_config in ['localhost', '127.0.0.1', ''] else host_from_config
            logging.info(f"SERVER_NAME ('{server_name}') não especificou porta. Usando porta padrão {port}.")

    except Exception as e:
        logging.exception(f"Erro ao processar SERVER_NAME '{app_instance.config.get('SERVER_NAME')}': {e}. Usando padrões {effective_host}:{port}.")

    logging.info(f"Iniciando servidor Flask diretamente (Debug: {is_debug}) em http://{effective_host}:{port}/")
    try:
        # Adiciona suporte a comandos Flask CLI (como flask db)
        # Isso geralmente é feito automaticamente, mas garantir que a app_instance
        # esteja disponível no contexto correto é importante.
        # A execução direta com app_instance.run() já disponibiliza isso.
        app_instance.run(host=effective_host, port=port, debug=is_debug)
    except OSError as e:
         if "address already in use" in str(e).lower() or "somente uma utilização de cada endereço" in str(e).lower():
              logging.error(f"ERRO FATAL: A porta {port} já está em uso por outro processo.")
              logging.error("Verifique se outra instância do servidor está rodando ou se outro programa está usando esta porta.")
         else:
             logging.error(f"Erro de sistema ao iniciar o servidor Flask em {effective_host}:{port}. Erro: {e}")
         sys.exit(1) # Sair com código de erro
    except Exception as e:
         logging.exception(f"Erro inesperado ao iniciar o servidor Flask: {e}")
         sys.exit(1) # Sair com código de erro

# --- Fim do Arquivo ---