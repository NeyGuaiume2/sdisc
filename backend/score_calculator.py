 """
Algoritmo de pontuação para a avaliação DISC.
Calcula o perfil DISC com base nas respostas MAIS e MENOS.
"""

from backend.disc_data import disc_mapping, disc_descriptions

def calculate_disc_scores(responses):
    """
    Calcula as pontuações DISC com base nas respostas fornecidas.
    
    Args:
        responses: Dictionary com as respostas 'mais' e 'menos' para cada questão
                  no formato {question_id: {'mais': letra, 'menos': letra}, ...}
    
    Returns:
        Dictionary com os resultados DISC, incluindo:
        - raw_scores: Contagem bruta para cada letra (A, B, C, D)
        - disc_scores: Pontuações para cada fator DISC (D, I, S, C)
        - primary_type: Tipo DISC predominante
        - secondary_type: Tipo DISC secundário
        - profile: Descrição do perfil completo
    """
    # Inicializa contadores
    raw_counts = {
        'A': {'mais': 0, 'menos': 0},
        'B': {'mais': 0, 'menos': 0},
        'C': {'mais': 0, 'menos': 0},
        'D': {'mais': 0, 'menos': 0}
    }
    
    # Conta as respostas MAIS e MENOS para cada letra
    for question_id, answer in responses.items():
        if 'mais' in answer and answer['mais']:
            raw_counts[answer['mais']]['mais'] += 1
        if 'menos' in answer and answer['menos']:
            raw_counts[answer['menos']]['menos'] += 1
    
    # Calcula os scores brutos (MAIS - MENOS)
    raw_scores = {
        'A': raw_counts['A']['mais'] - raw_counts['A']['menos'],
        'B': raw_counts['B']['mais'] - raw_counts['B']['menos'],
        'C': raw_counts['C']['mais'] - raw_counts['C']['menos'],
        'D': raw_counts['D']['mais'] - raw_counts['D']['menos']
    }
    
    # Mapeia para fatores DISC
    disc_scores = {
        'D': raw_scores['A'],  # Dominância (A)
        'I': raw_scores['B'],  # Influência (B)
        'S': raw_scores['C'],  # Estabilidade (C)
        'C': raw_scores['D']   # Conformidade (D)
    }
    
    # Identifica os tipos predominantes
    sorted_types = sorted(disc_scores.items(), key=lambda x: x[1], reverse=True)
    primary_type = sorted_types[0][0]
    secondary_type = sorted_types[1][0]
    
    # Determina o nível para cada fator (Alto, Médio, Baixo)
    # Valores típicos: Alto > 3, Médio entre -3 e 3, Baixo < -3
    disc_levels = {}
    for factor, score in disc_scores.items():
        if score > 3:
            level = "Alto"
        elif score < -3:
            level = "Baixo"
        else:
            level = "Médio"
        disc_levels[factor] = level
    
    # Prepara o resultado completo
    result = {
        'raw_counts': raw_counts,
        'raw_scores': raw_scores,
        'disc_scores': disc_scores,
        'disc_levels': disc_levels,
        'primary_type': primary_type,
        'secondary_type': secondary_type,
        'primary_description': disc_descriptions[primary_type],
        'secondary_description': disc_descriptions[secondary_type],
    }
    
    return result

def get_profile_summary(disc_result):
    """
    Gera um resumo do perfil DISC com base nos resultados calculados.
    
    Args:
        disc_result: Dictionary com os resultados do cálculo DISC
        
    Returns:
        String com o resumo do perfil
    """
    primary = disc_result['primary_type']
    secondary = disc_result['secondary_type']
    levels = disc_result['disc_levels']
    
    summary = f"Seu perfil DISC é predominantemente {disc_descriptions[primary]['title']}"
    summary += f" ({primary}), com {disc_descriptions[secondary]['title']} ({secondary}) como secundário.\n\n"
    
    summary += "Seus níveis DISC são:\n"
    for factor, level in levels.items():
        factor_name = disc_descriptions[factor]['title']
        summary += f"- {factor} ({factor_name}): {level}\n"
    
    summary += f"\nComo perfil {primary} dominante, você tende a ser motivado por: {disc_descriptions[primary]['motivation']}.\n\n"
    
    summary += "Suas principais características incluem:\n"
    for characteristic in disc_descriptions[primary]['characteristics'][:5]:  # Apenas as 5 primeiras
        summary += f"- {characteristic}\n"
    
    summary += f"\nSeu perfil secundário {secondary} contribui com elementos de {disc_descriptions[secondary]['motivation']}.\n"
    
    return summary

def generate_detailed_report(disc_result):
    """
    Gera um relatório detalhado do perfil DISC.
    
    Args:
        disc_result: Dictionary com os resultados do cálculo DISC
        
    Returns:
        Dictionary com seções detalhadas do relatório
    """
    primary = disc_result['primary_type']
    secondary = disc_result['secondary_type']
    
    report = {
        'summary': get_profile_summary(disc_result),
        'primary_strengths': disc_descriptions[primary]['strengths'],
        'primary_weaknesses': disc_descriptions[primary]['weaknesses'],
        'how_to_work_with': disc_descriptions[primary]['how_to_work_with'],
        'secondary_influence': f"Seu perfil secundário {secondary} ({disc_descriptions[secondary]['title']}) " +
                              f"adiciona características de {', '.join(disc_descriptions[secondary]['characteristics'][:3])}.",
        'development_areas': "Áreas para desenvolvimento pessoal:",
    }
    
    # Adiciona áreas de desenvolvimento com base no perfil
    development_areas = []
    if primary == 'D':
        development_areas.append("Trabalhar a paciência e empatia com os outros")
        development_areas.append("Desenvolver habilidades de escuta ativa")
    elif primary == 'I':
        development_areas.append("Melhorar a organização e atenção aos detalhes")
        development_areas.append("Desenvolver disciplina para concluir tarefas")
    elif primary == 'S':
        development_areas.append("Ser mais assertivo e expressar suas opiniões")
        development_areas.append("Desenvolver adaptabilidade a mudanças")
    elif primary == 'C':
        development_areas.append("Ser menos crítico e mais aberto a novas abordagens")
        development_areas.append("Desenvolver habilidades de comunicação interpessoal")
    
    report['development_areas_list'] = development_areas
    
    return report
