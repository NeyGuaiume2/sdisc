# Modelo de avaliação DISC 
class DISCAssessment:
    """
    Modelo para representar uma avaliação DISC.
    Inicialmente, usaremos uma classe simples sem ORM.
    """
    
    def __init__(self, user_id=None, name=None):
        self.user_id = user_id
        self.name = name
        self.responses = {}  # Armazenar respostas por ID da questão
        self.scores = {      # Pontuações calculadas
            'D': 0,  # Dominância
            'I': 0,  # Influência
            'S': 0,  # Estabilidade
            'C': 0   # Conformidade
        }
        self.timestamp = None
    
    def add_response(self, question_id, most, least):
        """Adiciona uma resposta do questionário"""
        self.responses[question_id] = {
            'most': most,
            'least': least
        }
    
    def calculate_scores(self):
        """Calcula as pontuações DISC com base nas respostas"""
        # Mapeamento de letra para fator DISC
        letter_to_disc = {
            'A': 'D',  # Dominância
            'B': 'I',  # Influência
            'C': 'S',  # Estabilidade
            'D': 'C'   # Conformidade
        }
        
        # Inicializar contadores
        disc_counts = {
            'D': {'most': 0, 'least': 0},
            'I': {'most': 0, 'least': 0},
            'S': {'most': 0, 'least': 0},
            'C': {'most': 0, 'least': 0}
        }
        
        # Contar as respostas MAIS e MENOS
        for question_id, answer in self.responses.items():
            if 'most' in answer:
                letter = answer['most']
                disc_factor = letter_to_disc[letter]
                disc_counts[disc_factor]['most'] += 1
            
            if 'least' in answer:
                letter = answer['least']
                disc_factor = letter_to_disc[letter]
                disc_counts[disc_factor]['least'] += 1
        
        # Calcular os resultados finais (MAIS - MENOS)
        self.scores = {
            'D': disc_counts['D']['most'] - disc_counts['D']['least'],
            'I': disc_counts['I']['most'] - disc_counts['I']['least'],
            'S': disc_counts['S']['most'] - disc_counts['S']['least'],
            'C': disc_counts['C']['most'] - disc_counts['C']['least']
        }
        
        return self.scores
    
    def get_primary_profile(self):
        """Retorna o perfil comportamental predominante"""
        if not any(self.scores.values()):
            return None
        
        # Encontrar o fator com maior pontuação
        primary = max(self.scores, key=self.scores.get)
        return primary
    
    def to_dict(self):
        """Converter para dicionário para serialização"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'responses': self.responses,
            'scores': self.scores,
            'primary_profile': self.get_primary_profile(),
            'timestamp': self.timestamp
        }