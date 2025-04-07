# backend/interpretation_loader.py
import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Determina o diretório base do projeto ou do módulo atual
# Isso pode precisar de ajuste dependendo de como você executa o app
try:
    # Assume que este arquivo está em backend/
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'interpretations_data')
except NameError:
    # Fallback se __file__ não estiver definido (ex: execução interativa)
    BASE_DIR = os.getcwd()
    DATA_DIR = os.path.join(BASE_DIR, 'backend', 'interpretations_data')

# Cache simples para evitar recarregar arquivos a cada request
_interpretation_cache: Dict[str, Optional[Dict[str, Any]]] = {}

def _load_json_data(filename: str) -> Optional[Dict[str, Any]]:
    """Carrega dados de um arquivo JSON no diretório de dados."""
    if filename in _interpretation_cache:
        return _interpretation_cache[filename]

    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        logger.error(f"Arquivo de interpretação não encontrado: {filepath}")
        _interpretation_cache[filename] = None
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _interpretation_cache[filename] = data
            logger.info(f"Carregado com sucesso: {filename}")
            return data
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
        logger.error(f"Erro ao carregar ou decodificar JSON de {filepath}: {e}", exc_info=True)
        _interpretation_cache[filename] = None
        return None

# Funções para obter os dados específicos (usam o loader)
def get_general_primary_data() -> Optional[Dict[str, Any]]:
    return _load_json_data('general_primary.json')

def get_general_secondary_data() -> Optional[Dict[str, Any]]:
    # ATENÇÃO: O nome do arquivo deve corresponder ao JSON criado a partir de perfis_secundarios.md
    return _load_json_data('general_secondary_combinations.json') # Nome exemplo

def get_professional_primary_data() -> Optional[Dict[str, Any]]:
    return _load_json_data('professional_primary.json')

def get_professional_secondary_data() -> Optional[Dict[str, Any]]:
    # ATENÇÃO: O nome do arquivo deve corresponder ao JSON criado a partir de perfis_profissionais_secundarios.md
    return _load_json_data('professional_secondary_combinations.json') # Nome exemplo

# Adicione aqui funções para carregar outros JSONs se necessário