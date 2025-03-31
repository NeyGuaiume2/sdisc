# backend/score_calculator.py

"""
Algoritmo de pontuação para a avaliação DISC.
Calcula o perfil DISC com base nas respostas MAIS e MENOS, utilizando as palavras selecionadas.
"""

# Importa as descrições e a função para buscar o perfil pela palavra
# Não precisamos mais de disc_mapping para o cálculo principal
from .disc_data import disc_descriptions, get_profile_for_word, disc_questions # Importamos disc_questions para garantir que os dados estão carregados

# Import List e Dict para type hinting (opcional, mas boa prática)
from typing import List, Dict, Any, Optional

def calculate_disc_scores(responses: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Calcula as pontuações DISC com base nas respostas fornecidas (palavras).

    Args:
        responses: Lista de dicionários, onde cada dicionário representa a resposta
                   de uma questão no formato:
                   {'question_id': int, 'mais': 'palavra_escolhida', 'menos': 'palavra_escolhida'}

    Returns:
        Dicionário com os resultados DISC, incluindo:
        - disc_scores: Pontuações para cada fator DISC (D, I, S, C)
        - disc_levels: Nível (Alto, Médio, Baixo) para cada fator
        - primary_profile: Perfil DISC predominante (letra)
        - secondary_profile: Perfil DISC secundário (letra)
        - primary_description: Dicionário com descrições do perfil primário
        - secondary_description: Dicionário com descrições do perfil secundário
        Retorna None se a entrada for inválida ou vazia.
    """
    if not responses:
        print("WARN: Nenhuma resposta fornecida para calcular scores.") # Use logging em produção
        return None

    # Inicializa scores diretamente para os perfis DISC
    disc_scores = {'D': 0, 'I': 0, 'S': 0, 'C': 0}

    # Processa cada resposta
    for answer in responses:
        question_id = answer.get('question_id')
        mais_word = answer.get('mais')
        menos_word = answer.get('menos')

        # Validação básica da resposta
        if not all([question_id, mais_word, menos_word]):
            print(f"WARN: Resposta inválida ou incompleta ignorada: {answer}") # Use logging
            continue # Pula para a próxima resposta

        # Encontra o perfil correspondente para a palavra MAIS
        profile_mais = get_profile_for_word(question_id, mais_word)
        if profile_mais:
            disc_scores[profile_mais] += 1
        else:
            print(f"WARN: Perfil não encontrado para MAIS='{mais_word}' na questão {question_id}") # Use logging

        # Encontra o perfil correspondente para a palavra MENOS
        profile_menos = get_profile_for_word(question_id, menos_word)
        if profile_menos:
            # Verifica se a mesma palavra foi escolhida para MAIS e MENOS (não deveria acontecer com UI correta)
            if profile_mais == profile_menos:
                 print(f"WARN: Mesma palavra ('{mais_word}') escolhida para MAIS e MENOS na questão {question_id}. Ignorando MENOS.") # Use logging
            else:
                disc_scores[profile_menos] -= 1
        else:
            print(f"WARN: Perfil não encontrado para MENOS='{menos_word}' na questão {question_id}") # Use logging

    # Verifica se algum score foi calculado (evita erro no sorted se todos forem 0 ou respostas inválidas)
    if not any(disc_scores.values()):
         print("WARN: Nenhum score DISC pôde ser calculado a partir das respostas.") # Use logging
         # Poderia retornar um resultado padrão ou None/Exception
         # Por enquanto, vamos continuar e eles serão ordenados como 0
         pass


    # Identifica os perfis predominantes
    # Ordena os itens do dicionário (perfil, score) por score em ordem decrescente
    sorted_profiles = sorted(disc_scores.items(), key=lambda item: item[1], reverse=True)

    primary_profile = sorted_profiles[0][0]
    # Garante que há pelo menos dois perfis para definir um secundário
    secondary_profile = sorted_profiles[1][0] if len(sorted_profiles) > 1 else primary_profile # Ou None, ou outro default

    # Determina o nível para cada fator (Alto, Médio, Baixo)
    # Estes limites podem precisar de ajuste dependendo da escala final dos scores (-28 a +28 teoricamente)
    # Vamos usar uma faixa mais ampla, por exemplo: Alto > 5, Baixo < -5
    disc_levels = {}
    for factor, score in disc_scores.items():
        # Ajuste os limites conforme necessário para sua escala
        if score > 5: # Exemplo: Limite para Alto
            level = "Alto"
        elif score < -5: # Exemplo: Limite para Baixo
            level = "Baixo"
        else:
            level = "Médio"
        disc_levels[factor] = level

    # Prepara o resultado completo
    # Removemos raw_counts e raw_scores que eram baseados nas letras A,B,C,D
    result = {
        'disc_scores': disc_scores,
        'disc_levels': disc_levels,
        'primary_profile': primary_profile,
        'secondary_profile': secondary_profile,
        # Inclui as descrições completas para facilitar o uso no template/API
        'primary_description': disc_descriptions.get(primary_profile, {}),
        'secondary_description': disc_descriptions.get(secondary_profile, {}),
        # Adiciona as interpretações para uso direto (opcional)
        'profile_interpretations': disc_descriptions # Passa todas as descrições
    }

    return result

# --- As funções auxiliares get_profile_summary e generate_detailed_report ---
# --- permanecem praticamente as mesmas, pois dependem da ESTRUTURA ---
# --- do resultado ('disc_scores', 'primary_profile', etc.) que foi mantida. ---

def get_profile_summary(disc_result: Dict[str, Any]) -> str:
    """
    Gera um resumo textual do perfil DISC com base nos resultados calculados.

    Args:
        disc_result: Dicionário com os resultados do cálculo DISC retornado por calculate_disc_scores.

    Returns:
        String com o resumo do perfil ou mensagem de erro.
    """
    if not disc_result or 'primary_profile' not in disc_result:
        return "Não foi possível gerar o resumo do perfil (dados de resultado inválidos)."

    primary = disc_result['primary_profile']
    secondary = disc_result['secondary_profile']
    levels = disc_result.get('disc_levels', {})
    descriptions = disc_result.get('profile_interpretations', disc_descriptions) # Usa o passado ou o global

    primary_title = descriptions.get(primary, {}).get('title', primary)
    secondary_title = descriptions.get(secondary, {}).get('title', secondary)

    summary = f"Seu perfil DISC é predominantemente **{primary_title} ({primary})**"
    if primary != secondary:
         summary += f", com uma influência secundária significativa de **{secondary_title} ({secondary})**.\n\n"
    else:
         summary += ".\n\n"


    summary += "**Níveis de Intensidade por Fator:**\n"
    for factor, level in levels.items():
        factor_name = descriptions.get(factor, {}).get('title', factor)
        score = disc_result.get('disc_scores', {}).get(factor, 'N/A')
        summary += f"- **{factor} ({factor_name}):** {level} (Score: {score})\n"

    primary_desc = descriptions.get(primary, {})
    if primary_desc:
        summary += f"\nComo perfil **{primary}** dominante, você tende a ser motivado(a) por: *{primary_desc.get('motivation', 'N/A')}*.\n\n"

        summary += "**Características Comuns Associadas:**\n"
        # Mostra algumas características do primário
        characteristics = primary_desc.get('characteristics', [])
        for characteristic in characteristics[:3]:  # Mostra as 3 primeiras
            summary += f"- {characteristic.capitalize()}\n"

    secondary_desc = descriptions.get(secondary, {})
    if primary != secondary and secondary_desc:
        summary += f"\nSua influência secundária **{secondary}** pode adicionar traços como *{secondary_desc.get('motivation', 'N/A')}* ao seu comportamento.\n"

    return summary

def generate_detailed_report(disc_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gera um relatório mais detalhado do perfil DISC.

    Args:
        disc_result: Dicionário com os resultados do cálculo DISC.

    Returns:
        Dicionário com seções detalhadas do relatório.
    """
    if not disc_result or 'primary_profile' not in disc_result:
        return {"error": "Dados de resultado inválidos para gerar relatório detalhado."}

    primary = disc_result['primary_profile']
    secondary = disc_result['secondary_profile']
    descriptions = disc_result.get('profile_interpretations', disc_descriptions)

    primary_desc = descriptions.get(primary, {})
    secondary_desc = descriptions.get(secondary, {})

    report = {
        'profile_summary': get_profile_summary(disc_result), # Reutiliza o resumo
        'primary_profile_details': {
            'title': primary_desc.get('title', primary),
            'motivation': primary_desc.get('motivation', 'N/A'),
            'characteristics': primary_desc.get('characteristics', []),
            'strengths': primary_desc.get('strengths', []),
            'weaknesses': primary_desc.get('weaknesses', []),
            'how_to_work_with': primary_desc.get('how_to_work_with', 'N/A')
        },
        'secondary_profile_details': None, # Preenchido se for diferente do primário
        'development_areas_list': [],
        'raw_scores': disc_result.get('disc_scores', {}) # Inclui os scores numéricos
    }

    if primary != secondary and secondary_desc:
         report['secondary_profile_details'] = {
             'title': secondary_desc.get('title', secondary),
             'motivation': secondary_desc.get('motivation', 'N/A'),
             'characteristics': secondary_desc.get('characteristics', []),
             'strengths': secondary_desc.get('strengths', []),
             'weaknesses': secondary_desc.get('weaknesses', []),
             'how_to_work_with': secondary_desc.get('how_to_work_with', 'N/A')
        }

    # Adiciona áreas de desenvolvimento genéricas baseadas no perfil primário
    # (Esta lógica pode ser muito mais sofisticada)
    development_areas = []
    if primary == 'D':
        development_areas.extend([
            "Desenvolver maior paciência e empatia nas interações.",
            "Praticar a escuta ativa para compreender melhor outras perspectivas.",
            "Delegar tarefas e confiar mais na equipe."
        ])
    elif primary == 'I':
        development_areas.extend([
            "Melhorar a organização pessoal e o gerenciamento do tempo.",
            "Aumentar o foco na conclusão de tarefas e atenção aos detalhes.",
            "Ser mais objetivo(a) na análise de dados e informações."
        ])
    elif primary == 'S':
        development_areas.extend([
            "Desenvolver maior assertividade para expressar necessidades e opiniões.",
            "Aumentar a adaptabilidade a mudanças e novas situações.",
            "Praticar a tomada de decisões de forma mais independente."
        ])
    elif primary == 'C':
        development_areas.extend([
            "Ser mais flexível e aberto(a) a abordagens diferentes.",
            "Desenvolver a capacidade de tomar decisões com informações 'suficientes' (evitar paralisia por análise).",
            "Praticar a comunicação interpessoal de forma mais calorosa e direta."
        ])

    # Considerar também o perfil secundário para sugestões mais ricas (lógica futura)
    # Ex: Se for D primário e S secundário, uma sugestão poderia ser "Equilibrar a busca por resultados com a manutenção da harmonia da equipe".

    report['development_areas_list'] = development_areas

    return report