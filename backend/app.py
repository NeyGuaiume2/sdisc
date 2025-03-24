# Arquivo principal do backend 
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
import json
from datetime import datetime
from backend.score_calculator import calculate_disc_scores, get_profile_summary, generate_detailed_report

# Adicione este import caso você use o arquivo disc_data.py
try:
    from backend.disc_data import disc_mapping, disc_descriptions
except ImportError:
    # Definição alternativa caso o arquivo não exista
    disc_mapping = {
        'A': 'D',
        'B': 'I',
        'C': 'S',
        'D': 'C'
    }
    
    disc_descriptions = {
        'D': {
            'title': 'Dominância',
            'motivation': 'resultados, poder e desafios',
            'characteristics': ['direto', 'decisivo', 'orientado a resultados', 'competitivo', 'assertivo'],
            'strengths': ['Liderança', 'Tomada de decisão rápida', 'Resolução de problemas'],
            'weaknesses': ['Impaciência', 'Insensibilidade às necessidades dos outros'],
            'how_to_work_with': 'Seja direto, focado em resultados e evite detalhes desnecessários.'
        },
        'I': {
            'title': 'Influência',
            'motivation': 'reconhecimento social, persuasão e popularidade',
            'characteristics': ['entusiasta', 'otimista', 'persuasivo', 'sociável', 'comunicativo'],
            'strengths': ['Comunicação', 'Networking', 'Motivação de equipes'],
            'weaknesses': ['Desorganização', 'Falta de atenção aos detalhes'],
            'how_to_work_with': 'Seja amigável, demonstre interesse e permita tempo para socialização.'
        },
        'S': {
            'title': 'Estabilidade',
            'motivation': 'cooperação, segurança e confiabilidade',
            'characteristics': ['paciente', 'leal', 'previsível', 'cooperativo', 'calmo'],
            'strengths': ['Cooperação', 'Consistência', 'Paciência'],
            'weaknesses': ['Resistência a mudanças', 'Dificuldade em dizer não'],
            'how_to_work_with': 'Seja consistente, sincero e evite mudanças bruscas.'
        },
        'C': {
            'title': 'Conformidade',
            'motivation': 'qualidade, precisão e expertise',
            'characteristics': ['analítico', 'detalhista', 'preciso', 'sistemático', 'organizado'],
            'strengths': ['Análise detalhada', 'Qualidade do trabalho', 'Organização'],
            'weaknesses': ['Perfeccionismo', 'Excesso de crítica'],
            'how_to_work_with': 'Forneça detalhes, seja preciso e use abordagem lógica.'
        }
    }

def create_app(testing=False):
    """Função factory que cria e configura a aplicação Flask"""
    app = Flask(__name__)
    CORS(app)  # Habilita CORS para todas as rotas
    
    # Configuração para ambiente de teste
    if testing:
        app.config['TESTING'] = True
    
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
            {
                "id": 2,
                "options": [
                    {"id": "A", "text": "DIRETO"},
                    {"id": "B", "text": "PERSUASIVO"},
                    {"id": "C", "text": "LEAL"},
                    {"id": "D", "text": "CUIDADOSO"}
                ]
            },
            # Adicione mais perguntas conforme necessário
            {
                "id": 3,
                "options": [
                    {"id": "A", "text": "COMPETITIVO"},
                    {"id": "B", "text": "SOCIÁVEL"},
                    {"id": "C", "text": "PACIENTE"},
                    {"id": "D", "text": "ANALÍTICO"}
                ]
            },
            {
                "id": 4,
                "options": [
                    {"id": "A", "text": "ASSERTIVO"},
                    {"id": "B", "text": "EXPRESSIVO"},
                    {"id": "C", "text": "AMIGÁVEL"},
                    {"id": "D", "text": "PRUDENTE"}
                ]
            }
        ]
        
        return jsonify(questions)
    
    # Rota para salvar uma avaliação completa
    @app.route('/api/assessment', methods=['POST'])
    def save_assessment():
        data = request.json
        
        # Adicionar timestamp
        data['timestamp'] = datetime.now().isoformat()
        
        # Carregar avaliações existentes
        try:
            with open(ASSESSMENTS_FILE, 'r') as f:
                assessments = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Se o arquivo estiver vazio ou com erro, inicialize com lista vazia
            assessments = []
        
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
        
        # Verificar se há dados
        if not responses:
            return jsonify({"error": "Nenhuma resposta recebida"}), 400
        
        try:
            # Converter 'most'/'least' para 'mais'/'menos' para compatibilidade com score_calculator
            converted_responses = {}
            for question_id, answer in responses.items():
                converted_responses[question_id] = {}
                if 'most' in answer and answer['most']:
                    converted_responses[question_id]['mais'] = answer['most']
                if 'least' in answer and answer['least']:
                    converted_responses[question_id]['menos'] = answer['least']
            
            # Usar a função avançada de cálculo do score_calculator
            disc_result = calculate_disc_scores(converted_responses)
            
            # Gerar resumo do perfil
            profile_summary = get_profile_summary(disc_result)
            
            # Gerar relatório detalhado
            detailed_report = generate_detailed_report(disc_result)
            
            # Adicionar o resumo e relatório ao resultado
            disc_result['profile_summary'] = profile_summary
            disc_result['detailed_report'] = detailed_report
            
            # Preparar resposta para o frontend
            result = {
                'results': disc_result,
                'success': True
            }
            
            # Retornar os resultados completos
            return jsonify(result)
        except Exception as e:
            # Tratamento de erro
            import traceback
            return jsonify({
                "error": str(e),
                "traceback": traceback.format_exc(),
                "success": False
            }), 500
    
    return app

# Instância da aplicação para execução direta
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
