# tests/e2e/test_home.py
import pytest
from playwright.sync_api import Page, expect # Importa Page e expect

# A fixture 'page' é fornecida automaticamente pelo pytest-playwright
def test_homepage_loads_and_has_correct_title(page: Page, live_server_url):
    """
    Verifica se a página inicial carrega e tem o título esperado.
    Usa a fixture live_server_url para obter a URL base da aplicação em execução.
    """
    print(f"Attempting to navigate to: {live_server_url}") # Log para depuração
    page.goto(live_server_url)

    # Verifica se o título da página contém o texto esperado
    # 'expect' oferece asserções mais robustas e com melhor feedback
    expect(page).to_have_title("Início - Sistema de Avaliação DISC")

    # Você também pode verificar a presença de elementos ou texto
    # Localiza o elemento H1 principal
    main_heading = page.locator("h1").first # Pega o primeiro h1 encontrado
    expect(main_heading).to_be_visible()
    expect(main_heading).to_have_text("Sistema de Avaliação DISC")

    # Verifica se o botão "Iniciar Avaliação" existe
    start_button = page.locator("a#start-btn") # Localiza pelo seletor CSS (<a> com id 'start-btn')
    expect(start_button).to_be_visible()
    expect(start_button).to_have_text("Iniciar Avaliação Agora!")
    print(f"Test test_homepage_loads_and_has_correct_title completed successfully.")

def test_navigation_to_quiz_page(page: Page, live_server_url):
    """
    Testa a navegação da home para a página do quiz.
    """
    print(f"Attempting to navigate to: {live_server_url}")
    page.goto(live_server_url)

    # Encontra o link/botão "Iniciar Avaliação Agora!" e clica nele
    start_button = page.locator("a#start-btn")
    expect(start_button).to_be_visible()
    start_button.click()

    # Espera que a URL mude para conter '/quiz' (ou a URL exata se preferir)
    expect(page).to_have_url(f"{live_server_url}/quiz") # Verifica a URL completa

    # Verifica se um elemento chave da página do quiz está presente
    quiz_heading = page.locator("h1").first
    expect(quiz_heading).to_have_text("Avaliação de Perfil Comportamental DISC")
    print(f"Test test_navigation_to_quiz_page completed successfully.")

# Você pode adicionar mais funções de teste neste arquivo ou criar outros arquivos
# como test_quiz.py, test_results.py dentro de tests/e2e/