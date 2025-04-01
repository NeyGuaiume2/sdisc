# tests/conftest.py
import pytest
import os
import sys
import logging
import socket
import threading
import time
from urllib.parse import urlparse

# Adiciona diretórios ao path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: [conftest] %(message)s')

# Tenta importar a factory create_app
try:
    from backend.app import create_app
    logging.info("backend.app.create_app importado com sucesso em conftest.py")
except ImportError as e:
    logging.critical(f"ERRO CRÍTICO em conftest.py: Não foi possível importar 'create_app' de backend.app. Erro: {e}")
    pytest.exit(f"Falha ao importar create_app: {e}", returncode=1)
except Exception as e_gen:
    logging.critical(f"ERRO GERAL em conftest.py durante a importação: {e_gen}")
    pytest.exit(f"Erro inesperado ao importar create_app: {e_gen}", returncode=1)

# Tenta importar waitress
try:
    from waitress import serve
    logging.info("Waitress importado com sucesso.")
except ImportError:
    logging.critical("ERRO CRÍTICO: Waitress não está instalado. Execute 'pip install waitress'")
    pytest.exit("Dependência Waitress não encontrada.", returncode=1)


@pytest.fixture(scope='session')
def app():
    """
    Fixture de sessão para criar uma instância da aplicação Flask para testes.
    """
    logging.info("Criando instância da app Flask para testes (scope='session')...")
    flask_app = create_app(testing=True)
    context = flask_app.app_context()
    context.push()
    logging.info("Contexto da aplicação Flask (session) criado e ativado.")
    yield flask_app
    context.pop()
    logging.info("Contexto da aplicação Flask (session) desativado.")


# Variável global simples para controlar o servidor
_server_thread = None
_server_should_stop = False
_server_started = False

def find_free_port():
    """Encontra uma porta TCP livre no host local."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def is_port_in_use(port, host='127.0.0.1'):
    """Verifica se uma porta está em uso."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def run_waitress(flask_app, host, port):
    """Função alvo para a thread do servidor Waitress."""
    global _server_should_stop, _server_started
    _server_should_stop = False
    logging.info(f"Iniciando Waitress na thread {threading.current_thread().name} em http://{host}:{port}")
    try:
        _server_started = True
        serve(flask_app, host=host, port=port, threads=4, _quiet=True)
    except Exception as e:
        if not _server_should_stop:
            logging.error(f"Erro no servidor Waitress: {e}", exc_info=True)
    finally:
        _server_started = False
        logging.info(f"Servidor Waitress em http://{host}:{port} encerrado.")


def wait_for_server(url, timeout=5):
    """Espera até que o servidor esteja respondendo no URL especificado."""
    import requests
    from requests.exceptions import RequestException
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code < 500:  # Aceita qualquer resposta não-5xx
                logging.info(f"Servidor respondendo em {url}")
                return True
        except RequestException:
            pass
        
        time.sleep(0.1)
    
    logging.warning(f"Timeout aguardando servidor em {url}")
    return False


@pytest.fixture(scope="session")
def live_server_url(app):
    """
    Fixture que inicia o servidor Flask (usando Waitress) em uma thread separada
    e retorna a URL base.
    """
    global _server_thread, _server_should_stop, _server_started

    host = "127.0.0.1"
    port = find_free_port()
    base_url = f"http://{host}:{port}"

    logging.info(f"Porta livre encontrada: {port}. Iniciando servidor Waitress...")

    # Cria e inicia a thread do servidor
    _server_thread = threading.Thread(
        target=run_waitress,
        args=(app, host, port),
        daemon=True,
        name=f"WaitressThread-{port}"
    )
    _server_thread.start()

    # Espera o servidor iniciar
    max_wait = 10  # segundos
    wait_interval = 0.1
    waited = 0
    
    while not _server_started and waited < max_wait:
        time.sleep(wait_interval)
        waited += wait_interval
    
    if not _server_started:
        pytest.fail(f"Servidor não iniciou dentro de {max_wait} segundos")
    
    # Verifica se o servidor está respondendo
    if not wait_for_server(base_url, timeout=5):
        pytest.fail(f"Servidor iniciou mas não está respondendo em {base_url}")

    logging.info(f"Servidor Waitress iniciado e respondendo em {base_url}")

    yield base_url

    # Cleanup
    logging.info(f"Sessão de teste concluída. Sinalizando parada para Waitress em {base_url}...")
    _server_should_stop = True


# Fixtures específicas para Playwright
@pytest.fixture(scope="function")
def browser_context_args(browser_context_args):
    """
    Fixture para configurar argumentos do contexto do navegador Playwright.
    Esta fixture é reaproveitada do pytest-playwright e estendida.
    """
    return {
        **browser_context_args,
        "viewport": {
            "width": 1280,
            "height": 720,
        },
        "ignore_https_errors": True,
        # Adicionar outros argumentos conforme necessário
    }


@pytest.fixture(scope="function")
def page_with_retry(page, request):
    """
    Fixture que adiciona tentativas de retry às ações do Playwright.
    Útil para operações que podem falhar por problemas de timing.
    """
    # Aqui você pode implementar lógica de retry personalizada
    # ou simplesmente retornar a page normal
    yield page


# Hook para configurar informações adicionais nos relatórios de teste
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    # Se houver falha, podemos adicionar informações extras ao relatório
    if report.when == "call" and report.failed:
        logging.error(f"Teste falhou: {item.name}")
        
        # Se os fixtures de page do Playwright estiverem disponíveis, podemos capturar screenshot
        page = None
        for fixture_name in ["page", "page_with_retry"]:
            if fixture_name in item.fixturenames:
                try:
                    page = item.funcargs[fixture_name]
                    break
                except:
                    continue
        
        if page:
            try:
                screenshot_dir = os.path.join(project_root, "tests", "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                
                screenshot_path = os.path.join(
                    screenshot_dir, 
                    f"{item.name}_{time.strftime('%Y%m%d-%H%M%S')}.png"
                )
                
                page.screenshot(path=screenshot_path)
                logging.info(f"Screenshot capturado em: {screenshot_path}")
            except Exception as e:
                logging.error(f"Falha ao capturar screenshot: {e}")