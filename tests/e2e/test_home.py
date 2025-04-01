# tests/e2e/test_home.py
import pytest
from playwright.sync_api import Page, expect
import logging # Adicionar para log

# Configurar logging básico para o teste também
# (Pode ser redundante se já configurado no conftest, mas não prejudica)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: [test_home] %(message)s')

# Usar a fixture customizada 'live_server_url'
def test_homepage_loads_and_has_correct_title(page: Page, live_server_url):
    """
    Verifica se a página inicial carrega e tem o título esperado.
    Usa a fixture customizada live_server_url com Waitress em thread.
    """
    target_url = live_server_url
    logging.info(f"Tentando navegar para: {target_url}")
    try:
        # Usar wait_until='domcontentloaded' ou 'load' pode ser mais explícito
        page.goto(target_url, timeout=10000, wait_until='domcontentloaded')
        logging.info(f"Navegação para {target_url} concluída.")
    except Exception as e:
         logging.error(f"Falha ao navegar para {target_url}: {e}")
         pytest.fail(f"Não foi possível conectar ao servidor de teste em {target_url}. Erro: {e}")

    logging.info("Verificando título da página...")
    # Usar timeout nas asserções individuais é uma boa prática
    expect(page).to_have_title("Início - Sistema de Avaliação DISC", timeout=5000)
    logging.info("Título da página verificado com sucesso.")

    logging.info("Verificando cabeçalho H1...")
    main_heading = page.locator("h1").first
    expect(main_heading).to_be_visible(timeout=5000)
    expect(main_heading).to_have_text("Sistema de Avaliação DISC")
    logging.info("Cabeçalho H1 verificado com sucesso.")

    logging.info("Verificando botão 'Iniciar Avaliação'...")
    start_button = page.locator("a#start-btn")
    expect(start_button).to_be_visible(timeout=5000)
    expect(start_button).to_have_text("Iniciar Avaliação Agora!")
    logging.info("Botão 'Iniciar Avaliação' verificado com sucesso.")
    logging.info("Teste test_homepage_loads_and_has_correct_title concluído com sucesso.")


# Usar a fixture customizada 'live_server_url'
def test_navigation_to_quiz_page(page: Page, live_server_url):
    """
    Testa a navegação da home para a página do quiz.
    """
    home_url = live_server_url
    logging.info(f"Tentando navegar para: {home_url}")
    try:
        page.goto(home_url, timeout=10000, wait_until='domcontentloaded')
        logging.info(f"Navegação para {home_url} concluída.")
    except Exception as e:
         logging.error(f"Falha ao navegar para {home_url}: {e}")
         pytest.fail(f"Não foi possível conectar ao servidor de teste em {home_url}. Erro: {e}")


    logging.info("Localizando e clicando no botão 'Iniciar Avaliação'...")
    start_button = page.locator("a#start-btn")
    expect(start_button).to_be_visible(timeout=5000)
    # Playwright espera automaticamente que o elemento esteja pronto para clique
    start_button.click()
    logging.info("Botão clicado.")

    quiz_url = f"{live_server_url}/quiz"
    logging.info(f"Esperando URL ser: {quiz_url}")
    # Espera explícita pela URL após o clique
    expect(page).to_have_url(quiz_url, timeout=10000)

    # *** CORREÇÃO APLICADA AQUI ***
    # Acessar page.url como uma propriedade, não como um método
    current_url = page.url
    logging.info(f"URL verificada: {current_url}")
    # ******************************

    logging.info("Verificando cabeçalho H1 da página do quiz...")
    quiz_heading = page.locator("h1").first
    # Esperar visibilidade antes de verificar o texto
    expect(quiz_heading).to_be_visible(timeout=5000)
    expect(quiz_heading).to_have_text("Avaliação de Perfil Comportamental DISC")
    logging.info("Cabeçalho H1 do quiz verificado com sucesso.")
    logging.info("Teste test_navigation_to_quiz_page concluído com sucesso.")