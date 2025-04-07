# backend/models/disc_result.py (Refatorado e mais robusto)

import json
from datetime import datetime
import logging # Adicionado para logging
from typing import Dict, Any, Optional, List # Melhora type hinting
from sqlalchemy.types import Text # Import Text explicitamente

# Import relativo seguro
try:
    # Se db.py está no mesmo nível que a pasta 'models' dentro de 'backend'
    from ..db import db
except (ImportError, ValueError):
    # Fallback se a estrutura for diferente ou executado como script
    try:
        from backend.db import db
    except ImportError:
        logging.critical("Falha crítica ao importar 'db' em disc_result.py. Verifique a estrutura do projeto e PYTHONPATH.")
        # Em um app real, talvez queira um erro mais explícito ou sair
        raise

# Configuração do logger para este módulo
logger = logging.getLogger(__name__)


class DISCResult(db.Model):
    """
    Modelo SQLAlchemy para armazenar resultados da avaliação DISC no banco de dados.

    Armazena as respostas brutas e os resultados calculados completos como JSON,
    mantendo os perfis principais como colunas separadas para acesso rápido.
    """
    __tablename__ = 'disc_results'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(120), nullable=True) # Tamanho ligeiramente aumentado
    user_email = db.Column(db.String(120), nullable=True, index=True) # Indexado para buscas
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True) # Não nulo, indexado

    # Respostas brutas fornecidas pelo usuário (JSON armazenado como string)
    # Renomeado de raw_responses para clareza que é JSON string
    raw_responses_json = db.Column(Text, nullable=False)

    # Resultados calculados completos (todo o dict retornado por calculate_disc_scores)
    # Armazenado como string JSON. Inclui scores, perfis, relatório detalhado, etc.
    calculated_result_json = db.Column(Text, nullable=False)

    # Perfis principais extraídos do JSON para acesso rápido e consultas
    # Mantidos como colunas separadas e indexadas.
    primary_type = db.Column(db.String(1), nullable=False, index=True) # Não nulo, indexado
    secondary_type = db.Column(db.String(1), nullable=False)           # Não nulo

    # Definição explícita de índices (alternativa ou complemento aos inline index=True)
    # __table_args__ = (
    #     db.Index('ix_disc_results_user_email', 'user_email'),
    #     db.Index('ix_disc_results_timestamp', 'timestamp'),
    #     db.Index('ix_disc_results_primary_type', 'primary_type'),
    # )

    def __init__(self,
                 user_name: Optional[str] = None,
                 user_email: Optional[str] = None,
                 raw_responses: Optional[List[Dict[str, Any]]] = None, # Espera lista de dicts
                 disc_result: Optional[Dict[str, Any]] = None):       # Espera o dict calculado
        """
        Inicializa uma nova instância de DISCResult.

        Args:
            user_name: Nome do usuário (opcional).
            user_email: Email do usuário (opcional).
            raw_responses: Lista de dicionários das respostas brutas do usuário.
            disc_result: Dicionário completo contendo os resultados calculados
                         pela função `calculate_disc_scores`.
        """
        self.user_name = user_name
        self.user_email = user_email
        # Garante que o timestamp seja definido na criação da instância Python
        # O default=datetime.utcnow no db.Column lida com o nível do DB
        self.timestamp = datetime.utcnow()

        # --- Processamento de raw_responses ---
        # Garante que raw_responses seja uma lista antes de tentar serializar
        if raw_responses is not None and isinstance(raw_responses, list):
            try:
                self.raw_responses_json = json.dumps(raw_responses)
            except (TypeError, OverflowError) as e:
                logger.error(f"Erro ao serializar 'raw_responses' para JSON: {e}. Armazenando lista vazia.")
                self.raw_responses_json = '[]' # Default seguro
        else:
            logger.warning(f"Tipo '{type(raw_responses)}' inválido ou não fornecido para 'raw_responses'. Armazenando lista vazia.")
            self.raw_responses_json = '[]' # Default seguro

        # --- Processamento de disc_result ---
        # Define valores padrão indicando erro/incompleto
        default_primary = '?' # Indica erro/ausência
        default_secondary = '?' # Indica erro/ausência
        default_result_json = '{}' # JSON vazio como default

        if disc_result and isinstance(disc_result, dict):
            try:
                # **Acesso às chaves retornadas por calculate_disc_scores**
                # Usa .get() para segurança, fallback para default_primary/secondary
                primary = disc_result.get('primary_profile', default_primary)
                secondary = disc_result.get('secondary_profile', default_secondary)

                # Validação simples do tipo e tamanho dos perfis extraídos
                if not isinstance(primary, str) or len(primary) != 1 or primary not in ['D', 'I', 'S', 'C']:
                    logger.error(f"Valor de 'primary_profile' inválido ('{primary}') no dicionário disc_result. Usando fallback '{default_primary}'.")
                    self.primary_type = default_primary
                else:
                    self.primary_type = primary

                if not isinstance(secondary, str) or len(secondary) != 1 or secondary not in ['D', 'I', 'S', 'C']:
                    logger.error(f"Valor de 'secondary_profile' inválido ('{secondary}') no dicionário disc_result. Usando fallback '{default_secondary}'.")
                    self.secondary_type = default_secondary
                else:
                    self.secondary_type = secondary

                # Serializa o dicionário *completo* para a coluna JSON
                self.calculated_result_json = json.dumps(disc_result)
                logger.debug(f"Resultado DISC processado e serializado. Primário: {self.primary_type}, Secundário: {self.secondary_type}")

            except (TypeError, OverflowError) as e:
                logger.error(f"Erro ao serializar 'disc_result' para JSON: {e}. Armazenando objeto vazio e perfis de fallback.", exc_info=True)
                self.calculated_result_json = default_result_json
                self.primary_type = default_primary
                self.secondary_type = default_secondary
            except Exception as e: # Captura outras exceções inesperadas durante o processamento
                logger.exception(f"Erro inesperado ao processar 'disc_result': {e}")
                self.calculated_result_json = default_result_json
                self.primary_type = default_primary
                self.secondary_type = default_secondary
        else:
            # Se disc_result for None ou não for um dicionário vindo do calculador
            logger.error(f"Dicionário 'disc_result' inválido ({type(disc_result)}) ou não fornecido por calculate_disc_scores. Armazenando dados vazios e perfis de fallback ('?').")
            self.calculated_result_json = default_result_json
            self.primary_type = default_primary
            self.secondary_type = default_secondary

    # --- Métodos Getters para acessar dados desserializados com cache e erro handling ---

    def get_raw_responses(self) -> Optional[List[Dict[str, Any]]]:
        """
        Retorna as respostas brutas desserializadas como um objeto Python (lista de dicts).
        Retorna None em caso de erro na desserialização. Cacheia o resultado ou o erro.
        """
        # Usa um nome de cache prefixado com _
        if not hasattr(self, '_cached_raw_responses'):
             try:
                 # Usa or '[]' para evitar erro se raw_responses_json for None (não deveria ser, mas por segurança)
                 self._cached_raw_responses = json.loads(self.raw_responses_json or '[]')
             except (json.JSONDecodeError, TypeError) as e:
                 logger.error(f"Erro ao desserializar raw_responses_json (ID: {self.id}): {e}. Conteúdo: '{self.raw_responses_json[:100]}...'")
                 self._cached_raw_responses = None # Cacheia o erro (None)
        return self._cached_raw_responses

    def get_calculated_result(self) -> Optional[Dict[str, Any]]:
        """
        Retorna o dicionário completo de resultados calculados desserializado.
        Retorna None em caso de erro na desserialização. Cacheia o resultado ou o erro.
        """
        # Usa um cache simples na instância para evitar desserialização repetida
        if not hasattr(self, '_cached_calculated_result'):
            try:
                # Usa or '{}' para evitar erro se for None
                self._cached_calculated_result = json.loads(self.calculated_result_json or '{}')
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Erro ao desserializar calculated_result_json (ID: {self.id}): {e}. Conteúdo: '{self.calculated_result_json[:100]}...'")
                self._cached_calculated_result = None # Cacheia o erro (None)
        return self._cached_calculated_result

    # --- Métodos de conveniência para acessar partes do resultado calculado ---

    def get_scores(self) -> Optional[Dict[str, int]]:
        """
        Retorna um dicionário com os scores D, I, S, C extraídos do resultado calculado.
        Retorna um dicionário com scores 0 se o resultado não puder ser carregado ou
        não contiver as chaves esperadas (d_score, i_score, s_score, c_score).
        Retorna None apenas se a desserialização falhar completamente.
        """
        result = self.get_calculated_result() # Obtem do cache/desserializa
        if result is None:
             logger.warning(f"Não foi possível obter resultado calculado (ID: {self.id}) para extrair scores.")
             return None # Falha na desserialização

        # Se result é um dict (mesmo vazio), tenta pegar os scores
        if isinstance(result, dict):
            # Usa .get() com default 0 para robustez
            scores = {
                'D': result.get('d_score', 0), # Chave retornada pelo calculador
                'I': result.get('i_score', 0), # Chave retornada pelo calculador
                'S': result.get('s_score', 0), # Chave retornada pelo calculador
                'C': result.get('c_score', 0), # Chave retornada pelo calculador
            }
            # Loga um aviso se todos os scores forem 0, pois pode indicar problema
            if all(s == 0 for s in scores.values()) and self.calculated_result_json != '{}':
                logger.warning(f"Scores extraídos são todos zero para ID {self.id}. Verifique o cálculo original ou o JSON armazenado: {self.calculated_result_json[:100]}...")
            return scores
        else:
            # Caso result não seja um dict após desserialização (improvável mas seguro)
            logger.error(f"Resultado calculado (ID: {self.id}) desserializado não é um dicionário ({type(result)}). Não é possível extrair scores.")
            return {'D': 0, 'I': 0, 'S': 0, 'C': 0} # Retorna scores zerados como fallback

    def get_detailed_report(self) -> Optional[Dict[str, Any]]:
        """
        Retorna o relatório detalhado extraído do resultado calculado (chave 'detailed_report').
        Retorna None se o resultado não puder ser carregado ou não contiver um dict válido
        na chave 'detailed_report'.
        """
        result = self.get_calculated_result() # Obtem do cache/desserializa
        if result is None:
             logger.warning(f"Não foi possível obter resultado calculado (ID: {self.id}) para extrair relatório detalhado.")
             return None # Falha na desserialização

        if isinstance(result, dict):
            report = result.get('detailed_report') # Chave retornada pelo calculador
            if isinstance(report, dict):
                return report
            else:
                 logger.warning(f"Chave 'detailed_report' não encontrada ou não é um dicionário no resultado calculado (ID: {self.id}). Valor: {report}")
                 return None # Retorna None se não for um dict
        else:
            logger.error(f"Resultado calculado (ID: {self.id}) desserializado não é um dicionário ({type(result)}). Não é possível extrair relatório.")
            return None

    # Opcional: Método para obter o resumo diretamente
    def get_profile_summary(self) -> Optional[str]:
        """Retorna o resumo textual do perfil extraído do relatório detalhado."""
        report = self.get_detailed_report()
        if report and isinstance(report, dict):
            summary = report.get('profile_summary')
            if isinstance(summary, str):
                return summary
            else:
                logger.warning(f"Chave 'profile_summary' encontrada no relatório (ID: {self.id}), mas não é uma string ({type(summary)}).")
                return None
        # Log implícito no get_detailed_report se falhar
        return None

    # --- Método de Serialização para Saída (ex: API) ---
    # (Não modificado significativamente, mas usa os getters aprimorados)
    def to_dict(self, include_raw_responses: bool = False) -> Dict[str, Any]:
        """
        Converte a instância do modelo em um dicionário Python.
        Args:
            include_raw_responses: Se True, inclui as respostas brutas desserializadas.
                                   Default é False por privacidade e tamanho.
        Returns:
            Um dicionário representando o objeto DISCResult.
        """
        calculated_result_data = self.get_calculated_result() # Usa getter com cache/erro handling

        data = {
            'id': self.id,
            'user_name': self.user_name,
            # Considerar omitir email em APIs públicas
            # 'user_email': self.user_email, # Omitido por padrão
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'primary_type': self.primary_type, # Vem direto da coluna
            'secondary_type': self.secondary_type, # Vem direto da coluna
            # Inclui o dicionário completo calculado, ou um erro se falhou ao carregar
            'calculated_result': calculated_result_data if calculated_result_data is not None else {
                "error": f"Falha ao carregar/desserializar dados do resultado calculado para ID {self.id}"
            }
            # Você poderia optar por incluir apenas partes específicas aqui usando os getters:
            # 'scores': self.get_scores(),
            # 'summary': self.get_profile_summary(),
        }

        if include_raw_responses:
            raw_responses_data = self.get_raw_responses() # Usa getter com cache/erro handling
            data['raw_responses'] = raw_responses_data if raw_responses_data is not None else {
                 "error": f"Falha ao carregar/desserializar respostas brutas para ID {self.id}"
            }

        return data

    def __repr__(self) -> str:
        """Representação textual da instância para debugging."""
        return (f"<DISCResult(id={self.id}, "
                f"user='{self.user_name or self.user_email or 'Anonymous'}', "
                f"primary='{self.primary_type}', secondary='{self.secondary_type}', "
                f"timestamp='{self.timestamp.strftime('%Y-%m-%d %H:%M') if self.timestamp else 'N/A'}')>")