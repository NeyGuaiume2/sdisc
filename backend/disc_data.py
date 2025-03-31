# backend/disc_data.py

# Mapeamento interno (se necessário em algum ponto, embora a estrutura abaixo seja mais direta)
# Pode ser útil se você receber apenas a letra da coluna (A, B, C, D) do frontend
disc_mapping = {
    'A': 'D', # Assumindo que a primeira palavra (depois da Questão) é D
    'B': 'I', # Assumindo que a segunda palavra é I
    'C': 'S', # Assumindo que a terceira palavra é S
    'D': 'C'  # Assumindo que a quarta palavra é C
}

# Descrições dos Perfis (mantido como estava)
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

# Lista com as 28 Questões DISC definitivas
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
    {"id": 19, "D": "Determinado(a)", "I": "Falante", "S": "Sincero(a)", "C": "Precavido(a)"}, # Repete Determinado(a), mas ok se for do teste original
    {"id": 20, "D": "Empreendedor(a)", "I": "Carismático(a)", "S": "Apoiador(a)", "C": "Formal"},
    {"id": 21, "D": "Inovador(a)", "I": "Envolvente", "S": "Atencioso(a)", "C": "Lógico(a)"},
    {"id": 22, "D": "Rápido(a)", "I": "Espontâneo(a)", "S": "Dedicado(a)", "C": "Estruturado(a)"},
    {"id": 23, "D": "Autoritário(a)", "I": "Bem-humorado(a)", "S": "Harmonioso(a)", "C": "Sistemático(a)"}, # Repete Sistemático(a), mas ok
    {"id": 24, "D": "Exigente", "I": "Brincalhão(ona)", "S": "Moderado(a)", "C": "Judicioso(a)"},
    {"id": 25, "D": "Ambicioso(a)", "I": "Aberto(a)", "S": "Confiável", "C": "Exigente"}, # Repete Exigente, mas ok
    {"id": 26, "D": "Focado", "I": "Interativo(a)", "S": "Atencioso(a)", "C": "Organizado(a)"}, # Repete Atencioso(a) e Organizado(a), mas ok
    {"id": 27, "D": "Proativo(a)", "I": "Agradável", "S": "Consistente", "C": "Normativo(a)"}, # Repete Agradável, mas ok
    {"id": 28, "D": "Decisivo(a)", "I": "Estimulante", "S": "Previsível", "C": "Correto(a)"}   # Repete Decisivo(a) e Previsível, mas ok
]

# Você pode adicionar funções auxiliares aqui se precisar, por exemplo:
def get_question_by_id(question_id):
    """Retorna o dicionário da questão com o ID fornecido."""
    for question in disc_questions:
        if question['id'] == question_id:
            return question
    return None

def get_profile_for_word(question_id, selected_word):
    """Retorna o perfil (D, I, S, C) para uma palavra específica em uma questão."""
    question = get_question_by_id(question_id)
    if question:
        for profile, word in question.items():
            # Ignora a chave 'id'
            if profile != 'id' and word == selected_word:
                return profile
    return None