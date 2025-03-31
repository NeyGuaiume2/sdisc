# backend/routes.py

from flask import Blueprint, jsonify, request, render_template, session, url_for, redirect
from datetime import datetime
import json
import os
import traceback
# Importação relativa (mantida)
from .score_calculator import calculate_disc_scores, get_profile_summary, generate_detailed_report
# Importar descrições diretamente se o JSON falhar consistentemente
from .disc_data import disc_descriptions as fallback_interpretations

# --- Função get_profile_interpretations (Mantida Robusta) ---
def get_profile_interpretations():
    interpretations = None
    try:
        # Caminho para data/interpretations.json relativo à raiz do projeto
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        interpretations_file = os.path.join(project_root, 'data', 'interpretations.json')

        if os.path.exists(interpretations_file):
            with open(interpretations_file, 'r', encoding='utf-8') as f:
                interpretations = json.load(f)
                if not isinstance(interpretations, dict):
                    print(f"WARN: interpretations.json não contém um dicionário. Usando fallback. Conteúdo: {interpretations}")
                    interpretations = None
                # Validar estrutura básica das interpretações carregadas
                elif not all(k in interpretations for k in ['D', 'I', 'S', 'C']):
                     print(f"WARN: interpretations.json não contém todas as chaves D, I, S, C. Usando fallback.")
                     interpretations = None

        else:
            print(f"WARN: Arquivo interpretations.json não encontrado em {interpretations_file}. Usando fallback.")

    except json.JSONDecodeError as json_err:
        print(f"ERROR: Erro ao decodificar interpretations.json: {json_err}. Usando fallback.")
        interpretations = None
    except Exception as e:
        print(f"ERROR: Erro inesperado ao carregar interpretations.json: {e}")
        print(traceback.format_exc())
        interpretations = None

    if interpretations is None:
        print("INFO: Usando fallback interno para profile_interpretations.")
        # Usar o fallback importado de disc_data.py diretamente
        interpretations = fallback_interpretations # Ou a estrutura que você tinha antes
    return interpretations
# --- Fim get_profile_interpretations ---

main_bp = Blueprint('main', __name__, template_folder='../templates', static_folder='../static') # Ajuste paths se necessário

# --- Rotas de Página ---
@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/quiz')
def quiz():  # Renomeado para 'quiz' para corresponder ao endpoint utilizado no template
    session.pop('last_disc_result', None)
    return render_template('quiz.html')

@main_bp.route('/start-quiz')
def start_quiz():  # Mantido por compatibilidade, caso seja usado em algum lugar
    session.pop('last_disc_result', None)
    return render_template('quiz.html')

@main_bp.route('/results')
def show_results():
    result_data = session.get('last_disc_result')
    if not result_data:
         print("WARN: Nenhum resultado encontrado na sessão para /results. Redirecionando para o início.")
         # Use main.index ou main.start_quiz dependendo do nome da sua rota
         return redirect(url_for('main.index'))

    profile_interpretations = get_profile_interpretations()

    # Converter string de data de volta para datetime se necessário para o template
    # (Embora o template use strftime, é mais seguro passar datetime)
    # if 'date_created' in result_data and isinstance(result_data['date_created'], str):
    #     try:
    #         result_data['date_created'] = datetime.fromisoformat(result_data['date_created'])
    #     except ValueError:
    #         print(f"WARN: Não foi possível converter date_created ('{result_data['date_created']}') de volta para datetime.")
    #         result_data['date_created'] = datetime.now() # Fallback

    # Garantir que os campos usados no template existem, mesmo que com '?'
    result_data.setdefault('primary_profile', '?')
    result_data.setdefault('secondary_profile', '?')
    result_data.setdefault('d_intensity', '?')
    result_data.setdefault('i_intensity', '?')
    result_data.setdefault('s_intensity', '?')
    result_data.setdefault('c_intensity', '?')
    result_data.setdefault('d_score', 0)
    result_data.setdefault('i_score', 0)
    result_data.setdefault('s_score', 0)
    result_data.setdefault('c_score', 0)
    result_data.setdefault('date_created', datetime.now()) # Adiciona data se não existir


    print(f"Rendering results page with data: {result_data}")
    return render_template('results.html',
                           result=result_data,
                           profile_interpretations=profile_interpretations)

# --- Rotas de API ---

# Rota /api/questions (Mantida, mas idealmente carregaria de um arquivo)
@main_bp.route('/api/questions', methods=['GET'])
def get_questions():
    try:
        # Idealmente, carregue de um arquivo JSON ou do disc_data.py
        # Exemplo: from .disc_data import load_questions; questions = load_questions()
        questions = [
             { "id": 1, "options": [{"id": "A", "text": "DETERMINADO"}, {"id": "B", "text": "CONFIANTE"}, {"id": "C", "text": "CONSISTENTE"}, {"id": "D", "text": "PRECISO"}]},
             { "id": 2, "options": [{"id": "A", "text": "APRESSADO"}, {"id": "B", "text": "PERSUASIVO"}, {"id": "C", "text": "METÓDICO"}, {"id": "D", "text": "CUIDADOSO"}]},
             { "id": 3, "options": [{"id": "A", "text": "COMPETITIVO"}, {"id": "B", "text": "POLÍTICO"}, {"id": "C", "text": "COOPERATIVO"}, {"id": "D", "text": "DIPLOMATA"}]},
             { "id": 4, "options": [{"id": "A", "text": "OBJETIVO"}, {"id": "B", "text": "EXAGERADO"}, {"id": "C", "text": "ESTÁVEL"}, {"id": "D", "text": "EXATO"}]}
         ] # Este é um exemplo muito curto!
        return jsonify(questions)
    except Exception as e:
        print(f"Erro ao obter questões: {e}")
        return jsonify({"error": "Erro ao carregar questões"}), 500

# Rota /api/assessment (Mantida como estava, parecia robusta)
@main_bp.route('/api/assessment', methods=['POST'])
def save_assessment():
    data = request.get_json()
    if data is None:
        print("ERROR: Nenhum dado JSON válido recebido em /api/assessment")
        return jsonify({"success": False, "error": "Payload inválido ou Content-Type incorreto."}), 400

    data['timestamp'] = data.get('timestamp', datetime.now().isoformat())

    # Usar caminho absoluto relativo à raiz do projeto
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assessments_file = os.path.join(project_root, 'data', 'assessments.json')

    try:
        assessments = []
        if os.path.exists(assessments_file):
             try:
                 with open(assessments_file, 'r', encoding='utf-8') as f:
                     content = f.read()
                     if content.strip():
                         assessments = json.loads(content)
                         if not isinstance(assessments, list):
                             print(f"WARN: assessments.json não continha uma lista. Iniciando nova lista.")
                             assessments = []
                     else:
                          print("WARN: assessments.json está vazio. Iniciando nova lista.")
             except json.JSONDecodeError as json_err:
                  print(f"WARN: Erro ao decodificar assessments.json: {json_err}. Iniciando nova lista.")
                  assessments = []
             except Exception as read_err:
                  print(f"ERROR: Erro ao ler assessments.json: {read_err}. Iniciando nova lista.")
                  assessments = []
        else:
             print(f"INFO: Arquivo {assessments_file} não encontrado. Criando novo.")

        os.makedirs(os.path.dirname(assessments_file), exist_ok=True)
        assessments.append(data)
        with open(assessments_file, 'w', encoding='utf-8') as f:
            json.dump(assessments, f, indent=2, ensure_ascii=False)

    except Exception as e:
         print(f"ERROR: Erro durante o processamento/salvamento da assessment: {e}")
         print(traceback.format_exc())
         return jsonify({"success": False, "error": "Erro interno ao salvar avaliação."}), 500

    print(f"Assessment saved to {assessments_file}")
    return jsonify({"success": True, "id": data.get('id', 'N/A')})

# Rota /api/calculate (CORRIGIDA para popular profiles e intensity)
@main_bp.route('/api/calculate', methods=['POST'])
def calculate_disc():
    answers_payload = request.get_json()
    if answers_payload is None:
        print(f"ERROR: Nenhum payload JSON válido recebido em /api/calculate.")
        return jsonify({'success': False, 'error': 'Payload inválido ou Content-Type incorreto.'}), 400

    if 'answers' not in answers_payload or not isinstance(answers_payload['answers'], list):
        print(f"ERROR: Payload JSON não contém 'answers' como lista: {answers_payload}")
        return jsonify({'success': False, 'error': "Payload inválido: 'answers' deve ser uma lista."}), 400

    answers_list = answers_payload['answers']

    try:
        responses_dict = {}
        for index, item in enumerate(answers_list):
             if not isinstance(item, dict): continue
             q_id_raw = item.get('questionId'); most_val = item.get('most'); least_val = item.get('least')
             if q_id_raw is None or most_val is None or least_val is None: continue
             # Adicionar validação para não permitir mais == menos?
             # if most_val == least_val:
             #    print(f"WARN: Resposta inválida para questão {q_id_raw}: 'most' e 'least' são iguais ({most_val}). Pulando.")
             #    continue
             q_id = str(q_id_raw)
             responses_dict[q_id] = {'most': most_val, 'least': least_val}

        if not responses_dict:
             print(f"ERROR: Nenhuma resposta válida processada: {answers_list}")
             return jsonify({'success': False, 'error': 'Nenhuma resposta válida processada.'}), 400

        # Calcular scores e perfis
        disc_scores_result = calculate_disc_scores(responses_dict)
        if disc_scores_result is None:
            raise ValueError("calculate_disc_scores retornou None.")

        # Obter sumário e relatório (com fallbacks se necessário)
        profile_summary = get_profile_summary(disc_scores_result) or "Resumo indisponível."
        detailed_report = generate_detailed_report(disc_scores_result) or {"error": "Relatório detalhado indisponível."}

        # --- CORREÇÃO: Popular os campos corretamente ---
        raw_scores = disc_scores_result.get('disc_scores', {}) # Usar disc_scores aqui
        disc_levels = disc_scores_result.get('disc_levels', {}) # Obter os níveis calculados

        full_result_data = {
             # Incluir todos os dados calculados
             **disc_scores_result,
             # Sobrescrever/Adicionar campos específicos para o template/DB
             'profile_summary': profile_summary,
             'detailed_report': detailed_report,
             'date_created': datetime.now(), # Usar objeto datetime
             # Scores individuais (pegando de disc_scores)
             'd_score': raw_scores.get('D', 0),
             'i_score': raw_scores.get('I', 0),
             's_score': raw_scores.get('S', 0),
             'c_score': raw_scores.get('C', 0),
             # Perfis (pegando do resultado do cálculo)
             'primary_profile': disc_scores_result.get('primary_type', '?'),
             'secondary_profile': disc_scores_result.get('secondary_type', '?'),
             # Intensidades (mapeando dos níveis calculados)
             'd_intensity': disc_levels.get('D', '?'),
             'i_intensity': disc_levels.get('I', '?'),
             's_intensity': disc_levels.get('S', '?'),
             'c_intensity': disc_levels.get('C', '?')
        }
        # --------------------------------------------

        # Salvar na sessão (precisa serializar datetime se não usar JSON default)
        # O Flask session lida bem com datetime, mas cuidado se for salvar em outro lugar
        session['last_disc_result'] = full_result_data
        session.modified = True # Garante que a sessão seja salva
        print(f"Resultados calculados e salvos na sessão: {full_result_data}")

        return jsonify({'success': True})

    except Exception as e:
        print(f"!!! Erro crítico durante cálculo ou processamento em /api/calculate !!!")
        print(f"Erro: {e}")
        print(traceback.format_exc())
        # Não exponha detalhes do erro interno ao cliente em produção
        return jsonify({"success": False, "error": f"Erro interno do servidor ao calcular resultados."}), 500