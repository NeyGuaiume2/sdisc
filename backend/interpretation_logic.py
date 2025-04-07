# backend/interpretation_logic.py
import logging
from typing import Dict, Any, Optional

# Importa o loader e outras dependências se necessário
try:
    from .interpretation_loader import (
        get_general_primary_data,
        get_general_secondary_data,
        get_professional_primary_data,
        get_professional_secondary_data
    )
    from .disc_data import disc_descriptions
except ImportError:
    logging.exception("Falha ao importar interpretation_loader ou disc_data em interpretation_logic.py.")
    # Fallback (ajuste conforme necessário)
    from backend.interpretation_loader import (
        get_general_primary_data,
        get_general_secondary_data,
        get_professional_primary_data,
        get_professional_secondary_data
    )
    from backend.disc_data import disc_descriptions

logger = logging.getLogger(__name__)

# --- Função Auxiliar de Intensidade (mantida) ---
def get_intensity_key(score: Optional[int]) -> Optional[str]:
    """
    Determina a chave de intensidade ('moderate', 'significant', 'high') com base na pontuação.
    Retorna None se o score for inválido ou None.
    """
    if score is None:
        return None

    # Faixas confirmadas: 0-8, 9-15, 16+ (Ajuste se as faixas mudarem!)
    if 0 <= score <= 8:
        return 'moderate'
    elif 9 <= score <= 15:
        return 'significant'
    elif score >= 16:
        return 'high'
    else:
        # Trata scores negativos ou outros inesperados como 'moderate' por segurança, mas loga
        logger.warning(f"Pontuação inválida ou inesperada encontrada: {score}. Determinando nível baseado em 0 ou mais próximo.")
        # Lógica de fallback para negativos (pode ajustar):
        if score < 0: return 'moderate' # Ou a faixa mais baixa que fizer sentido
        # Se por algum motivo score for > maximo esperado, considera high
        if score > 28: return 'high' # Ajuste 28 se o máximo for outro
        # Fallback geral
        return 'moderate'

# --- Função Principal Refatorada ---

def get_all_interpretations(
    primary_type: Optional[str],
    secondary_type: Optional[str],
    disc_scores: Dict[str, int]
) -> Dict[str, Any]:
    """
    Gera um dicionário completo com interpretações gerais e profissionais
    para os perfis primário e secundário, baseados em tipo e intensidade.

    Args:
        primary_type: 'D', 'I', 'S', 'C' ou None/'?'.
        secondary_type: 'D', 'I', 'S', 'C' ou None/'?'.
        disc_scores: Dicionário com scores {'D': score, 'I': score, ...}.

    Returns:
        Dicionário com chaves 'general' e 'professional', cada uma contendo
        'primary' e 'secondary' interpretations. Retorna estruturas vazias
        em caso de erro ou dados ausentes.
    """
    all_interpretations = {
        'general': {'primary': {}, 'secondary': {}},
        'professional': {'primary': {}, 'secondary': {}}
    }

    # Carrega todos os dados necessários no início
    gen_primary_data = get_general_primary_data()
    gen_secondary_data = get_general_secondary_data()
    prof_primary_data = get_professional_primary_data()
    prof_secondary_data = get_professional_secondary_data()

    # --- Validação e Cálculo de Níveis ---
    if not primary_type or primary_type not in ['D', 'I', 'S', 'C']:
        logger.error(f"Tipo primário inválido: {primary_type}. Não é possível gerar interpretações.")
        return all_interpretations

    primary_score = disc_scores.get(primary_type)
    primary_intensity_key = get_intensity_key(primary_score) # Ex: 'high'

    if not primary_intensity_key:
         logger.error(f"Não foi possível determinar a intensidade para o perfil primário {primary_type} com score {primary_score}.")
         return all_interpretations # Não podemos prosseguir sem intensidade primária

    logger.info(f"Gerando interpretações para Primário: {primary_type} ({primary_intensity_key}), Secundário: {secondary_type or 'Nenhum'}")

    # --- Processamento Primário (sem alterações) ---
    primary_key = primary_type # Ex: 'D'
    primary_level_key = primary_intensity_key # Ex: 'high'

    # Geral Primário
    if gen_primary_data and primary_key in gen_primary_data and primary_level_key in gen_primary_data[primary_key]:
        all_interpretations['general']['primary'] = gen_primary_data[primary_key][primary_level_key].copy()
        all_interpretations['general']['primary']['type'] = primary_type
        all_interpretations['general']['primary']['level'] = primary_level_key
        all_interpretations['general']['primary']['score'] = primary_score
        all_interpretations['general']['primary']['title'] = disc_descriptions.get(primary_type, {}).get('title', primary_type)
    else:
        logger.warning(f"Dados gerais primários não encontrados para {primary_key} - {primary_level_key}")

    # Profissional Primário
    if prof_primary_data and primary_key in prof_primary_data and primary_level_key in prof_primary_data[primary_key]:
        all_interpretations['professional']['primary'] = prof_primary_data[primary_key][primary_level_key].copy()
        all_interpretations['professional']['primary']['type'] = primary_type
        all_interpretations['professional']['primary']['level'] = primary_level_key
    else:
        logger.warning(f"Dados profissionais primários não encontrados para {primary_key} - {primary_level_key}")


    # --- Processamento Secundário (REVISADO CONFORME EXPLICAÇÃO) ---
    if secondary_type and secondary_type in ['D', 'I', 'S', 'C'] and secondary_type != primary_type:
        # Chave para os dados de combinação secundária USA o nível do PRIMÁRIO
        primary_combination_key = f"{primary_type}_{primary_intensity_key}" # Ex: "D_high"
        # Chave secundária é APENAS o TIPO secundário
        secondary_lookup_key = secondary_type # Ex: "C"

        # Calcula o score e nível secundário APENAS para informação adicional
        secondary_score = disc_scores.get(secondary_type)
        secondary_intensity_level = get_intensity_key(secondary_score)

        logger.info(f"Tentando encontrar interpretação secundária para combinação: Primário='{primary_combination_key}', Secundário (Tipo)='{secondary_lookup_key}'")

        # Geral Secundário (Combinação) - LÓGICA DE BUSCA CORRIGIDA
        if gen_secondary_data and primary_combination_key in gen_secondary_data and secondary_lookup_key in gen_secondary_data[primary_combination_key]:
            # Pega o valor (texto ou objeto) associado a esta combinação
            secondary_interpretation_data = gen_secondary_data[primary_combination_key][secondary_lookup_key]

            # Monta o dicionário de resultado secundário geral
            if isinstance(secondary_interpretation_data, str):
                # Se for apenas um texto, coloca na chave 'Descrição'
                all_interpretations['general']['secondary'] = {
                    'Descrição': secondary_interpretation_data
                }
                logger.debug(f"Interpretação secundária geral encontrada como string para {primary_combination_key} + {secondary_lookup_key}")
            elif isinstance(secondary_interpretation_data, dict):
                # Se for um dicionário (mais flexível), copia ele
                all_interpretations['general']['secondary'] = secondary_interpretation_data.copy()
                logger.debug(f"Interpretação secundária geral encontrada como dict para {primary_combination_key} + {secondary_lookup_key}")
            else:
                logger.error(f"Tipo inesperado ({type(secondary_interpretation_data)}) encontrado para interpretação secundária geral [{primary_combination_key}][{secondary_lookup_key}]")
                all_interpretations['general']['secondary'] = {} # Define como vazio em caso de tipo inesperado

            # Adiciona informações extras SEMPRE, se o dict existir
            if all_interpretations['general']['secondary'] is not None and isinstance(all_interpretations['general']['secondary'], dict):
                all_interpretations['general']['secondary']['type'] = secondary_type
                all_interpretations['general']['secondary']['level'] = secondary_intensity_level # Nível do secundário (calculado)
                all_interpretations['general']['secondary']['score'] = secondary_score
                all_interpretations['general']['secondary']['title'] = disc_descriptions.get(secondary_type, {}).get('title', secondary_type)

        else:
            logger.warning(f"Dados gerais secundários (combinação) não encontrados em gen_secondary_data['{primary_combination_key}']['{secondary_lookup_key}']")
            # Garante que fique vazio se não encontrado
            all_interpretations['general']['secondary'] = {}


        # Profissional Secundário (Combinação) - LÓGICA DE BUSCA CORRIGIDA (ASSUMINDO MESMA ESTRUTURA DE CHAVE)
        if prof_secondary_data and primary_combination_key in prof_secondary_data and secondary_lookup_key in prof_secondary_data[primary_combination_key]:
             # Pega o objeto/dict profissional secundário
             secondary_prof_data = prof_secondary_data[primary_combination_key][secondary_lookup_key]

             if isinstance(secondary_prof_data, dict):
                  all_interpretations['professional']['secondary'] = secondary_prof_data.copy()
                  # Adiciona/Garante info extra
                  all_interpretations['professional']['secondary']['type'] = secondary_type
                  all_interpretations['professional']['secondary']['level'] = secondary_intensity_level
                  # Não costuma precisar de title/score aqui, mas pode adicionar se necessário
                  logger.debug(f"Interpretação secundária profissional encontrada como dict para {primary_combination_key} + {secondary_lookup_key}")
             # Adapte aqui se o JSON profissional secundário for apenas uma string também
             # elif isinstance(secondary_prof_data, str):
             #      all_interpretations['professional']['secondary'] = {'Descrição': secondary_prof_data, ...}
             else:
                  logger.error(f"Tipo inesperado ({type(secondary_prof_data)}) encontrado para interpretação secundária profissional [{primary_combination_key}][{secondary_lookup_key}]")
                  all_interpretations['professional']['secondary'] = {}

        else:
            logger.warning(f"Dados profissionais secundários (combinação) não encontrados em prof_secondary_data['{primary_combination_key}']['{secondary_lookup_key}']")
            # Garante que fique vazio se não encontrado
            all_interpretations['professional']['secondary'] = {}

    # Garante que as chaves 'secondary' existam mesmo se não houve secundário válido
    if 'secondary' not in all_interpretations['general']:
        all_interpretations['general']['secondary'] = {}
    if 'secondary' not in all_interpretations['professional']:
        all_interpretations['professional']['secondary'] = {}


    return all_interpretations