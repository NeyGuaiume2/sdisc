"""
Definição das rotas da API para a aplicação DISC.
"""

from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
import json
from backend.score_calculator import calculate_disc_scores, get_profile_summary, generate_detailed_report
# Removido: from backend.models.disc_result import DISCResult
# Removido: from backend.db import db

# Cria blueprint para as rotas principais
main_bp = Blueprint('main', __name__)


# Rota principal
@main_bp.route('/')
def index():
    return render_template('index.html')

# Rota para obter as perguntas do questionário DISC
@main_bp.route('/api/questions', methods=['GET'])
def get_questions():
    # Carregando as perguntas do questionário DISC (exemplo)
    questions = [
        {
            "id": 1,
            "options": [
                {"id": "A", "text": "DETERMINADO"},
                {"id": "B", "text": "CONFIANTE"},
                {"id": "C", "text": "CONSISTENTE"},
                {"id": "D", "text": "PRECISO"}
            ]
        },
        {
            "id": 2,
            "options": [
                {"id": "A", "text": "DIRETO"},
                {"id": "B", "text": "PERSUASIVO"},
                {"id": "C", "text": "LEAL"},
                {"id": "D", "text": "CUIDADOSO"}
            ]
        },
        # ... mais perguntas ...
    ]
    return jsonify(questions)


# Rota para salvar uma avaliação completa
@main_bp.route('/api/assessment', methods=['POST'])
def save_assessment():
    data = request.json
    data['timestamp'] = datetime.now().isoformat()

    # Corrigido: Acesso ao ASSESSMENTS_FILE usando app.config
    assessments_file = main_bp.root_path + '/data/assessments.json'


    with open(assessments_file, 'r') as f:
        try:
            assessments = json.load(f)
        except json.JSONDecodeError:
            assessments = []

    assessments.append(data)

    with open(assessments_file, 'w') as f:
        json.dump(assessments, f, indent=2)

    return jsonify({"success": True, "id": data.get('id', len(assessments))})


# Rota para processar e calcular os resultados DISC
@main_bp.route('/api/calculate', methods=['POST'])
def calculate_disc():
    responses = request.json

    if not responses:
        return jsonify({"error": "Nenhuma resposta recebida"}), 400

    try:
        converted_responses = {}
        for question_id, answer in responses.items():
            converted_responses[question_id] = {}
            if 'most' in answer and answer['most']:
                converted_responses[question_id]['mais'] = answer['most']
            if 'least' in answer and answer['least']:
                converted_responses[question_id]['menos'] = answer['least']

        disc_result = calculate_disc_scores(converted_responses)
        profile_summary = get_profile_summary(disc_result)
        detailed_report = generate_detailed_report(disc_result)

        disc_result['profile_summary'] = profile_summary
        disc_result['detailed_report'] = detailed_report

        result = {
            'results': disc_result,
            'success': True
        }
        return jsonify(result)

    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc(),
            "success": False
        }), 500