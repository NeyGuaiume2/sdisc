# tests/e2e/test_basic_quiz_flow.py

import pytest
from playwright.sync_api import Page, expect

# URL base onde sua aplicação Flask estará rodando
# Certifique-se que corresponde à porta que o Flask usa (normalmente 5000)
BASE_URL = "http://127.0.0.1:5000" # Ou a porta configurada/padrão

# Número de questões para responder (só para exemplo, pode ser menor que o total)
# Ajuste se o seu quiz tiver um número diferente de blocos/questões visíveis inicialmente
QUESTIONS_TO_ANSWER = 5 # Responde apenas as 5 primeiras para simplificar

@pytest.mark.e2e # Marca como teste E2E
def test_complete_quiz_and_reach_results(page: Page):
    """
    Testa o fluxo básico: ir para o quiz, responder algumas questões,
    enviar e verificar se a página de resultados é carregada.
    """
    quiz_url = f"{BASE_URL}/quiz"
    results_url_pattern = f"**{BASE_URL}/results" # Padrão para esperar a URL

    # 1. Navegar para a página do quiz
    print(f"Navegando para: {quiz_url}")
    page.goto(quiz_url)

    # 2. Esperar um elemento chave do quiz carregar
    #    ASSUMINDO que cada questão está num div com a classe 'question-block'
    #    e que os inputs de 'mais'/'menos' têm nomes específicos.
    #    *** AJUSTE OS SELETORES ABAIXO CONFORME SEU HTML REAL ***
    try:
        page.wait_for_selector('.question-block', timeout=10000) # Espera até 10s
        print("Página do quiz carregada (encontrou .question-block).")
    except Exception as e:
        pytest.fail(f"Falha ao esperar pelo seletor do quiz '.question-block': {e}")

    # 3. Responder *algumas* questões (apenas para permitir o envio)
    print(f"Respondendo as primeiras {QUESTIONS_TO_ANSWER} questões (exemplo)...")
    # Obter todos os blocos de questão
    question_blocks = page.locator('.question-block').all()

    if not question_blocks:
         pytest.fail("Nenhum bloco de questão (.question-block) encontrado na página.")

    # Itera apenas sobre o número definido de questões
    answered_count = 0
    for i, block in enumerate(question_blocks):
        if i >= QUESTIONS_TO_ANSWER:
            break
        try:
            # ASSUMINDO: Inputs 'mais' têm name='qX_more', 'menos' têm name='qX_less'
            # e cada um tem 4 opções (value='word1', 'word2', etc.)
            # Clica na *primeira* opção de 'mais' e na *segunda* opção de 'menos'
            # *** ESTES SELETORES SÃO CRÍTICOS E PRECISAM CORRESPONDER AO SEU HTML/JS ***

            # Tenta localizar o primeiro radio 'mais' visível dentro do bloco
            more_radios = block.locator("input[type='radio'][name^='q'][name$='_more']")
            first_more_radio = more_radios.first # Pega o primeiro
            expect(first_more_radio).to_be_visible(timeout=2000) # Espera ficar visível
            first_more_radio.check() # Marca a opção 'mais'

            # Tenta localizar o segundo radio 'menos' visível dentro do bloco
            less_radios = block.locator("input[type='radio'][name^='q'][name$='_less']")
            second_less_radio = less_radios.nth(1) # Pega o segundo (índice 1)
            expect(second_less_radio).to_be_visible(timeout=2000) # Espera ficar visível
            second_less_radio.check() # Marca a opção 'menos'

            print(f"Respondeu questão no bloco {i+1}.")
            answered_count += 1
        except Exception as e:
            # Se falhar em uma questão, loga e continua (pode ser que o quiz permita envio parcial)
            print(f"Aviso: Falha ao responder questão no bloco {i+1}: {e}")
            # Poderia usar pytest.fail aqui se todas as respostas forem obrigatórias

    if answered_count < QUESTIONS_TO_ANSWER:
         print(f"Aviso: Conseguiu responder apenas {answered_count} das {QUESTIONS_TO_ANSWER} questões planejadas.")
         # Decida se isso é uma falha ou não dependendo da lógica do seu quiz
         # pytest.fail(f"Não foi possível responder o número mínimo de questões ({answered_count}/{QUESTIONS_TO_ANSWER}).")

    # 4. Encontrar e clicar no botão de submissão
    #    ASSUMINDO que o botão tem id='submit-quiz' ou texto 'Finalizar'
    #    *** AJUSTE O SELETOR CONFORME SEU HTML ***
    submit_button = page.locator("button:has-text('Finalizar'), #submit-quiz").first
    try:
        expect(submit_button).to_be_enabled(timeout=5000) # Espera o botão estar habilitado
        print("Botão de finalizar encontrado e habilitado.")
        submit_button.click()
        print("Clicou em finalizar.")
    except Exception as e:
        pytest.fail(f"Falha ao encontrar/clicar no botão de finalizar: {e}")

    # 5. Esperar pela navegação para a página de resultados
    print(f"Esperando navegação para URL que corresponda a: {results_url_pattern}")
    try:
        # page.wait_for_load_state('networkidle') # Espera a rede ficar ociosa
        page.wait_for_url(results_url_pattern, timeout=15000) # Espera até 15s pela URL
        print(f"Navegou para a página de resultados: {page.url}")
    except Exception as e:
        pytest.fail(f"Falha ao esperar pela URL da página de resultados ({results_url_pattern}): {e}")

    # 6. Verificação Mínima na Página de Resultados
    #    Verifica se um elemento chave da página de resultados está visível
    #    ASSUMINDO que a página de resultados tem um <h1> com "Seu Perfil DISC"
    #    *** AJUSTE O SELETOR E TEXTO CONFORME SEU HTML ***
    results_heading = page.locator("h1:has-text('Seu Perfil DISC')")
    try:
        expect(results_heading).to_be_visible(timeout=5000)
        print("Verificação mínima da página de resultados passou (encontrou heading).")
    except Exception as e:
        pytest.fail(f"Falha ao encontrar o heading esperado na página de resultados: {e}")

    # O teste passou se chegou até aqui sem falhar
    print("Teste básico do fluxo do quiz concluído com sucesso!")