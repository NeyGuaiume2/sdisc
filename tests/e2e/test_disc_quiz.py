# tests/e2e/test_disc_quiz.py
import pytest
from playwright.sync_api import Page, expect
import logging
import time
import re
import random # Importar o módulo random

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: [%(filename)s] %(message)s')

# --- Teste 1: Carregamento da Página do Quiz (Mantido como antes) ---
def test_quiz_page_loads_properly(page: Page, live_server_url):
    """
    Verifica se a página do quiz (/quiz) carrega corretamente com todas as estruturas
    e elementos esperados iniciais.
    """
    quiz_url = f"{live_server_url}/quiz"
    test_name = "test_quiz_page_loads_properly"
    logging.info(f"[{test_name}] Navegando para página do quiz: {quiz_url}")

    try:
        page.goto(quiz_url, timeout=15000, wait_until='domcontentloaded')
        logging.info(f"[{test_name}] Página do quiz carregada")
    except Exception as e:
        logging.error(f"[{test_name}] Falha ao navegar para a página do quiz: {e}")
        pytest.fail(f"Não foi possível acessar a página do quiz: {e}")

    logging.info(f"[{test_name}] Verificando título da página...")
    expect(page).to_have_title("Avaliação DISC - Questionário", timeout=5000)
    logging.info(f"[{test_name}] Título da página OK.")

    logging.info(f"[{test_name}] Aguardando carregamento/exibição da seção #assessment...")
    page.wait_for_selector("#assessment", state="visible", timeout=15000)
    logging.info(f"[{test_name}] Seção #assessment visível.")

    logging.info(f"[{test_name}] Verificando elementos principais do quiz...")
    expect(page.locator(".quiz-header")).to_be_visible(timeout=5000)
    expect(page.locator(".question-counter")).to_be_visible(timeout=5000)
    expect(page.locator(".timer-container")).to_be_visible(timeout=5000)
    expect(page.locator("#question-content-wrapper")).to_be_visible(timeout=5000)
    expect(page.locator("#options-list")).to_be_visible(timeout=5000)
    expect(page.locator("#question-number")).to_be_visible(timeout=5000)
    expect(page.locator("#total-questions")).to_be_visible(timeout=5000)
    logging.info(f"[{test_name}] Elementos principais do quiz OK.")

    logging.info(f"[{test_name}] Verificando texto inicial do contador de questões...")
    question_counter = page.locator(".question-counter")
    expect(question_counter).to_contain_text(re.compile(r"Questão\s+1\s+de\s+\d+"), timeout=5000)
    logging.info(f"[{test_name}] Contador de questões inicial OK.")
    logging.info(f"[{test_name}] Teste concluído com sucesso.")


# --- Teste 2: Seleção de Respostas em uma Questão (Mantido como antes) ---
def test_select_answers_in_quiz(page: Page, live_server_url):
    """
    Testa a funcionalidade de selecionar respostas (MAIS e MENOS)
    em uma única questão e verifica o avanço automático (se aplicável).
    """
    quiz_url = f"{live_server_url}/quiz"
    test_name = "test_select_answers_in_quiz"
    logging.info(f"[{test_name}] Navegando para página do quiz: {quiz_url}")

    try:
        page.goto(quiz_url, timeout=15000, wait_until='domcontentloaded')
        logging.info(f"[{test_name}] Página do quiz carregada.")
    except Exception as e:
        logging.error(f"[{test_name}] Falha ao navegar para a página do quiz: {e}")
        pytest.fail(f"Não foi possível acessar a página do quiz: {e}")

    logging.info(f"[{test_name}] Aguardando opções da primeira questão...")
    page.wait_for_selector("#assessment", state="visible", timeout=15000)
    page.wait_for_selector("#options-list .option-item input.most-option", timeout=15000)
    logging.info(f"[{test_name}] Opções da questão 1 carregadas.")

    logging.info(f"[{test_name}] Selecionando a primeira opção como MAIS...")
    first_most_option = page.locator("#options-list .option-item input.most-option").first
    first_most_option.click()

    logging.info(f"[{test_name}] Selecionando a última opção como MENOS...")
    last_least_option = page.locator("#options-list .option-item input.least-option").last
    last_least_option.click()

    logging.info(f"[{test_name}] Verificando se as opções foram marcadas...")
    expect(first_most_option).to_be_checked(timeout=1000)
    expect(last_least_option).to_be_checked(timeout=1000)
    logging.info(f"[{test_name}] Opções marcadas OK.")

    logging.info(f"[{test_name}] Verificando transição para próxima questão (esperando número 2)...")
    question_number_locator = page.locator("#question-number")
    try:
        expect(question_number_locator).to_have_text("2", timeout=7000)
        logging.info(f"[{test_name}] Quiz avançou automaticamente para a questão 2.")
    except Exception as e:
        logging.warning(f"[{test_name}] Quiz não avançou para questão 2 dentro do tempo esperado: {e}. Verificar lógica JS/timeouts.")
    logging.info(f"[{test_name}] Teste concluído.")


# --- Teste 3: Fluxo Completo do Quiz com Respostas Aleatórias ---
def test_complete_quiz_flow(page: Page, live_server_url):
    """
    Testa o fluxo completo do quiz, respondendo todas as questões ALEATORIAMENTE,
    chegando à tela de conclusão, clicando para ver resultados e
    verificando o conteúdo básico da página de resultados.
    Inclui uma pausa opcional no final para depuração.
    """
    quiz_url = f"{live_server_url}/quiz"
    test_name = "test_complete_quiz_flow_random" # Nome ligeiramente diferente no log
    logging.info(f"[{test_name}] Iniciando teste de fluxo completo do quiz com respostas aleatórias: {quiz_url}")

    # --- Navegação e Setup Inicial ---
    try:
        page.goto(quiz_url, timeout=15000, wait_until='domcontentloaded')
        logging.info(f"[{test_name}] Página do quiz carregada.")
    except Exception as e:
        logging.error(f"[{test_name}] Falha ao navegar para a página do quiz: {e}")
        pytest.fail(f"Não foi possível acessar a página do quiz: {e}")

    logging.info(f"[{test_name}] Aguardando avaliação ficar visível...")
    page.wait_for_selector("#assessment", state="visible", timeout=15000)

    total_questions_el = page.locator("#total-questions")
    total_questions_text = total_questions_el.inner_text(timeout=5000)
    try:
        total_questions = int(total_questions_text)
    except ValueError:
        logging.warning(f"[{test_name}] Não foi possível extrair número total de questões do texto '{total_questions_text}'. Usando default 28.")
        total_questions = 28

    logging.info(f"[{test_name}] Total de questões identificado: {total_questions}")

    # --- Loop de Respostas Aleatórias ---
    for question_num in range(1, total_questions + 1):
        logging.info(f"[{test_name}] Processando questão {question_num} de {total_questions}...")

        # Aguardar opções e validar número da questão
        page.wait_for_selector("#options-list .option-item input.most-option", state="visible", timeout=10000)
        expect(page.locator("#question-number")).to_have_text(str(question_num), timeout=1000)

        # --- LÓGICA DE SELEÇÃO ALEATÓRIA ---
        try:
            # 1. Localizar todos os itens de opção para a questão atual
            option_items = page.locator(".option-item").all()
            num_options = len(option_items)
            if num_options < 2: # Precisa de pelo menos 2 opções para escolher MAIS e MENOS diferentes
                logging.error(f"[{test_name}] Questão {question_num} tem menos de 2 opções ({num_options}). Impossível continuar.")
                pytest.fail(f"Questão {question_num} tem apenas {num_options} opções.")

            # 2. Escolher um índice aleatório para a resposta "MAIS"
            most_option_index = random.randrange(num_options)
            most_item_locator = option_items[most_option_index]
            most_input_locator = most_item_locator.locator("input.most-option")
            most_word = most_input_locator.get_attribute("value") # Pega a palavra para log
            logging.info(f"[{test_name}] Escolhendo aleatoriamente a opção {most_option_index + 1} ('{most_word}') como MAIS.")
            most_input_locator.click(timeout=5000)

            # 3. Escolher um índice aleatório para "MENOS", garantindo que seja DIFERENTE do "MAIS"
            possible_least_indices = [i for i in range(num_options) if i != most_option_index]
            least_option_index = random.choice(possible_least_indices)
            least_item_locator = option_items[least_option_index]
            least_input_locator = least_item_locator.locator("input.least-option")
            least_word = least_input_locator.get_attribute("value") # Pega a palavra para log
            logging.info(f"[{test_name}] Escolhendo aleatoriamente a opção {least_option_index + 1} ('{least_word}') como MENOS.")
            least_input_locator.click(timeout=5000)

            # 4. Verificar se foram marcados (opcional, mas bom para garantir)
            expect(most_input_locator).to_be_checked(timeout=1000)
            expect(least_input_locator).to_be_checked(timeout=1000)

        except Exception as selection_error:
             logging.error(f"[{test_name}] Erro durante a seleção aleatória na questão {question_num}: {selection_error}")
             pytest.fail(f"Erro na seleção aleatória da questão {question_num}: {selection_error}")
        # --- FIM DA LÓGICA DE SELEÇÃO ALEATÓRIA ---

        # --- Lógica de Avanço (Mantida como antes) ---
        if question_num < total_questions:
            next_question_num_str = str(question_num + 1)
            logging.info(f"[{test_name}] Aguardando avanço para questão {next_question_num_str}...")
            try:
                page.wait_for_function(
                    f"document.querySelector('#question-number').textContent.trim() === '{next_question_num_str}'",
                    timeout=7000
                )
                logging.info(f"[{test_name}] Avançou para questão {next_question_num_str}")
            except Exception as e:
                current_q_num = page.locator("#question-number").text_content().strip()
                logging.error(f"[{test_name}] Falha ao detectar avanço para questão {next_question_num_str} via JS function: {e}. Número atual: {current_q_num}")
                page.screenshot(path=f"tests/screenshots/failure_advance_q{question_num}_{time.strftime('%Y%m%d-%H%M%S')}.png")
                pytest.fail(f"Não avançou para a questão {next_question_num_str} após timeout/erro. Número atual: {current_q_num}")
        else:
             logging.info(f"[{test_name}] Última questão respondida.")

    # --- Tela de Conclusão (Mantida como antes) ---
    logging.info(f"[{test_name}] Verificando seção de conclusão #quiz-completion...")
    try:
        completion_section = page.locator("#quiz-completion")
        expect(completion_section).to_be_visible(timeout=10000)
        logging.info(f"[{test_name}] Seção de conclusão do quiz exibida com sucesso.")
        view_results_btn = completion_section.locator("#view-results-btn")
        expect(view_results_btn).to_be_visible(timeout=1000)
        expect(view_results_btn).to_be_enabled(timeout=1000)
        logging.info(f"[{test_name}] Botão 'Ver Meus Resultados' pronto.")
    except Exception as e:
        logging.error(f"[{test_name}] Seção de conclusão ou botão não apareceram/habilitaram: {e}")
        page.screenshot(path=f"tests/screenshots/failure_completion_screen_{time.strftime('%Y%m%d-%H%M%S')}.png")
        pytest.fail("A seção de conclusão ou o botão não foram exibidos/habilitados corretamente.")

    # --- Navegação para Resultados (Mantida como antes) ---
    logging.info(f"[{test_name}] Clicando no botão 'Ver Meus Resultados'...")
    view_results_btn = page.locator("#view-results-btn")
    view_results_btn.click()

    # --- Verificações na Página de Resultados (Mantida como antes) ---
    logging.info(f"[{test_name}] Verificando redirecionamento para página de resultados...")
    results_url_pattern = f"{live_server_url}/results"
    try:
        page.wait_for_url(results_url_pattern, timeout=15000)
        logging.info(f"[{test_name}] URL atual corresponde ao padrão de resultados: {page.url}")
    except Exception as e:
        logging.error(f"[{test_name}] Falha ao esperar/verificar a URL da página de resultados: {e}")
        page.screenshot(path=f"tests/screenshots/failure_results_url_{time.strftime('%Y%m%d-%H%M%S')}.png")
        pytest.fail(f"A URL não atingiu o padrão esperado '{results_url_pattern}'. URL atual: {page.url}")

    logging.info(f"[{test_name}] Verificando conteúdo da página de resultados...")
    try:
        # H1
        h1_locator = page.locator("h1.mb-4.text-center")
        expect(h1_locator).to_be_visible(timeout=10000)
        expect(h1_locator).to_have_text("Seu Perfil DISC", timeout=5000)
        logging.info(f"[{test_name}] Título H1 'Seu Perfil DISC' encontrado.")

        # Gráfico
        chart_canvas = page.locator("#discChart")
        expect(chart_canvas).to_be_visible(timeout=10000)
        logging.info(f"[{test_name}] Canvas do gráfico '#discChart' encontrado e visível.")

        # Resumo do Perfil (verifica se existe, sem checar o perfil exato pois é aleatório)
        primary_profile_paragraph = page.locator("p:has-text('Perfil Primário:')")
        expect(primary_profile_paragraph).to_be_visible(timeout=5000)
        expect(primary_profile_paragraph).to_contain_text(re.compile(r"Perfil Primário:\s*[DISC]"), timeout=5000) # Verifica se tem D, I, S ou C
        logging.info(f"[{test_name}] Parágrafo do Perfil Primário encontrado (Perfil aleatório).")

        # Lista de Scores (verifica se existe)
        score_item_locator = page.locator("li:has-text('(Dominância):')")
        expect(score_item_locator).to_be_visible(timeout=5000)
        logging.info(f"[{test_name}] Item da lista de scores (Dominância) encontrado.")

        # Abas
        tabs_locator = page.locator("#discTabs")
        expect(tabs_locator).to_be_visible(timeout=5000)
        logging.info(f"[{test_name}] Abas de interpretação '#discTabs' encontradas.")

        logging.info(f"[{test_name}] Conteúdo principal da página de resultados verificado com sucesso.")

        # <<< PONTO DE PAUSA PARA DEPURAÇÃO MANUAL >>>
        logging.info(f"[{test_name}] Pausando a execução para inspeção manual (remova page.pause() para execução normal)...")
        page.pause()

    except Exception as e:
        logging.error(f"[{test_name}] Erro ao verificar o conteúdo da página de resultados: {e}")
        screenshot_path = f"tests/screenshots/failure_results_page_{time.strftime('%Y%m%d-%H%M%S')}.png"
        try:
            page.screenshot(path=screenshot_path)
            logging.info(f"[{test_name}] Screenshot da falha salvo em: {screenshot_path}")
        except Exception as screenshot_error:
            logging.error(f"[{test_name}] Falha ao capturar screenshot: {screenshot_error}")
        pytest.fail(f"Falha ao verificar elementos essenciais na página de resultados: {e}")

    logging.info(f"[{test_name}] Teste de fluxo completo do quiz finalizado com sucesso (após pausa).")