# backend/routes.py

import sys
import os
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    current_app, # Para logging
    session      # Para armazenar resultados entre requests
)

# Importações locais do projeto
try:
    # Use import relativo se routes.py estiver dentro do pacote backend
    from .disc_data import disc_questions, disc_descriptions
    from .score_calculator import calculate_disc_scores, generate_detailed_report # Pode usar generate_detailed_report se precisar na rota /results
except ImportError:
    # Fallback para import absoluto (pode funcionar dependendo de como o app é executado)
    # mas o relativo é geralmente preferível dentro de um pacote.
    from disc_data import disc_questions, disc_descriptions
    from score_calculator import calculate_disc_scores, generate_detailed_report
    current_app.logger.warning("Usando imports absolutos em routes.py. Verifique a estrutura do pacote se houver problemas.")


# Criação do Blueprint (geralmente nomeado 'main' ou algo descritivo)
# Use o nome que você definiu ao registrar o blueprint em app.py
main_bp = Blueprint('main', __name__)

# --- Rota Principal (Página Inicial) ---
@main_bp.route('/')
def index():
    """Renderiza a página inicial."""
    current_app.logger.info("Acessando a rota / (index)")
    # Adicione qualquer lógica necessária para a página inicial aqui
    return render_template('index.html')

# --- Rota para a Página do Quiz ---
@main_bp.route('/quiz')
def quiz():
    """Renderiza a página do questionário DISC."""
    current_app.logger.info("Acessando a rota /quiz")
    try:
        total_questions = len(disc_questions)
        current_app.logger.info(f"Renderizando quiz.html com total_questions={total_questions}")
    except Exception as e:
        current_app.logger.error(f"Erro ao obter tamanho de disc_questions: {e}")
        total_questions = 0 # Ou um valor padrão seguro
    # Passa o número total de questões para o template (usado no HTML inicial)
    return render_template('quiz.html', total_questions=total_questions)

# --- Rota da API para Fornecer as Questões ---
@main_bp.route('/api/questions')
def get_questions_api():
    """Endpoint da API para retornar a lista completa de questões DISC em JSON."""
    current_app.logger.info("Acessando a rota /api/questions")
    if not disc_questions:
        current_app.logger.error("API /api/questions: Lista de questões não carregada ou vazia.")
        return jsonify({"error": "Lista de questões não disponível."}), 500
    # Retorna a lista de dicionários das questões diretamente
    return jsonify(disc_questions)

# --- Rota da API para Calcular Resultados ---
@main_bp.route('/api/calculate', methods=['POST'])
def calculate_results_api():
    """
    Endpoint da API para receber as respostas do quiz (formato de palavras),
    calcular o perfil DISC e armazenar o resultado na sessão.
    """
    current_app.logger.info("Acessando a rota /api/calculate (POST)")
    if not request.is_json:
        current_app.logger.warning("/api/calculate: Requisição não é JSON.")
        return jsonify({"success": False, "error": "Requisição deve ser JSON."}), 400

    data = request.get_json()
    if not data or 'answers' not in data or not isinstance(data['answers'], list):
        current_app.logger.warning("/api/calculate: Payload JSON inválido ou chave 'answers' ausente/inválida.")
        return jsonify({"success": False, "error": "Payload inválido. Esperado: {'answers': [...]}"}), 400

    answers = data['answers']
    current_app.logger.info(f"Recebidas {len(answers)} respostas para cálculo.")
    # Log para depuração (cuidado com dados excessivos em produção)
    # current_app.logger.debug(f"Primeiras 2 respostas: {answers[:2]}")

    if not answers:
         current_app.logger.warning("/api/calculate: Lista de 'answers' está vazia.")
         return jsonify({"success": False, "error": "Nenhuma resposta fornecida."}), 400

    # Chama a função de cálculo que agora espera uma lista de dicts com palavras
    results = calculate_disc_scores(answers)

    if results and isinstance(results, dict):
        current_app.logger.info(f"Cálculo DISC bem-sucedido. Perfil primário: {results.get('primary_profile')}")

        # Armazena o resultado completo na sessão do usuário
        # Isso requer que a app Flask tenha uma SECRET_KEY configurada!
        session['disc_result'] = results
        # Armazena também as descrições usadas, para garantir consistência na página de resultados
        session['profile_interpretations'] = disc_descriptions

        # Confirma para o frontend que o cálculo foi ok (ele redirecionará)
        return jsonify({"success": True})
    else:
        current_app.logger.error("Falha no cálculo dos scores DISC (calculate_disc_scores retornou None ou formato inválido).")
        return jsonify({"success": False, "error": "Falha interna ao calcular os scores DISC."}), 500

# --- Rota para Exibir a Página de Resultados ---
@main_bp.route('/results')
def show_results():
    """Exibe a página de resultados buscando os dados armazenados na sessão."""
    current_app.logger.info("Acessando a rota /results")

    # Tenta obter os resultados da sessão
    result_data = session.get('disc_result')
    interpretations = session.get('profile_interpretations', disc_descriptions) # Usa da sessão ou o default global

    if not result_data:
        current_app.logger.warning("Acesso a /results sem 'disc_result' na sessão. Renderizando página vazia.")
        # Opcional: redirecionar para o quiz ou mostrar uma mensagem clara
        # return redirect(url_for('main.quiz'))
        # Renderiza a página de resultados, mas passa `result=None`
        # O template results.html já tem lógica para tratar isso ({% if result %})
        return render_template('results.html', result=None, profile_interpretations=interpretations)

    # Se encontrou dados na sessão, renderiza a página com eles
    current_app.logger.info(f"Exibindo resultados para perfil primário: {result_data.get('primary_profile')}")

    # O template results.html espera 'result' (que é o dicionário completo vindo do calculador)
    # e 'profile_interpretations' (que é o disc_descriptions)
    return render_template('results.html', result=result_data, profile_interpretations=interpretations)

# --- Outras rotas do seu Blueprint (se houver) ---
# ...