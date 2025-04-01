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

# --- Importação das Rotas ---
# Importar ANTES da factory `create_app` se a factory precisar delas imediatamente
# ou se elas não dependerem da instância `app`.
# Se as rotas precisarem da instância `app` (comum com Blueprints), importe DENTRO da factory.
# Neste caso, o Blueprint `main_bp` é importado, então podemos fazer aqui.
try:
    # Tentar import relativo primeiro (padrão dentro de um pacote)
    from .routes import main_bp
    logging.info("Importação relativa de 'backend.routes.main_bp' bem-sucedida.")
except ImportError as e_rel:
    logging.warning(f"Falha na importação relativa de routes (.routes): {e_rel}. Tentando absoluta...")
    try:
        # Fallback para import absoluto (pode funcionar dependendo de como é executado)
        from routes import main_bp
        logging.info("Importação absoluta de 'routes.main_bp' bem-sucedida (fallback).")
    except ImportError as e_abs:
         # Se nem relativo nem absoluto funcionarem, é um erro crítico
         logging.critical(f"Falha fatal ao importar 'main_bp' de routes (relativo e absoluto falharam). Verifique a estrutura e PYTHONPATH. Erro: {e_abs}")
         # Usar sys.exit() aqui é apropriado, pois a app não pode funcionar sem rotas.
         # Não usar pytest.exit() aqui.
         sys.exit(f"Erro Crítico: Não foi possível importar as rotas necessárias (main_bp). Detalhes: {e_abs}")
# -----------------------------

# Context Processor para o Ano Atual (mantido)
def inject_current_year():
    """Injeta o ano atual no contexto dos templates."""
    return {'current_year': datetime.now().year}

# --- Factory Function para criar a App ---
# Definir a factory DEPOIS das importações essenciais como `main_bp`
def create_app(testing=False):
    """Cria e configura uma instância da aplicação Flask."""
    # REMOVIDO: `from backend.app import create_app` - Esta era a causa da importação circular.

    app = Flask(__name__,
                static_folder='static',
                template_folder='templates',
                static_url_path='/static') # URL base para arquivos estáticos

    # Lê FLASK_ENV do ambiente, default 'development'
    flask_env = os.environ.get('FLASK_ENV', 'development').lower()
    logging.info(f"Ambiente inicial detectado/definido como: '{flask_env}'. Parâmetro testing={testing}")

    # --- CARREGAMENTO DE CONFIGURAÇÃO ---

    if testing:
        # Aplicação direta da configuração de teste
        logging.info("Aplicando configuração de TESTE diretamente na factory.")
        app.config.update(
            TESTING=True,
            DEBUG=False,
            ENV='testing',
            SECRET_KEY=os.environ.get('FLASK_TEST_SECRET_KEY', 'test-secret-fallback'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('TEST_DATABASE_URL', 'sqlite:///:memory:'),
            SERVER_NAME='localhost.localdomain:5000', # Essencial para pytest-flask
            WTF_CSRF_ENABLED=False,
            SESSION_COOKIE_SECURE=False,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        app.config['ENV'] = 'testing'  # Define explicitamente o ambiente interno

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
                # Tenta carregar a classe de configuração específica do módulo
                app.config.from_object(f'{dev_config_module}.{dev_config_class}')
                logging.info(f"Configuração de DESENVOLVIMENTO carregada de {dev_config_module}.{dev_config_class}.")
                config_loaded_from_file = True
            except (ImportError, AttributeError) as e:
                 logging.warning(f"Falha ao carregar {dev_config_module}.{dev_config_class} (Erro: {e}). Verificando fallbacks.")
            except Exception as e:
                 logging.error(f"Erro inesperado ao carregar config de desenvolvimento: {e}. Verificando fallbacks.")
        else:
            logging.warning(f"Arquivo {config_py_path} não encontrado.")

        # Aplica fallbacks SE a configuração do arquivo falhar OU se o arquivo não existir
        if not config_loaded_from_file:
            logging.warning("Usando configurações padrão de DESENVOLVIMENTO (fallbacks).")
            # Usar os valores do .env como prioridade nos fallbacks
            app.config.setdefault('DEBUG', os.environ.get('FLASK_DEBUG', '1') == '1') # '1' para True
            app.config.setdefault('ENV', 'development') # Já definido pelo FLASK_ENV, mas seguro colocar
            app.config.setdefault('SECRET_KEY', os.environ.get('FLASK_SECRET_KEY', 'dev-secret-fallback-in-app')) # Usa do .env se disponível
            # Usa DATABASE_URL do .env se disponível, senão um fallback final
            # CORREÇÃO: Usar dev_sdisc.db como fallback se DATABASE_URL não estiver no .env
            db_path_fallback = os.path.join(project_root_dir, 'instance', 'dev_sdisc.db')
            os.makedirs(os.path.dirname(db_path_fallback), exist_ok=True)
            app.config.setdefault('SQLALCHEMY_DATABASE_URI', os.environ.get('DATABASE_URL', f'sqlite:///{db_path_fallback}'))
            # Define SERVER_NAME usando .env ou fallback
            app.config.setdefault('SERVER_NAME', os.environ.get('FLASK_SERVER_NAME', '127.0.0.1:5000'))

        # Garante que estes tenham um valor, mesmo que a config.py exista mas não os defina
        app.config.setdefault('DEBUG', True)
        app.config.setdefault('TESTING', False)
        app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)


    # --- Configurações Pós-Carregamento (Garantir valores essenciais) ---
    # Garante que SECRET_KEY tem um valor (mesmo que config/env falhe)
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = secrets.token_hex(16)
        logging.warning("Nenhuma SECRET_KEY definida via config ou env. Usando chave temporária gerada.")

    # Garante que DATABASE_URL tem um valor
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        fallback_db_name = 'final_fallback.db'
        fallback_db_path_full = os.path.join(project_root_dir, 'instance', fallback_db_name)
        os.makedirs(os.path.dirname(fallback_db_path_full), exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{fallback_db_path_full}'
        logging.warning(f"Nenhuma URI de DB definida via config ou env. Usando fallback final: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Garante que SERVER_NAME tem um valor para o bloco __main__
    if not app.config.get('SERVER_NAME'):
        app.config['SERVER_NAME'] = '127.0.0.1:5000'
        logging.warning(f"Nenhum SERVER_NAME definido via config ou env. Usando fallback final: {app.config['SERVER_NAME']}")


    # --- Inicializar Extensões ---
    # (Mantenha comentado se não usar SQLAlchemy diretamente aqui)
    # try:
    #     from .db import db
    #     db.init_app(app)
    #     logging.info("Extensão SQLAlchemy inicializada.")
    # except ImportError:
    #     logging.warning("Arquivo backend/db.py não encontrado. SQLAlchemy não inicializado.")
    # except Exception as e:
    #     logging.error(f"Erro ao inicializar SQLAlchemy: {e}")

    # --- Registrar Blueprints, Context Processors, Error Handlers ---
    app.context_processor(inject_current_year)

    # >>> CORREÇÃO APLICADA AQUI PARA O ERRO 'hasattr' <<<
    # Adiciona a função 'hasattr' ao ambiente global do Jinja para ser usada nos templates
    app.jinja_env.globals['hasattr'] = hasattr
    logging.info("Função 'hasattr' adicionada ao ambiente global do Jinja.")
    # >>> FIM DA CORREÇÃO <<<

    # Configurar CORS
    # Simplificado: permite tudo em dev/test, revisar para produção
    if app.config.get('ENV') in ['development', 'testing'] or app.config.get('DEBUG'):
        CORS(app)
        logging.info(f"CORS configurado para {app.config.get('ENV', 'desconhecido')} (permitindo todas as origens).")
    else: # Produção
        # TODO: Configurar origens permitidas explicitamente em produção
        CORS(app) # Temporário: permite tudo - REVISAR PARA PRODUÇÃO!
        logging.warning("CORS configurado para produção PERMITINDO TODAS AS ORIGENS. ISSO É INSEGURO!")

    # Registrar o Blueprint principal (que foi importado no início do arquivo)
    try:
        app.register_blueprint(main_bp)
        logging.info("Blueprint 'main_bp' registrado.")
    except Exception as e:
        # Usar sys.exit aqui também é válido se o blueprint for essencial
        logging.critical(f"Falha ao registrar o blueprint 'main_bp': {e}")
        sys.exit(f"Erro Crítico: Falha ao registrar blueprint principal: {e}")

    # Rota Favicon
    @app.route('/favicon.ico')
    def favicon():
        try:
            return send_from_directory(
                os.path.join(app.root_path, 'static', 'images'),
                'favicon.ico',
                mimetype='image/vnd.microsoft.icon'
            )
        except FileNotFoundError:
            logging.warning("Arquivo favicon.ico não encontrado em static/images.")
            return "Not Found", 404
        except Exception as e:
            logging.error(f"Erro ao servir favicon.ico: {e}")
            return "Internal Server Error", 500

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        logging.info(f"Rota não encontrada (404): {request.path}")
        # Tenta renderizar um template, senão retorna HTML simples
        try:
            # Certifique-se que a pasta 'errors' existe em 'templates'
            return render_template('errors/404.html'), 404
        except Exception:
             logging.exception("Template errors/404.html não encontrado ou erro ao renderizar.")
             return "<h1>404 Not Found</h1><p>A página que você procura não existe.</p>", 404

    @app.errorhandler(500)
    def internal_error(error):
        # Loga a exceção original que causou o 500
        logging.exception(f"Erro interno do servidor (500) na rota {request.path}.")
        # Tenta renderizar um template customizado, senão retorna HTML simples
        try:
             # Certifique-se que a pasta 'errors' existe em 'templates'
            return render_template('errors/500.html'), 500
        except Exception:
            logging.exception("Template errors/500.html não encontrado ou erro ao renderizar fallback.")
            return "<h1>500 Internal Server Error</h1><p>Ocorreu um erro inesperado no servidor.</p>", 500

    # Log final da criação
    final_env = 'testing' if app.config.get('TESTING') else app.config.get('ENV', 'development')
    logging.info(f"Criação da aplicação Flask ('{app.name}') concluída para o ambiente '{final_env}'.")
    logging.info(f"Debug mode: {app.config.get('DEBUG')}")
    logging.info(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}") # Log do DB URI
    logging.info(f"Server Name: {app.config.get('SERVER_NAME')}") # Log do Server Name
    return app

# --- Ponto de Entrada Principal (para execução direta) ---
if __name__ == '__main__':
    # Cria a app usando a factory, SEM flag testing (usará config dev/prod)
    app_instance = create_app(testing=False)
    is_debug = app_instance.config.get('DEBUG', False) # Pega o valor de DEBUG da config final
    effective_host = '0.0.0.0' # Default para acesso externo
    port = 5000 # Default

    try:
        # Pega o valor da config, pode ser None ou vazio
        raw_server_name = app_instance.config.get('SERVER_NAME')

        # Garante que temos uma string padrão se raw_server_name for None ou vazio
        server_name = raw_server_name if raw_server_name else '127.0.0.1:5000'
        logging.info(f"Processando SERVER_NAME: {server_name!r}") # Log para ver o valor final

        # Agora processa a string server_name (que garantidamente não é None nem vazia)
        if ':' in server_name:
            host_from_config, port_str_from_config = server_name.rsplit(':', 1) # Divide no último ':'
            # Valida o host (não pode ser vazio)
            if host_from_config:
                 # Usa 0.0.0.0 para acesso externo se o host configurado for localhost/127.0.0.1 ou vazio
                effective_host = '0.0.0.0' if host_from_config in ['localhost', '127.0.0.1', ''] else host_from_config
            else:
                logging.warning(f"Host vazio em SERVER_NAME ('{server_name}'). Usando host padrão {effective_host}.")

            # Tenta converter a porta para inteiro
            try:
                port = int(port_str_from_config) # type: ignore[arg-type] # Mantém ignore, pois Pylance pode reclamar
            except ValueError:
                 logging.warning(f"Porta inválida em SERVER_NAME ('{port_str_from_config}'). Usando porta padrão {port}.")
                 # Mantém o host já definido
        else:
            # Se não tiver ':', assume que é só o host e usa porta padrão
            host_from_config = server_name
            # Usa 0.0.0.0 para acesso externo se o host configurado for localhost/127.0.0.1 ou vazio
            effective_host = '0.0.0.0' if host_from_config in ['localhost', '127.0.0.1', ''] else host_from_config
            # Porta padrão já é 5000
            logging.info(f"SERVER_NAME ('{server_name}') não especificou porta. Usando porta padrão {port}.")

    except Exception as e: # Captura erros genéricos ao processar server_name
        logging.exception(f"Erro ao processar SERVER_NAME '{app_instance.config.get('SERVER_NAME')}': {e}. Usando padrões {effective_host}:{port}.")
        # Mantém os defaults definidos no início do bloco try

    logging.info(f"Iniciando servidor Flask diretamente (Debug: {is_debug}) em http://{effective_host}:{port}/")
    try:
        # Usa debug=is_debug para refletir a config carregada
        app_instance.run(host=effective_host, port=port, debug=is_debug) # type: ignore[arg-type] # Mantém ignore
    except OSError as e:
         # Erro comum: porta já em uso
         if "address already in use" in str(e).lower() or "somente uma utilização de cada endereço" in str(e).lower(): # Adicionado check em português
              logging.error(f"ERRO FATAL: A porta {port} já está em uso por outro processo.")
              logging.error("Verifique se outra instância do servidor está rodando ou se outro programa está usando esta porta.")
         else:
             logging.error(f"Erro de sistema ao iniciar o servidor Flask em {effective_host}:{port}. Erro: {e}")
    except Exception as e:
         logging.exception(f"Erro inesperado ao iniciar o servidor Flask: {e}")

# --- Fim do Arquivo ---