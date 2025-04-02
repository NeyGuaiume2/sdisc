# backend/score_calculator.py

"""
Algoritmo de pontuação para a avaliação DISC.
Calcula o perfil DISC com base nas respostas MAIS e MENOS, utilizando as palavras selecionadas.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime # Manter a importação

# Importa as descrições e a função para buscar o perfil pela palavra
try:
    # Tenta import relativo primeiro
    from .disc_data import disc_descriptions, get_profile_for_word, disc_questions
except ImportError:
    # Fallback para absoluto (menos ideal dentro de um pacote)
    from disc_data import disc_descriptions, get_profile_for_word, disc_questions
    logging.warning("Usando import absoluto em score_calculator.py")

# Cria um logger específico para este módulo
logger = logging.getLogger(__name__)

def calculate_disc_scores(responses: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Calcula as pontuações DISC com base nas respostas fornecidas (palavras).

    Args:
        responses: Lista de dicionários {'questionId': int, 'mais': 'palavra', 'menos': 'palavra'}
                   (Note o 'questionId' em camelCase vindo do frontend)

    Returns:
        Dicionário com os resultados DISC (incluindo scores NUMÉRICOS e data como string ISO)
        ou None se falhar.
    """
    if not responses:
        logger.warning("Nenhuma resposta fornecida para calcular scores.")
        return None

    # Inicializa scores DISC
    disc_scores = {'D': 0, 'I': 0, 'S': 0, 'C': 0}
    valid_responses_processed = 0 # Contador para respostas válidas

    # Loga as primeiras respostas para verificar o formato recebido
    if responses:
        logger.debug(f"Recebido {len(responses)} respostas. Exemplo da primeira: {responses[0] if responses else 'N/A'}") # Log seguro

    # Processa cada resposta
    for idx, answer in enumerate(responses):
        question_id_val = None # Renomeado para evitar conflito com nome da chave
        mais_word = None
        menos_word = None

        # --- CORREÇÃO APLICADA AQUI ---
        # Verifica se é um dicionário e se contém as chaves ESPERADAS do frontend ('questionId', 'mais', 'menos')
        if isinstance(answer, dict) and 'questionId' in answer and 'mais' in answer and 'menos' in answer:
            question_id_val = answer.get('questionId') # Usa 'questionId' (camelCase do JS)
            mais_word = answer.get('mais')
            menos_word = answer.get('menos')
            # Log para cada resposta no formato esperado
            logger.debug(f"Processando resposta {idx+1}/{len(responses)}: ID={question_id_val}, Mais='{mais_word}', Menos='{menos_word}'")
        else:
             # Loga se o formato não for reconhecido
             logger.warning(f"Formato de resposta inesperado no índice {idx}, ignorando: {answer}")
             continue
        # --- FIM DA CORREÇÃO ---


        # Validação dos dados extraídos (garante que não são None ou vazios)
        # Usa a variável `question_id_val` aqui
        if not question_id_val or not mais_word or not menos_word:
            logger.warning(f"Resposta {idx+1} inválida ou incompleta (após extração). ID={question_id_val}, Mais='{mais_word}', Menos='{menos_word}'. Resposta original: {answer}")
            continue

        # --- CHAMADAS A get_profile_for_word COM LOGGING DETALHADO ---
        profile_mais = None
        profile_menos = None
        try:
            # Encontra o perfil para a palavra MAIS (passa question_id_val)
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # !!! IMPORTANTE: A CORREÇÃO DE get_profile_for_word DEPENDE !!!
            # !!! DO CONTEÚDO DE backend/disc_data.py                    !!!
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            profile_mais = get_profile_for_word(question_id_val, mais_word)
            if profile_mais:
                disc_scores[profile_mais] += 1
                logger.debug(f"  -> Q{question_id_val} MAIS='{mais_word}' -> Perfil={profile_mais}. Score {profile_mais} agora = {disc_scores[profile_mais]}")
            else:
                # Este warning é crucial para saber se o mapeamento está falhando
                logger.warning(f"  -> Q{question_id_val} MAIS='{mais_word}' -> Perfil NÃO ENCONTRADO. Verifique disc_data.py e a palavra exata enviada.")

            # Encontra o perfil para a palavra MENOS (passa question_id_val)
            profile_menos = get_profile_for_word(question_id_val, menos_word)
            if profile_menos:
                # Verifica se a mesma palavra foi escolhida para MAIS e MENOS (deve ser evitado no frontend)
                if profile_mais == profile_menos and profile_mais is not None:
                     # Não subtrai se for a mesma palavra, mas loga
                     logger.warning(f"  -> Q{question_id_val}: Mesma palavra ('{mais_word}') ou perfil ({profile_mais}) para MAIS e MENOS. Pontuação MENOS ignorada.")
                else:
                    disc_scores[profile_menos] -= 1
                    logger.debug(f"  -> Q{question_id_val} MENOS='{menos_word}' -> Perfil={profile_menos}. Score {profile_menos} agora = {disc_scores[profile_menos]}")
            else:
                # Este warning é crucial
                logger.warning(f"  -> Q{question_id_val} MENOS='{menos_word}' -> Perfil NÃO ENCONTRADO. Verifique disc_data.py e a palavra exata enviada.")

            # Se pelo menos um perfil foi encontrado para esta resposta, conta como válida
            if profile_mais or profile_menos:
                valid_responses_processed += 1

        except Exception as e:
            # Log de erro mais específico
            logger.error(f"Erro inesperado ao processar resposta para Q{question_id_val} (Mais='{mais_word}', Menos='{menos_word}'): {e}", exc_info=True)
            continue # Pula para a próxima resposta em caso de erro nesta
        # --- FIM DAS CHAMADAS ---

    # Verifica se alguma resposta válida foi processada
    if valid_responses_processed == 0:
         logger.error(f"Nenhuma resposta válida pôde ser processada (total recebido: {len(responses)}). Verifique o formato do JSON de entrada ou a função 'get_profile_for_word' em disc_data.py. Scores finais serão zerados.")
         # Continua para retornar um resultado com scores zerados, mas loga o erro.
         # Alternativamente: return None # Para indicar falha total
    elif valid_responses_processed < len(responses):
         logger.warning(f"Foram processadas apenas {valid_responses_processed} de {len(responses)} respostas. Verifique warnings anteriores sobre formatos ou perfis não encontrados.")


    # Verifica se algum score foi calculado (após processar respostas válidas)
    # Mesmo que scores sejam zero, ainda é um resultado válido (perfil neutro/erro no mapeamento)
    if not any(v != 0 for v in disc_scores.values()):
         logger.warning(f"Todos os scores DISC finais são zero após processar {valid_responses_processed} respostas válidas. Scores: {disc_scores}. Isso pode indicar cancelamento total ou falha no mapeamento em disc_data.py.")

    # --- Identificação dos perfis predominantes ---
    try:
        # Garante que todos os perfis D, I, S, C estão presentes com score 0 se não foram alterados
        all_scores = {p: disc_scores.get(p, 0) for p in ['D', 'I', 'S', 'C']}
        # Ordena por score (maior primeiro) e depois alfabeticamente como desempate
        sorted_profiles = sorted(all_scores.items(), key=lambda item: (-item[1], item[0]))

        primary_profile = sorted_profiles[0][0]
        # Encontra o primeiro perfil diferente do primário na lista ordenada
        secondary_profile = primary_profile # Default se todos tiverem o mesmo score
        for profile, score in sorted_profiles[1:]:
             # A condição `score < sorted_profiles[0][1]` garante que só pegamos um secundário se o score for menor
             # Se houver empate no score primário, o desempate alfabético já ocorreu.
             # Se queremos o *próximo* score mais alto diferente, mesmo que igual ao primário (ex: D=5, I=5, S=2),
             # precisamos de lógica diferente. Assumindo que secundário é o *segundo mais alto*.
            if profile != primary_profile: # Pega o primeiro diferente
                 secondary_profile = profile
                 break
            # Se todos os scores forem iguais, secundário será igual ao primário.

    except Exception as e:
        logger.error(f"Erro ao determinar perfis primário/secundário a partir dos scores {disc_scores}: {e}", exc_info=True)
        primary_profile = 'D' # Fallback seguro
        secondary_profile = 'I' # Fallback seguro

    # ---- GERAÇÃO DO RESULTADO FINAL ----
    # Chaves consistentes que o model DISCResult espera
    result_base = {
        'd_score': all_scores.get('D', 0),
        'i_score': all_scores.get('I', 0),
        's_score': all_scores.get('S', 0),
        'c_score': all_scores.get('C', 0),
        'primary_profile': primary_profile,      # Chave esperada pelo Model
        'secondary_profile': secondary_profile,  # Chave esperada pelo Model
        # Não incluir todas as descrições aqui, elas são estáticas e podem ser pegas no template
        # 'profile_interpretations': disc_descriptions, # REMOVIDO daqui
        # >>> CORREÇÃO APLICADA AQUI <<<
        # Converter datetime para string ISO 8601 para ser serializável em JSON
        'calculation_timestamp_iso': datetime.now().isoformat() # Nome mais explícito
        # >>> FIM DA CORREÇÃO <<<
    }

    # Gera o relatório detalhado (função auxiliar não modificada, assume que está ok)
    # Passa as descrições para a função de relatório, se necessário
    detailed_report_data = generate_detailed_report(result_base, disc_descriptions) # Passa descrições explicitamente

    # Combina o resultado base com o relatório detalhado
    # O model DISCResult salvará este dicionário inteiro no campo JSON
    final_result = {
        **result_base,
        'detailed_report': detailed_report_data
     }

    logger.info(f"Scores DISC calculados: D={final_result['d_score']}, I={final_result['i_score']}, S={final_result['s_score']}, C={final_result['c_score']}. Primário: {primary_profile}, Secundário: {secondary_profile}. Processadas {valid_responses_processed}/{len(responses)} respostas.")
    # Log do resultado final antes de retornar
    logger.debug(f"Retornando resultado final: {final_result}")
    return final_result


# --- Funções Auxiliares (get_profile_summary, generate_detailed_report) ---
# Modificar generate_detailed_report para aceitar descrições

def get_profile_summary(disc_result: Dict[str, Any], descriptions: Dict) -> str:
    """Gera um resumo textual do perfil DISC."""
    # Verifica as chaves esperadas no disc_result que vem do CALCULATOR
    if not disc_result or not all(k in disc_result for k in ['primary_profile', 'secondary_profile', 'd_score', 'i_score', 's_score', 'c_score']):
        logger.error("Dados de resultado inválidos para gerar resumo.")
        return "Não foi possível gerar o resumo do perfil (dados de resultado inválidos)."

    primary = disc_result['primary_profile']
    secondary = disc_result['secondary_profile']
    scores = {
        'D': disc_result['d_score'], 'I': disc_result['i_score'],
        'S': disc_result['s_score'], 'C': disc_result['c_score']
    }
    # Usa as descrições passadas como argumento
    if not descriptions: descriptions = {} # Fallback

    primary_title = descriptions.get(primary, {}).get('title', primary)
    secondary_title = descriptions.get(secondary, {}).get('title', secondary)

    summary = f"Seu perfil DISC é predominantemente **{primary_title} ({primary})**"
    if primary != secondary:
         summary += f", com uma influência secundária significativa de **{secondary_title} ({secondary})**.\n\n"
    else:
         summary += ".\n\n"

    summary += "**Intensidade por Fator (Scores):**\n"
    # Garante a ordem D, I, S, C
    for factor in ['D', 'I', 'S', 'C']:
        factor_name = descriptions.get(factor, {}).get('title', factor)
        score = scores.get(factor, 'N/A')
        summary += f"- **{factor} ({factor_name}):** {score}\n" # Mostra o score diretamente

    primary_desc_data = descriptions.get(primary, {})
    if primary_desc_data:
        summary += f"\nComo perfil **{primary}** dominante, você tende a ser motivado(a) por: *{primary_desc_data.get('motivation', 'N/A')}*.\n"
    else:
         logger.warning(f"Descrição não encontrada para o perfil primário: {primary}")


    if primary != secondary:
        secondary_desc_data = descriptions.get(secondary, {})
        if secondary_desc_data:
             summary += f"\nSua influência secundária **{secondary}** pode adicionar traços relacionados à motivação por: *{secondary_desc_data.get('motivation', 'N/A')}*.\n"
        else:
             logger.warning(f"Descrição não encontrada para o perfil secundário: {secondary}")


    return summary

def generate_detailed_report(disc_result_base: Dict[str, Any], descriptions: Dict) -> Dict[str, Any]:
    """
    Gera um relatório mais detalhado do perfil DISC. Recebe o dicionário base
    com scores e perfis já calculados, e as descrições.
    """
    # Verifica chaves no dict BASE
    if not disc_result_base or not all(k in disc_result_base for k in ['primary_profile', 'secondary_profile']):
        logger.error("Dados de resultado base inválidos para gerar relatório detalhado.")
        return {"error": "Dados de resultado inválidos para gerar relatório detalhado."}

    primary = disc_result_base['primary_profile']
    secondary = disc_result_base['secondary_profile']
    # Usa as descrições passadas como argumento
    if not descriptions: descriptions = {} # Fallback

    primary_desc = descriptions.get(primary, {})
    secondary_desc = descriptions.get(secondary, {})

    # Cria o resumo usando os dados base e as descrições passadas
    profile_summary_text = get_profile_summary(disc_result_base, descriptions)

    # Usa .get com fallback para listas vazias para evitar erros no template
    report = {
        'profile_summary': profile_summary_text,
        'primary_profile_details': {
            'title': primary_desc.get('title', primary),
            'description': primary_desc.get('description', 'N/A'), # Adicionado description
            'motivation': primary_desc.get('motivation', 'N/A'),
            'characteristics': primary_desc.get('characteristics', []),
            'strengths': primary_desc.get('strengths', []),
            'weaknesses': primary_desc.get('weaknesses', []),
            'how_to_work_with': primary_desc.get('how_to_work_with', []) # Usa lista vazia
        },
        'secondary_profile_details': None, # Preenchido se for diferente do primário
        'development_areas_list': [],
    }

    if primary != secondary and secondary_desc:
         report['secondary_profile_details'] = {
             'title': secondary_desc.get('title', secondary),
             'description': secondary_desc.get('description', 'N/A'), # Adicionado description
             'motivation': secondary_desc.get('motivation', 'N/A'),
             'characteristics': secondary_desc.get('characteristics', []),
             'strengths': secondary_desc.get('strengths', []),
             'weaknesses': secondary_desc.get('weaknesses', []),
             'how_to_work_with': secondary_desc.get('how_to_work_with', []) # Usa lista vazia
        }
    elif primary != secondary:
        logger.warning(f"Descrição não encontrada para perfil secundário '{secondary}' ao gerar detalhes.")
        # Adiciona um placeholder para evitar erro no template se ele tentar acessar
        report['secondary_profile_details'] = {
            'title': secondary, 'description':'Detalhes não disponíveis.', 'motivation': 'N/A',
            'characteristics': [], 'strengths': [], 'weaknesses': [], 'how_to_work_with': []
        }


    # Adiciona áreas de desenvolvimento genéricas baseadas no perfil primário
    development_areas = []
    if primary_desc: # Adiciona apenas se a descrição primária foi encontrada
        weaknesses = primary_desc.get('weaknesses', [])
        if weaknesses:
             # Formata como lista de strings
             development_areas.extend([f"Considerar formas de mitigar: {w}" for w in weaknesses])
        else:
             development_areas.append(f"Nenhuma fraqueza específica listada para o perfil {primary} para sugerir desenvolvimento.")

        # Adiciona sugestões mais direcionadas (exemplo)
        if primary == 'D': development_areas.append("Praticar a escuta ativa, a paciência e considerar o impacto das decisões nas pessoas.")
        elif primary == 'I': development_areas.append("Melhorar a organização, o foco em detalhes e o acompanhamento de tarefas até a conclusão.")
        elif primary == 'S': development_areas.append("Desenvolver maior assertividade ao expressar necessidades, adaptabilidade a mudanças rápidas e iniciativa.")
        elif primary == 'C': development_areas.append("Ser mais flexível com regras quando apropriado, tomar decisões com dados suficientes (sem paralisia por análise) e expressar mais o raciocínio.")

    else:
        logger.warning(f"Não foi possível adicionar áreas de desenvolvimento pois a descrição do perfil primário {primary} não foi encontrada.")

    # Lógica mais sofisticada pode combinar primário e secundário (Exemplo)
    if primary != secondary and secondary_desc:
        if primary == 'D' and secondary == 'S':
            development_areas.append("Buscar equilibrar a busca por resultados (D) com a manutenção da harmonia e apoio da equipe (S).")
        # Adicionar outras combinações aqui se desejar...
        pass # Só um exemplo

    # Garante que sempre seja uma lista
    report['development_areas_list'] = development_areas if development_areas else ["Nenhuma sugestão específica gerada."]

    return report