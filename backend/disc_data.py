# backend/disc_data.py

import logging # Adicionar import de logging

# Cria um logger específico para este módulo (opcional, mas bom)
logger = logging.getLogger(__name__)

# Mapeamento interno (se necessário em algum ponto)
disc_mapping = {
    'A': 'D',
    'B': 'I',
    'C': 'S',
    'D': 'C'
}

# Descrições dos Perfis (COM 'how_to_work_with' CORRIGIDO PARA LISTA)
disc_descriptions = {
    'D': {
        'title': 'Dominância',
        'motivation': 'resultados, poder e desafios',
        'characteristics': ['direto', 'decisivo', 'orientado a resultados', 'competitivo', 'assertivo'],
        'strengths': ['Liderança', 'Tomada de decisão rápida', 'Resolução de problemas'],
        'weaknesses': ['Impaciência', 'Insensibilidade às necessidades dos outros'],
        'how_to_work_with': [
            'Seja direto e objetivo.',
            'Foque nos resultados e metas.',
            'Evite detalhes excessivos ou conversas longas não relacionadas ao objetivo.',
            'Apresente os fatos de forma lógica.',
            'Dê espaço para autonomia e tomada de decisão.'
        ]
    },
    'I': {
        'title': 'Influência',
        'motivation': 'reconhecimento social, persuasão e popularidade',
        'characteristics': ['entusiasta', 'otimista', 'persuasivo', 'sociável', 'comunicativo'],
        'strengths': ['Comunicação', 'Networking', 'Motivação de equipes'],
        'weaknesses': ['Desorganização', 'Falta de atenção aos detalhes', 'Impulsividade'],
        'how_to_work_with': [
            'Seja amigável, positivo e demonstre entusiasmo.',
            'Permita tempo para interação social e conversa.',
            'Reconheça publicamente suas contribuições.',
            'Evite excesso de dados ou rotinas rígidas.',
            'Foques no "quadro geral" e nos relacionamentos.'
        ]
    },
    'S': {
        'title': 'Estabilidade',
        'motivation': 'cooperação, segurança e confiabilidade',
        'characteristics': ['paciente', 'leal', 'previsível', 'cooperativo', 'calmo', 'bom ouvinte'],
        'strengths': ['Cooperação', 'Consistência', 'Paciência', 'Lealdade'],
        'weaknesses': ['Resistência a mudanças', 'Dificuldade em dizer não', 'Evita conflitos'],
        'how_to_work_with': [
            'Seja paciente, calmo e sincero.',
            'Construa um relacionamento de confiança.',
            'Evite mudanças bruscas ou pressão excessiva.',
            'Explique as coisas passo a passo e de forma clara.',
            'Demonstre apreço pela sua lealdade e consistência.'
        ]
    },
    'C': {
        'title': 'Conformidade',
        'motivation': 'qualidade, precisão e expertise',
        'characteristics': ['analítico', 'detalhista', 'preciso', 'sistemático', 'organizado', 'cauteloso'],
        'strengths': ['Análise detalhada', 'Qualidade do trabalho', 'Organização', 'Planejamento'],
        'weaknesses': ['Perfeccionismo', 'Excesso de crítica', 'Pode ser indeciso sem dados suficientes'],
        'how_to_work_with': [
            'Forneça informações detalhadas, fatos e dados.',
            'Seja preciso, lógico e organizado.',
            'Evite abordagens emocionais ou muito informais.',
            'Dê tempo suficiente para análise e planejamento.',
            'Respeite a necessidade de regras e procedimentos.'
        ]
    }
}

# Lista com as 28 Questões DISC (sem alterações, parece correta)
disc_questions = [
    {"id": 1, "D": "Determinado(a)", "I": "Persuasivo(a)", "S": "Paciente", "C": "Preciso(a)"},
    {"id": 2, "D": "Direto(a)", "I": "Entusiasmado(a)", "S": "Estável", "C": "Analítico(a)"},
    {"id": 3, "D": "Competitivo(a)", "I": "Otimista", "S": "Calmo(a)", "C": "Exato(a)"},
    {"id": 4, "D": "Decisivo(a)", "I": "Sociável", "S": "Solidário(a)", "C": "Sistemático(a)"},
    {"id": 5, "D": "Assertivo(a)", "I": "Extrovertido(a)", "S": "Tolerante", "C": "Cuidadoso(a)"},
    {"id": 6, "D": "Conquistador(a)", "I": "Charmoso(a)", "S": "Compreensivo(a)", "C": "Detalhista"},
    {"id": 7, "D": "Líder", "I": "Comunicativo(a)", "S": "Colaborativo(a)", "C": "Organizado(a)"},
    {"id": 8, "D": "Independente", "I": "Inspirador(a)", "S": "Gentil", "C": "Criterioso(a)"},
    {"id": 9, "D": "Ousado(a)", "I": "Popular", "S": "Constante", "C": "Objetivo(a)"},
    {"id": 10, "D": "Enérgico(a)", "I": "Confiante", "S": "Bondoso(a)", "C": "Consciente"},
    {"id": 11, "D": "Pioneiro(a)", "I": "Amigável", "S": "Leal", "C": "Investigador(a)"},
    {"id": 12, "D": "Arrojado(a)", "I": "Convincente", "S": "Cooperativo(a)", "C": "Planejador(a)"},
    {"id": 13, "D": "Desafiador(a)", "I": "Animado(a)", "S": "Relaxado(a)", "C": "Metódico(a)"},
    {"id": 14, "D": "Impulsionador(a)", "I": "Alegre", "S": "Agradável", "C": "Racional"},
    {"id": 15, "D": "Vigoroso(a)", "I": "Magnético(a)", "S": "Equilibrado(a)", "C": "Perfeccionista"},
    {"id": 16, "D": "Aventureiro(a)", "I": "Demonstrativo(a)", "S": "Pacífico(a)", "C": "Caprichoso(a)"},
    {"id": 17, "D": "Realizador(a)", "I": "Expressivo(a)", "S": "Sensível", "C": "Minucioso(a)"},
    {"id": 18, "D": "Autônomo(a)", "I": "Influente", "S": "Bom(boa) ouvinte", "C": "Disciplinado(a)"},
    {"id": 19, "D": "Determinado(a)", "I": "Falante", "S": "Sincero(a)", "C": "Precavido(a)"},
    {"id": 20, "D": "Empreendedor(a)", "I": "Carismático(a)", "S": "Apoiador(a)", "C": "Formal"},
    {"id": 21, "D": "Inovador(a)", "I": "Envolvente", "S": "Atencioso(a)", "C": "Lógico(a)"},
    {"id": 22, "D": "Rápido(a)", "I": "Espontâneo(a)", "S": "Dedicado(a)", "C": "Estruturado(a)"},
    {"id": 23, "D": "Autoritário(a)", "I": "Bem-humorado(a)", "S": "Harmonioso(a)", "C": "Sistemático(a)"},
    {"id": 24, "D": "Exigente", "I": "Brincalhão(ona)", "S": "Moderado(a)", "C": "Judicioso(a)"},
    {"id": 25, "D": "Ambicioso(a)", "I": "Aberto(a)", "S": "Confiável", "C": "Exigente"}, # Atenção: "Exigente" aparece em D e C aqui. Isso é intencional? Pode causar comportamento inesperado.
    {"id": 26, "D": "Focado", "I": "Interativo(a)", "S": "Atencioso(a)", "C": "Organizado(a)"}, # Atenção: "Atencioso(a)" aparece em S (Q21) e S (Q26). "Organizado(a)" aparece em C (Q7) e C (Q26). Isso é intencional?
    {"id": 27, "D": "Proativo(a)", "I": "Agradável", "S": "Consistente", "C": "Normativo(a)"},
    {"id": 28, "D": "Decisivo(a)", "I": "Estimulante", "S": "Previsível", "C": "Correto(a)"}
]

# --- Funções auxiliares ---
def get_question_by_id(question_id):
    """Retorna o dicionário da questão com o ID fornecido."""
    # Certifica que o ID é um inteiro para a comparação
    try:
        target_id = int(question_id)
    except (ValueError, TypeError):
        logger.warning(f"ID de questão inválido recebido: {question_id}. Não é um inteiro.")
        return None

    for question in disc_questions:
        if question.get('id') == target_id: # Usa .get() para segurança
            return question
    logger.warning(f"Questão com ID {target_id} não encontrada em disc_questions.")
    return None

# --- FUNÇÃO CORRIGIDA ---
def get_profile_for_word(question_id, selected_word):
    """
    Retorna o perfil (D, I, S, C) para uma palavra específica em uma questão,
    ignorando maiúsculas/minúsculas e espaços extras.
    """
    question = get_question_by_id(question_id)
    if not question:
        # get_question_by_id já loga o warning
        return None

    if not selected_word or not isinstance(selected_word, str):
        logger.warning(f"Palavra selecionada inválida para Q{question_id}: {selected_word}")
        return None

    # Normaliza a palavra selecionada (lowercase, remove espaços no início/fim)
    normalized_selected_word = selected_word.strip().lower()
    # logger.debug(f"Q{question_id}: Buscando perfil para palavra normalizada: '{normalized_selected_word}' (original: '{selected_word}')") # Log Opcional

    found_profiles = [] # Lista para armazenar perfis encontrados (tratar duplicatas)

    for profile, word_in_data in question.items():
        if profile != 'id' and isinstance(word_in_data, str):
            # Normaliza a palavra dos dados da questão
            normalized_word_in_data = word_in_data.strip().lower()

            # Compara as palavras normalizadas
            if normalized_word_in_data == normalized_selected_word:
                # logger.debug(f"Q{question_id}: Match! Palavra '{normalized_selected_word}' corresponde a '{normalized_word_in_data}' (Perfil: {profile})") # Log Opcional
                found_profiles.append(profile)

    # --- Tratamento de Múltiplos Matches (se uma palavra aparecer em mais de um perfil na MESMA questão) ---
    if len(found_profiles) == 1:
        return found_profiles[0] # Caso normal: encontrou exatamente um perfil
    elif len(found_profiles) > 1:
        # Isso indica um problema nos dados da questão (palavra duplicada para perfis diferentes na MESMA questão)
        logger.error(f"ERRO NOS DADOS! Q{question_id}: A palavra '{selected_word}' (normalizada: '{normalized_selected_word}') foi encontrada para múltiplos perfis: {found_profiles}. Retornando o primeiro ({found_profiles[0]}). VERIFICAR disc_questions!")
        # Retorna o primeiro encontrado como fallback, mas isso deve ser corrigido nos dados
        return found_profiles[0]
    else:
        # Nenhuma correspondência encontrada após normalização
        # logger.warning(f"Q{question_id}: NENHUM perfil encontrado para a palavra '{selected_word}' (normalizada: '{normalized_selected_word}'). Verifique se a palavra existe nesta questão em disc_questions.") # Log Opcional (score_calculator já loga)
        return None
# --- FIM DA FUNÇÃO CORRIGIDA ---

# --- Adicionando validação inicial dos dados (opcional, mas recomendado) ---
def validate_disc_data():
    """Verifica por IDs duplicados e palavras duplicadas dentro da mesma questão."""
    all_ids = set()
    valid = True
    logger.info("Iniciando validação dos dados de disc_questions...")

    for i, question in enumerate(disc_questions):
        q_id = question.get('id')
        if not isinstance(q_id, int):
            logger.error(f"Erro nos dados: Questão {i+1} (índice {i}) não tem um 'id' inteiro: {question}")
            valid = False
            continue # Pula para a próxima

        if q_id in all_ids:
            logger.error(f"Erro nos dados: ID de questão duplicado encontrado: {q_id}")
            valid = False
        all_ids.add(q_id)

        words_in_question = {} # {palavra_normalizada: [perfis]}
        for profile, word in question.items():
            if profile != 'id':
                if not isinstance(word, str) or not word.strip():
                     logger.error(f"Erro nos dados: Q{q_id}, Perfil {profile} tem palavra inválida ou vazia: '{word}'")
                     valid = False
                     continue

                normalized_word = word.strip().lower()
                if normalized_word in words_in_question:
                     # Palavra duplicada DENTRO da mesma questão
                     logger.error(f"Erro nos dados: Q{q_id}, palavra duplicada encontrada: '{word}' (normalizada: '{normalized_word}') aparece para perfis {words_in_question[normalized_word]} e {profile}")
                     words_in_question[normalized_word].append(profile)
                     valid = False
                else:
                    words_in_question[normalized_word] = [profile]

    if valid:
        logger.info("Validação de disc_questions concluída. Nenhum erro óbvio encontrado.")
    else:
        logger.error("Validação de disc_questions encontrou ERROS. Verifique os logs acima.")
    return valid

# Executa a validação quando o módulo é importado (opcional)
# validate_disc_data()
# -------------------------------------------------------------------