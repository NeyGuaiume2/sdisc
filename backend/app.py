# Arquivo principal do backend 
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Configuração do banco de dados (inicialmente usaremos arquivos JSON para simplicidade)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Arquivo para armazenar os dados das avaliações
ASSESSMENTS_FILE = os.path.join(DATA_DIR, 'assessments.json')

# Inicializa o arquivo de avaliações se não existir
if not os.path.exists(ASSESSMENTS_FILE):
    with open(ASSESSMENTS_FILE, 'w') as f:
        json.dump([], f)

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para obter as perguntas do questionário DISC
@app.route('/api/questions', methods=['GET'])
def get_questions():
    # Carregando as perguntas do questionário DISC
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
        # As demais perguntas serão adicionadas na próxima parte
    ]
    
    return jsonify(questions)

# Rota para salvar uma avaliação completa
@app.route('/api/assessment', methods=['POST'])
def save_assessment():
    data = request.json
    
    # Adicionar timestamp
    data['timestamp'] = datetime.now().isoformat()
    
    # Carregar avaliações existentes
    with open(ASSESSMENTS_FILE, 'r') as f:
        assessments = json.load(f)
    
    # Adicionar nova avaliação
    assessments.append(data)
    
    # Salvar de volta no arquivo
    with open(ASSESSMENTS_FILE, 'w') as f:
        json.dump(assessments, f, indent=2)
    
    return jsonify({"success": True, "id": data.get('id', len(assessments))})

# Rota para processar e calcular os resultados DISC
@app.route('/api/calculate', methods=['POST'])
def calculate_disc():
    # Receber as respostas do questionário
    responses = request.json
    
    # Inicializar contadores para cada fator DISC
    disc_counts = {
        'D': {'most': 0, 'least': 0},
        'I': {'most': 0, 'least': 0},
        'S': {'most': 0, 'least': 0},
        'C': {'most': 0, 'least': 0}
    }
    
    # Mapeamento de letra para fator DISC
    letter_to_disc = {
        'A': 'D',  # Dominância
        'B': 'I',  # Influência
        'C': 'S',  # Estabilidade
        'D': 'C'   # Conformidade
    }
    
    # Contar as respostas MAIS e MENOS
    for question_id, answer in responses.items():
        if 'most' in answer:
            letter = answer['most']
            disc_factor = letter_to_disc[letter]
            disc_counts[disc_factor]['most'] += 1
        
        if 'least' in answer:
            letter = answer['least']
            disc_factor = letter_to_disc[letter]
            disc_counts[disc_factor]['least'] += 1
    
    # Calcular os resultados finais (MAIS - MENOS)
    disc_results = {
        'D': disc_counts['D']['most'] - disc_counts['D']['least'],
        'I': disc_counts['I']['most'] - disc_counts['I']['least'],
        'S': disc_counts['S']['most'] - disc_counts['S']['least'],
        'C': disc_counts['C']['most'] - disc_counts['C']['least']
    }
    
    # Retornar os resultados
    return jsonify({
        'counts': disc_counts,
        'results': disc_results
    })

if __name__ == '__main__':
    app.run(debug=True)