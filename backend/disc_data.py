# backend/disc_data.py

import logging

# Cria um logger específico para este módulo
logger = logging.getLogger(__name__)

# Mapeamento interno (remover se não for usado em nenhum lugar)
# disc_mapping = {
#     'A': 'D',
#     'B': 'I',
#     'C': 'S',
#     'D': 'C'
# }

# Descrições dos Perfis (sem alterações da versão anterior)
disc_descriptions = {
    'D': {
        'title': 'Dominância',
        'description': 'Pessoas com alta Dominância são diretas, assertivas, focadas em resultados e gostam de desafios e controle. São competitivas e tomam decisões rapidamente.',
        'motivation': 'resultados, poder e desafios',
        'characteristics': ['direto', 'decisivo', 'orientado a resultados', 'competitivo', 'assertivo', 'independente', 'focado', 'ousado'],
        'strengths': ['Liderança', 'Tomada de decisão rápida', 'Resolução de problemas', 'Foco em metas', 'Iniciativa'],
        'weaknesses': ['Impaciência', 'Insensibilidade às necessidades dos outros', 'Pode ser visto como autoritário', 'Tende a assumir controle excessivo'],
        'how_to_work_with': [
            'Seja direto e objetivo.',
            'Foque nos resultados e metas (o "quê").',
            'Evite detalhes excessivos ou conversas longas não relacionadas ao objetivo.',
            'Apresente os fatos de forma lógica e concisa.',
            'Dê espaço para autonomia e tomada de decisão.',
            'Mostre competência e confiança.'
        ]
    },
    'I': {
        'title': 'Influência',
        'description': 'Indivíduos com alta Influência são entusiastas, otimistas, sociáveis e persuasivos. Gostam de interagir, motivar os outros e buscam reconhecimento social.',
        'motivation': 'reconhecimento social, persuasão e popularidade',
        'characteristics': ['entusiasta', 'otimista', 'persuasivo', 'sociável', 'comunicativo', 'inspirador', 'amigável', 'falante'],
        'strengths': ['Comunicação', 'Networking', 'Motivação de equipes', 'Persuasão', 'Entusiasmo'],
        'weaknesses': ['Desorganização', 'Falta de atenção aos detalhes', 'Impulsividade', 'Pode evitar conflitos para manter a popularidade', 'Otimismo excessivo'],
        'how_to_work_with': [
            'Seja amigável, positivo e demonstre entusiasmo.',
            'Permita tempo para interação social e conversa.',
            'Reconheça publicamente suas contribuições e ideias.',
            'Evite excesso de dados, rotinas rígidas ou isolamento.',
            'Foque no "quadro geral", nos relacionamentos e na inspiração (o "quem").',
            'Apresente ideias de forma animada.'
        ]
    },
    'S': {
        'title': 'Estabilidade',
        'description': 'Pessoas com alta Estabilidade são pacientes, calmas, leais e cooperativas. Valorizam a segurança, a harmonia e relacionamentos consistentes. São bons ouvintes.',
        'motivation': 'cooperação, segurança e confiabilidade',
        'characteristics': ['paciente', 'leal', 'previsível', 'cooperativo', 'calmo', 'bom ouvinte', 'constante', 'atencioso'],
        'strengths': ['Cooperação', 'Consistência', 'Paciência', 'Lealdade', 'Bom ouvinte', 'Trabalho em equipe'],
        'weaknesses': ['Resistência a mudanças', 'Dificuldade em dizer não', 'Evita conflitos', 'Pode guardar ressentimentos', 'Demora a se adaptar'],
        'how_to_work_with': [
            'Seja paciente, calmo e sincero.',
            'Construa um relacionamento de confiança e mostre interesse genuíno.',
            'Evite mudanças bruscas, pressão excessiva ou conflitos abertos.',
            'Explique as coisas passo a passo, de forma clara e lógica (o "como").',
            'Demonstre apreço pela sua lealdade e consistência.',
            'Ofereça suporte e segurança.'
        ]
    },
    'C': {
        'title': 'Conformidade',
        'description': 'Indivíduos com alta Conformidade são analíticos, precisos, organizados e focados em qualidade e regras. São cuidadosos, lógicos e buscam informações detalhadas.',
        'motivation': 'qualidade, precisão e expertise',
        'characteristics': ['analítico', 'detalhista', 'preciso', 'sistemático', 'organizado', 'cauteloso', 'disciplinado', 'lógico'],
        'strengths': ['Análise detalhada', 'Qualidade do trabalho', 'Organização', 'Planejamento', 'Precisão', 'Seguir regras'],
        'weaknesses': ['Perfeccionismo', 'Excesso de crítica (a si e aos outros)', 'Pode ser indeciso sem dados suficientes (paralisia por análise)', 'Dificuldade com ambiguidades', 'Pode parecer frio ou distante'],
        'how_to_work_with': [
            'Forneça informações detalhadas, fatos e dados.',
            'Seja preciso, lógico e organizado na comunicação.',
            'Evite abordagens emocionais, pressão por decisões rápidas ou informações vagas.',
            'Dê tempo suficiente para análise e planejamento.',
            'Respeite a necessidade de regras, procedimentos e qualidade (o "porquê").',
            'Prepare-se bem antes de interagir.'
        ]
    }
}

# Lista com as 28 Questões DISC ATUALIZADA
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
    {"id": 25, "D": "Ambicioso(a)", "I": "Aberto(a)", "S": "Confiável", "C": "Exigente"}, # Confirmado: Exigente é C aqui
    {"id": 26, "D": "Focado", "I": "Interativo(a)", "S": "Atencioso(a)", "C": "Organizado(a)"},
    {"id": 27, "D": "Proativo(a)", "I": "Agradável", "S": "Consistente", "C": "Normativo(a)"},
    {"id": 28, "D": "Decisivo(a)", "I": "Estimulante", "S": "Previsível", "C": "Correto(a)"}
]

# --- Funções auxiliares (sem alterações da versão anterior) ---
def get_question_by_id(question_id):
    """Retorna o dicionário da questão com o ID fornecido."""
    try:
        target_id = int(question_id)
    except (ValueError, TypeError):
        logger.warning(f"ID de questão inválido recebido: {question_id}. Não é um inteiro.")
        return None

    for question in disc_questions:
        if question.get('id') == target_id:
            return question
    logger.warning(f"Questão com ID {target_id} não encontrada em disc_questions.")
    return None

def get_profile_for_word(question_id, selected_word):
    """
    Retorna o perfil (D, I, S, C) para uma palavra específica em uma questão,
    ignorando maiúsculas/minúsculas e espaços extras.
    """
    question = get_question_by_id(question_id)
    if not question:
        return None

    if not selected_word or not isinstance(selected_word, str):
        logger.warning(f"Palavra selecionada inválida para Q{question_id}: {selected_word}")
        return None

    # Normaliza a palavra selecionada
    normalized_selected_word = selected_word.strip().lower()

    found_profiles = []

    for profile, word_in_data in question.items():
        if profile in ['D', 'I', 'S', 'C'] and isinstance(word_in_data, str):
            # Normaliza a palavra dos dados da questão
            normalized_word_in_data = word_in_data.strip().lower()
            if normalized_word_in_data == normalized_selected_word:
                found_profiles.append(profile)

    # Tratamento de Múltiplos Matches (não deve ocorrer com os dados corrigidos)
    if len(found_profiles) == 1:
        return found_profiles[0]
    elif len(found_profiles) > 1:
        # Log de erro caso a validação falhe ou não seja executada
        logger.error(f"ERRO NOS DADOS (inesperado)! Q{question_id}: Palavra '{selected_word}' encontrada para múltiplos perfis: {found_profiles}. Retornando o primeiro ({found_profiles[0]}). VERIFICAR disc_questions!")
        return found_profiles[0]
    else:
        # Log movido para score_calculator para evitar duplicação se a palavra não for encontrada
        # logger.warning(f"Q{question_id}: NENHUM perfil encontrado para a palavra '{selected_word}' (normalizada: '{normalized_selected_word}').")
        return None

# --- Função de validação inicial dos dados (sem alterações) ---
def validate_disc_data():
    """Verifica por IDs duplicados e palavras duplicadas dentro da mesma questão."""
    all_ids = set()
    valid = True
    logger.info("Iniciando validação dos dados de disc_questions...")
    question_count = len(disc_questions)
    if question_count != 28:
         logger.warning(f"Validação: Número de questões encontrado é {question_count}, esperado era 28.")
         # Pode definir valid = False aqui se o número exato for crítico

    for i, question in enumerate(disc_questions):
        q_id = question.get('id')
        if not isinstance(q_id, int):
            logger.error(f"Erro nos dados: Questão {i+1} (índice {i}) não tem um 'id' inteiro: {question}")
            valid = False
            continue

        if q_id in all_ids:
            logger.error(f"Erro nos dados: ID de questão duplicado encontrado: {q_id}")
            valid = False
        all_ids.add(q_id)

        words_in_question = {} # {palavra_normalizada: [perfis]}
        profiles_in_question = set()
        for profile, word in question.items():
            if profile == 'id': continue # Ignora o ID

            if profile not in ['D', 'I', 'S', 'C']:
                logger.error(f"Erro nos dados: Q{q_id}, perfil inválido encontrado: '{profile}'")
                valid = False
            profiles_in_question.add(profile)

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

        # Verifica se todos os 4 perfis estão presentes
        if len(profiles_in_question) != 4:
             logger.error(f"Erro nos dados: Q{q_id} não contém exatamente 4 perfis (D, I, S, C). Encontrados: {profiles_in_question}")
             valid = False

    # Verifica se todos os IDs de 1 a 28 estão presentes
    expected_ids = set(range(1, 29))
    if all_ids != expected_ids:
        missing = expected_ids - all_ids
        extra = all_ids - expected_ids
        if missing: logger.error(f"Erro nos dados: IDs de questão faltando: {missing}")
        if extra: logger.error(f"Erro nos dados: IDs de questão extras/inválidos: {extra}")
        valid = False


    if valid:
        logger.info(f"Validação de disc_questions ({question_count} questões) concluída. Nenhum erro óbvio encontrado.")
    else:
        logger.error("Validação de disc_questions encontrou ERROS. Verifique os logs acima.")
    return valid

# Executa a validação quando o módulo é importado (recomendado durante desenvolvimento)
# validate_disc_data()