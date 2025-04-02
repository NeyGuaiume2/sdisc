# backend/routes.py (com ajustes)

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
    session      # Para armazenar ID do resultado entre requests
)

# Importações locais do projeto
try:
    # Use import relativo se routes.py estiver dentro do pacote backend
    from .disc_data import disc_questions, disc_descriptions # Necessário para passar ao template
    from .score_calculator import calculate_disc_scores #, generate_detailed_report (não usado diretamente aqui)
    from .db import db
    from .models.disc_result import DISCResult
except ImportError as e:
    # Fallback para import absoluto (pode funcionar dependendo de como o app é executado)
    # mas o relativo é geralmente preferível dentro de um pacote.
    # Use current_app.logger APÓS a criação do app
    print(f"AVISO: Erro ao importar módulos em routes.py via import relativo: {e}. Tentando fallback absoluto.")
    # Tenta fallback (menos ideal)
    try:
        from disc_data import disc_questions, disc_descriptions
        from score_calculator import calculate_disc_scores
        from db import db
        from models.disc_result import DISCResult # Ajuste o caminho se necessário
        print("AVISO: Usando imports absolutos/de fallback em routes.py.")
    except ImportError as e_fallback:
        print(f"ERRO CRÍTICO: Falha ao importar dependências em routes.py (relativo e fallback): {e_fallback}")
        # Considerar sair ou levantar um erro mais explícito se as rotas não puderem funcionar
        raise e_fallback # Relança o erro para impedir a execução incorreta


# Criação do Blueprint
main_bp = Blueprint('main', __name__)

# --- Rota Principal (Página Inicial) ---
@main_bp.route('/')
def index():
    """Renderiza a página inicial."""
    current_app.logger.info("Acessando a rota / (index)")
    return render_template('index.html')

# --- Rota para a Página do Quiz ---
@main_bp.route('/quiz')
def quiz():
    """Renderiza a página do questionário DISC."""
    current_app.logger.info("Acessando a rota /quiz")
    try:
        # Tenta carregar as questões para passar o total ao template
        questions_list = disc_questions # Usa a variável importada
        total_questions = len(questions_list) if questions_list else 0
        current_app.logger.info(f"Renderizando quiz.html com total_questions={total_questions}")
    except Exception as e:
        current_app.logger.error(f"Erro ao obter/contar disc_questions: {e}", exc_info=True)
        total_questions = 0 # Fallback
    # Passa a lista de questões também, se o JS precisar delas pré-carregadas (opcional)
    return render_template('quiz.html', total_questions=total_questions) #, questions=questions_list)

# --- Rota da API para Fornecer as Questões ---
# (Não modificada, parece OK)
@main_bp.route('/api/questions')
def get_questions_api():
    """Endpoint da API para retornar a lista completa de questões DISC em JSON."""
    current_app.logger.info("Acessando a rota /api/questions")
    if not disc_questions:
        current_app.logger.error("API /api/questions: Lista de questões 'disc_questions' não carregada ou vazia.")
        return jsonify({"error": "Lista de questões não disponível."}), 500
    return jsonify(disc_questions)

# --- Rota da API para Calcular Resultados ---
@main_bp.route('/api/calculate', methods=['POST'])
def calculate_results_api():
    """
    Endpoint da API para receber as respostas do quiz, calcular o perfil DISC,
    salvar no banco de dados e armazenar o ID do resultado na sessão.
    """
    current_app.logger.info("Acessando a rota /api/calculate (POST)")
    if not request.is_json:
        current_app.logger.warning("/api/calculate: Requisição não é JSON.")
        return jsonify({"success": False, "error": "Requisição deve ser JSON."}), 400

    data = request.get_json()
    if not data: # Checa se o JSON está vazio
         current_app.logger.warning("/api/calculate: Payload JSON vazio.")
         return jsonify({"success": False, "error": "Payload JSON vazio."}), 400

    raw_answers = data.get('answers') # Usar .get() para evitar KeyError
    user_info = data.get('userInfo', {}) # Opcional: obter info do usuário
    user_name = user_info.get('name')
    user_email = user_info.get('email')

    # Validação mais específica de raw_answers
    if not raw_answers or not isinstance(raw_answers, list):
        current_app.logger.warning(f"/api/calculate: Payload JSON inválido ou chave 'answers' ausente/inválida. Tipo recebido: {type(raw_answers)}")
        return jsonify({"success": False, "error": "Payload inválido. Esperado: {'answers': [lista_de_respostas], 'userInfo':{...}(opcional)}"}), 400

    current_app.logger.info(f"Recebidas {len(raw_answers)} respostas para cálculo. User: {user_name or user_email or 'Anon'}")
    # Log do início do payload para depuração (cuidado com dados sensíveis em produção)
    current_app.logger.debug(f"Payload 'answers' recebido (início): {str(raw_answers)[:200]}...")


    try:
        # 1. Calcula os scores chamando score_calculator
        # calculate_disc_scores agora retorna um Dict ou None em caso de falha grave
        calculated_result_dict = calculate_disc_scores(raw_answers)

        # ----> VERIFICAÇÃO IMPORTANTE <----
        if calculated_result_dict is None:
            # Se o calculador indicou falha (ex: nenhuma resposta válida processada)
            current_app.logger.error("Falha crítica no cálculo dos scores DISC (calculate_disc_scores retornou None). Verifique logs anteriores.")
            # Retorna erro 500, pois algo interno falhou
            return jsonify({"success": False, "error": "Falha interna ao calcular os scores DISC. Verifique as respostas enviadas."}), 500
        # ---------------------------------

        # Log do resultado calculado para depuração (antes de salvar)
        current_app.logger.debug(f"Resultado calculado pelo score_calculator: {calculated_result_dict}")

        # 2. Cria a instância do modelo DISCResult
        # O __init__ do modelo agora espera 'raw_responses' (lista) e 'disc_result' (o dict calculado)
        # Ele mesmo extrairá 'primary_profile' e 'secondary_profile' de dentro do dict
        new_result_entry = DISCResult(
            user_name=user_name,
            user_email=user_email,
            raw_responses=raw_answers,         # Passa a lista original recebida
            disc_result=calculated_result_dict # Passa o dict COMPLETO calculado
        )

        # 3. Salva no banco de dados
        db.session.add(new_result_entry)
        db.session.commit()
        # Log após o commit ser bem-sucedido
        current_app.logger.info(f"Resultado DISC salvo no banco de dados com ID: {new_result_entry.id}, Perfil: {new_result_entry.primary_type}/{new_result_entry.secondary_type}")

        # 4. Armazena o ID do resultado na sessão do Flask
        session['disc_result_id'] = new_result_entry.id
        # Opcional: Limpar dados antigos da sessão se necessário
        # session.pop('profile_interpretations', None) # Não precisa mais disso na sessão

        # 5. Retorna sucesso para o frontend (ele redirecionará para /results)
        return jsonify({"success": True, "result_id": new_result_entry.id}) # Retorna o ID como confirmação

    except KeyError as e:
        db.session.rollback() # Desfaz quaisquer mudanças na sessão se houver erro ANTES do commit
        current_app.logger.error(f"Erro de chave ausente ao processar/salvar resultado: {e}. Verifique o payload ou o retorno de calculate_disc_scores.", exc_info=True)
        return jsonify({"success": False, "error": f"Erro interno: chave ausente ({e})."}), 500
    except Exception as e:
        db.session.rollback() # Garante rollback em qualquer exceção durante add/commit
        current_app.logger.exception("Erro inesperado durante o cálculo ou salvamento do resultado DISC.") # Loga o traceback completo
        return jsonify({"success": False, "error": "Erro interno inesperado no servidor ao processar resultados."}), 500

# --- Rota para Exibir a Página de Resultados ---
@main_bp.route('/results')
def show_results():
    """
    Exibe a página de resultados buscando os dados do banco de dados
    usando o ID armazenado na sessão.
    """
    current_app.logger.info("Acessando a rota /results")

    # 1. Tenta obter o ID do resultado da sessão
    result_id = session.get('disc_result_id')

    if not result_id:
        current_app.logger.warning("Acesso a /results sem 'disc_result_id' na sessão. Redirecionando para o quiz.")
        # Redirecionar para o quiz ou para a home faz mais sentido
        return redirect(url_for('main.quiz')) # Ou main.index

    try:
        # 2. Busca o resultado no banco de dados pelo ID
        # Usar get_or_404 lida com o caso de ID não encontrado de forma padrão
        result_data = db.session.get(DISCResult, result_id) # Método mais novo
        # result_data = DISCResult.query.get_or_404(result_id) # Método antigo também funciona

        if result_data is None:
             current_app.logger.error(f"Resultado com ID {result_id} da sessão não encontrado no banco de dados.")
             session.pop('disc_result_id', None) # Limpa ID inválido da sessão
             # Renderiza uma página de erro amigável ou redireciona
             # return render_template('errors/404.html', message=f"Resultado da avaliação {result_id} não encontrado."), 404
             return redirect(url_for('main.index', error='result_not_found'))


        # Verifica se o resultado foi salvo com erro (perfis '?' indicam isso)
        if result_data.primary_type == '?' or result_data.secondary_type == '?':
             current_app.logger.warning(f"Exibindo resultado ID {result_id}, mas foi salvo com erro (perfis '?'). Provável falha no cálculo anterior.")
             # Pode adicionar uma mensagem no template ou logar mais detalhes

        current_app.logger.info(f"Exibindo resultados para ID: {result_id}, User: {result_data.user_name or result_data.user_email or 'Anon'}, Perfil: {result_data.primary_type}/{result_data.secondary_type}")

        # 3. Passa o objeto DISCResult diretamente para o template
        # O template usará os métodos do objeto (result.get_scores(), result.get_detailed_report(), etc.)
        # Passa também as descrições estáticas
        # Certifique-se que 'disc_descriptions' foi importado corretamente no início do arquivo
        if not disc_descriptions:
             current_app.logger.error("Variável 'disc_descriptions' não está carregada/importada em routes.py! Interpretações não serão exibidas.")
             # Fornece um fallback vazio para evitar erro no template
             loaded_descriptions = {}
        else:
             loaded_descriptions = disc_descriptions

        return render_template(
            'results.html',
            result=result_data,                  # O objeto SQLAlchemy completo
            profile_interpretations=loaded_descriptions # O dicionário de descrições estático
        )

    # Captura exceções específicas do SQLAlchemy se necessário
    # from sqlalchemy.exc import SQLAlchemyError
    # except SQLAlchemyError as e:
    #    current_app.logger.exception(f"Erro de banco de dados ao buscar resultado ID {result_id}.")
    #    return render_template('errors/500.html', message="Erro ao acessar o banco de dados."), 500
    except Exception as e:
        # Captura erros gerais durante a busca ou renderização do template
        current_app.logger.exception(f"Erro inesperado ao buscar ou renderizar resultado com ID {result_id}.")
        # Renderiza uma página de erro genérica
        # TODO: Criar templates de erro se não existirem
        # return render_template('errors/500.html', message="Erro interno ao carregar a página de resultados."), 500
        return f"<h1>Erro 500</h1><p>Ocorreu um erro interno ao tentar carregar os resultados para ID {result_id}. Detalhes: {e}</p>", 500

# --- Outras rotas ---
# Adicionar rotas para páginas de erro se não existirem
# @main_bp.app_errorhandler(404)
# def page_not_found(e):
#     current_app.logger.warning(f"Rota não encontrada: {request.path}")
#     return render_template('errors/404.html', message=e.description), 404

# @main_bp.app_errorhandler(500)
# def internal_server_error(e):
#     # O erro original já deve ter sido logado pela rota que falhou
#     current_app.logger.error(f"Erro interno 500 interceptado para {request.path}")
#     # Cuidado para não causar outro erro aqui
#     try:
#         return render_template('errors/500.html', message="Ocorreu um erro interno no servidor."), 500
#     except: # pylint: disable=bare-except
#         return "<h1>Erro 500</h1><p>Ocorreu um erro interno no servidor.</p>", 500