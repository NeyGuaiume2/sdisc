# tests/e2e/test_helpers.py
"""
Funções auxiliares para testes E2E com Playwright.
"""
import logging
import time
from playwright.sync_api import Page, expect

def reset_timer(page: Page, seconds=15):
    """
    Redefine o temporizador do quiz para um valor específico usando JavaScript.
    Útil para testes onde não queremos esperar o temporizador real.
    """
    logging.info(f"Redefinindo temporizador para {seconds} segundos")
    try:
        # Assume que há uma variável countdown ou um elemento #countdown 
        # controlado por JavaScript
        reset_script = f"""
        // Tenta forçar o timer para o valor desejado
        if (window.countdown !== undefined) {{
            window.countdown = {seconds};
        }}
        if (document.getElementById('countdown')) {{
            document.getElementById('countdown').textContent = '{seconds}';
        }}
        """
        page.evaluate(reset_script)
        return True
    except Exception as e:
        logging.error(f"Erro ao redefinir timer: {e}")
        return False

def force_next_question(page: Page):
    """
    Força o avanço para a próxima questão usando JavaScript.
    Útil quando queremos testar o fluxo sem esperar pelo temporizador ou animações.
    """
    logging.info("Forçando avanço para próxima questão via JavaScript")
    try:
        # Este script precisará ser adaptado com base em como seu código JS
        # implementa a navegação entre questões
        advance_script = """
        // Tenta invocar a função que avança para a próxima questão
        // Adapte com base na implementação real do seu código
        if (typeof goToNextQuestion === 'function') {
            goToNextQuestion();
        } else if (typeof loadNextQuestion === 'function') {
            loadNextQuestion();
        } else {
            // Alternativa: Tenta simular o fim do temporizador
            if (window.countdown !== undefined) {
                window.countdown = 0;
            }
            // Ou tenta encontrar e clicar em um botão de próxima questão
            const nextBtn = document.querySelector('.next-btn, #next-question, [data-action="next"]');
            if (nextBtn) nextBtn.click();
        }
        """
        page.evaluate(advance_script)
        return True
    except Exception as e:
        logging.error(f"Erro ao forçar próxima questão: {e}")
        return False

def wait_for_quiz_ready(page: Page, timeout=10000):
    """
    Espera até que o quiz esteja completamente carregado e pronto para interação.
    """
    logging.info("Aguardando quiz estar pronto...")
    try:
        # Espera o indicador de carregamento desaparecer
        page.wait_for_selector("#loading-indicator", state="hidden", timeout=timeout)
        # Espera a seção principal do quiz aparecer
        page.wait_for_selector("#assessment", state="visible", timeout=timeout)
        # Espera as opções da questão serem carregadas
        page.wait_for_selector("#options-list .option-item", state="visible", timeout=timeout)
        logging.info("Quiz está pronto para interação")
        return True
    except Exception as e:
        logging.error(f"Timeout aguardando quiz ficar pronto: {e}")
        return False

def select_question_options(page: Page, most_index=0, least_index=3):
    """
    Seleciona opções MAIS e MENOS para a questão atual.
    Por padrão, seleciona a primeira como MAIS e a última como MENOS.
    
    Args:
        page: Instância da Page do Playwright
        most_index: Índice da opção a ser selecionada como MAIS (0-based)
        least_index: Índice da opção a ser selecionada como MENOS (0-based)
    
    Returns:
        bool: True se selecionou com sucesso, False caso contrário
    """
    logging.info(f"Selecionando opção {most_index} como MAIS e {least_index} como MENOS")
    try:
        # Obter todas as opções
        options = page.locator("#options-list .option-item").all()
        if not options or len(options) < 4:
            logging.error(f"Não há opções suficientes. Encontradas: {len(options) if options else 0}")
            return False
        
        # Selecionar MAIS
        most_radio = options[most_index].locator("input.most-option")
        most_radio.click()
        
        # Selecionar MENOS
        least_radio = options[least_index].locator("input.least-option")
        least_radio.click()
        
        # Verificar se foram selecionadas
        if most_radio.is_checked() and least_radio.is_checked():
            logging.info("Opções MAIS e MENOS selecionadas com sucesso")
            return True
        else:
            logging.warning("Opções foram clicadas mas não estão marcadas como selecionadas")
            return False
    except Exception as e:
        logging.error(f"Erro ao selecionar opções: {e}")
        return False

def get_current_question_number(page: Page):
    """
    Obtém o número da questão atual do DOM.
    
    Returns:
        int: Número da questão atual ou None se não conseguir obter
    """
    try:
        question_num_text = page.locator("#question-number").text_content()
        return int(question_num_text) if question_num_text.isdigit() else None
    except Exception as e:
        logging.error(f"Erro ao obter número da questão atual: {e}")
        return None

def get_total_questions(page: Page):
    """
    Obtém o número total de questões do DOM.
    
    Returns:
        int: Número total de questões ou valor padrão (28) se não conseguir obter
    """
    try:
        total_questions_text = page.locator("#total-questions").text_content()
        return int(total_questions_text) if total_questions_text.isdigit() else 28
    except Exception as e:
        logging.error(f"Erro ao obter número total de questões: {e}")
        return 28  # Valor padrão