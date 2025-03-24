"""
Dados do questionário DISC baseados na metodologia de William Moulton Marston.
Contém as 25 perguntas (cartões) da avaliação DISC com 4 opções cada.

A = Dominância
B = Influência
C = Estabilidade
D = Conformidade
"""

# Cartões de instruções para exibir antes do questionário
instruction_cards = [
    {
        "id": 1,
        "content": "A avaliação DISC é uma metodologia criada por William Moulton Marston, pesquisador da Universidade de Harvard."
    },
    {
        "id": 2,
        "content": "Em cada tela da apresentação há quatro adjetivos. Marque o que MAIS tem a ver com você na coluna esquerda e o que MENOS tem a ver com você na coluna direita."
    },
    {
        "id": 3,
        "content": "Em cada tela da apresentação há quatro adjetivos. Marque o que MAIS tem a ver com você na coluna esquerda e o que MENOS tem a ver com você na coluna direita."
    },
    {
        "id": 4,
        "content": "Escolha primeiro o MAIS e depois o MENOS. Despreze os demais."
    },
    {
        "id": 5,
        "content": "Seja sincero... Não responda pensando em como você GOSTARIA de ser... escolha como você realmente É NO SEU DIA-A-DIA."
    },
    {
        "id": 6,
        "content": "As telas vão mudar a cada 15 segundos totalizando SEIS minutos."
    },
    {
        "id": 7,
        "content": "Seja o mais natural e espontâneo possível e não interrompa o preenchimento... isso poderá interferir negativamente na sua avaliação."
    },
    {
        "id": 8,
        "content": "Você pode fazer a contagem da sua marcação com palitinhos..."
    },
    {
        "id": 9,
        "content": "PREPARADOS!"
    }
]

# Cartões das questões DISC
question_cards = [
    {
        "id": 10,
        "options": [
            {"letter": "A", "text": "DETERMINADO"},
            {"letter": "B", "text": "CONFIANTE"},
            {"letter": "C", "text": "CONSISTENTE"},
            {"letter": "D", "text": "PRECISO"}
        ]
    },
    {
        "id": 11,
        "options": [
            {"letter": "A", "text": "APRESSADO"},
            {"letter": "B", "text": "PERSUASIVO"},
            {"letter": "C", "text": "METÓDICO"},
            {"letter": "D", "text": "CUIDADOSO"}
        ]
    },
    {
        "id": 12,
        "options": [
            {"letter": "A", "text": "COMPETITIVO"},
            {"letter": "B", "text": "POLÍTICO"},
            {"letter": "C", "text": "COOPERATIVO"},
            {"letter": "D", "text": "DIPLOMATA"}
        ]
    },
    {
        "id": 13,
        "options": [
            {"letter": "A", "text": "OBJETIVO"},
            {"letter": "B", "text": "EXAGERADO"},
            {"letter": "C", "text": "ESTÁVEL"},
            {"letter": "D", "text": "EXATO"}
        ]
    },
    {
        "id": 14,
        "options": [
            {"letter": "A", "text": "ASSERTIVO"},
            {"letter": "B", "text": "OTIMISTA"},
            {"letter": "C", "text": "PACIENTE"},
            {"letter": "D", "text": "PRUDENTE"}
        ]
    },
    {
        "id": 15,
        "options": [
            {"letter": "A", "text": "FAZEDOR"},
            {"letter": "B", "text": "INSPIRADOR"},
            {"letter": "C", "text": "PERSISTENTE"},
            {"letter": "D", "text": "PERFECCIONISTA"}
        ]
    },
    {
        "id": 16,
        "options": [
            {"letter": "A", "text": "AGRESSIVO"},
            {"letter": "B", "text": "EXPANSIVO"},
            {"letter": "C", "text": "POSSESSIVO"},
            {"letter": "D", "text": "JULGADOR"}
        ]
    },
    {
        "id": 17,
        "options": [
            {"letter": "A", "text": "DECIDIDO"},
            {"letter": "B", "text": "FLEXÍVEL"},
            {"letter": "C", "text": "PREVISÍVEL"},
            {"letter": "D", "text": "SISTEMÁTICO"}
        ]
    },
    {
        "id": 18,
        "options": [
            {"letter": "A", "text": "INOVADOR"},
            {"letter": "B", "text": "COMUNICATIVO"},
            {"letter": "C", "text": "AGRADÁVEL"},
            {"letter": "D", "text": "ELEGANTE"}
        ]
    },
    {
        "id": 19,
        "options": [
            {"letter": "A", "text": "AUTORITÁRIO"},
            {"letter": "B", "text": "EXTRAVAGANTE"},
            {"letter": "C", "text": "MODESTO"},
            {"letter": "D", "text": "DESCONFIADO"}
        ]
    },
    {
        "id": 20,
        "options": [
            {"letter": "A", "text": "ENÉRGICO"},
            {"letter": "B", "text": "ENTUSIASMADO"},
            {"letter": "C", "text": "CALMO"},
            {"letter": "D", "text": "DISCIPLINADO"}
        ]
    },
    {
        "id": 21,
        "options": [
            {"letter": "A", "text": "FIRME"},
            {"letter": "B", "text": "EXPRESSIVO"},
            {"letter": "C", "text": "AMÁVEL"},
            {"letter": "D", "text": "FORMAL"}
        ]
    },
    {
        "id": 22,
        "options": [
            {"letter": "A", "text": "VISIONÁRIO"},
            {"letter": "B", "text": "CRIATIVO"},
            {"letter": "C", "text": "PONDERADO"},
            {"letter": "D", "text": "DETALHISTA"}
        ]
    },
    {
        "id": 23,
        "options": [
            {"letter": "A", "text": "EGOCÊNTRICO"},
            {"letter": "B", "text": "TAGARELA"},
            {"letter": "C", "text": "ACOMODADO"},
            {"letter": "D", "text": "RETRAÍDO"}
        ]
    },
    {
        "id": 24,
        "options": [
            {"letter": "A", "text": "INSPIRA CONFIANÇA"},
            {"letter": "B", "text": "CONVINCENTE"},
            {"letter": "C", "text": "COMPREENSIVO"},
            {"letter": "D", "text": "PONTUAL"}
        ]
    },
    {
        "id": 25,
        "options": [
            {"letter": "A", "text": "INTIMIDANTE"},
            {"letter": "B", "text": "SEM CERIMÔNIA"},
            {"letter": "C", "text": "RESERVADO"},
            {"letter": "D", "text": "INTRANSIGENTE"}
        ]
    },
    {
        "id": 26,
        "options": [
            {"letter": "A", "text": "VIGOROSO"},
            {"letter": "B", "text": "CALOROSO"},
            {"letter": "C", "text": "GENTIL"},
            {"letter": "D", "text": "PREOCUPADO"}
        ]
    },
    {
        "id": 27,
        "options": [
            {"letter": "A", "text": "OUSADO"},
            {"letter": "B", "text": "SEDUTOR"},
            {"letter": "C", "text": "HARMONIZADOR"},
            {"letter": "D", "text": "CAUTELOSO"}
        ]
    },
    {
        "id": 28,
        "options": [
            {"letter": "A", "text": "FORÇA DE VONTADE"},
            {"letter": "B", "text": "ESPONTÂNEO"},
            {"letter": "C", "text": "SATISFEITO"},
            {"letter": "D", "text": "CONSERVADOR"}
        ]
    },
    {
        "id": 29,
        "options": [
            {"letter": "A", "text": "EXIGENTE"},
            {"letter": "B", "text": "SOCIÁVEL"},
            {"letter": "C", "text": "LEAL"},
            {"letter": "D", "text": "RIGOROSO"}
        ]
    },
    {
        "id": 30,
        "options": [
            {"letter": "A", "text": "PIONEIRO"},
            {"letter": "B", "text": "DIVERTIDO"},
            {"letter": "C", "text": "TRANQUILO"},
            {"letter": "D", "text": "CONVENCIONAL"}
        ]
    },
    {
        "id": 31,
        "options": [
            {"letter": "A", "text": "AMBICIOSO"},
            {"letter": "B", "text": "RADIANTE"},
            {"letter": "C", "text": "REGULADO"},
            {"letter": "D", "text": "CALCULISTA"}
        ]
    },
    {
        "id": 32,
        "options": [
            {"letter": "A", "text": "INQUISITIVO"},
            {"letter": "B", "text": "OFERECIDO"},
            {"letter": "C", "text": "RÍGIDO CONSIGO"},
            {"letter": "D", "text": "CÉTICO"}
        ]
    },
    {
        "id": 33,
        "options": [
            {"letter": "A", "text": "AUDACIOSO"},
            {"letter": "B", "text": "EXTROVERTIDO"},
            {"letter": "C", "text": "CASUAL"},
            {"letter": "D", "text": "METICULOSO"}
        ]
    },
    {
        "id": 34,
        "options": [
            {"letter": "A", "text": "DIRETO"},
            {"letter": "B", "text": "PROLIXO"},
            {"letter": "C", "text": "MODERADO"},
            {"letter": "D", "text": "PROCESSUAL"}
        ]
    }
]

# Mapeamento das letras para os fatores DISC
disc_mapping = {
    'A': 'D',  # Dominância
    'B': 'I',  # Influência
    'C': 'S',  # Estabilidade
    'D': 'C'   # Conformidade
}

# Descrições dos perfis DISC
disc_descriptions = {
    'D': {
        'title': 'Dominância',
        'motivation': 'Desafio, Liberdade e Criatividade',
        'characteristics': [
            'Determinado', 'Competitivo', 'Objetivo', 'Assertivo', 'Fazedor',
            'Decidido', 'Inovador', 'Autoritário', 'Enérgico', 'Firme',
            'Visionário', 'Intimidante', 'Vigoroso', 'Ousado', 'Direto'
        ],
        'strengths': [
            'Foco em resultados', 
            'Toma iniciativa', 
            'Aceita desafios',
            'Decisivo',
            'Direto'
        ],
        'weaknesses': [
            'Pode parecer agressivo',
            'Impaciente', 
            'Pode dominar os outros',
            'Dificuldade de ouvir',
            'Pouca empatia'
        ],
        'how_to_work_with': [
            'Seja breve e direto ao ponto',
            'Respeite sua autonomia',
            'Seja claro com as regras e expectativas',
            'Demonstre competência'
        ]
    },
    'I': {
        'title': 'Influência',
        'motivation': 'Relacionamento',
        'characteristics': [
            'Confiante', 'Persuasivo', 'Político', 'Exagerado', 'Otimista',
            'Inspirador', 'Expansivo', 'Flexível', 'Comunicativo', 'Extravagante',
            'Entusiasmado', 'Expressivo', 'Criativo', 'Tagarela', 'Convincente'
        ],
        'strengths': [
            'Comunicação', 
            'Entusiasmo', 
            'Criatividade',
            'Habilidades sociais',
            'Motivação'
        ],
        'weaknesses': [
            'Pode ser desorganizado',
            'Falante demais', 
            'Nem sempre cumpre compromissos',
            'Pode exagerar',
            'Evita detalhes'
        ],
        'how_to_work_with': [
            'Seja informal e sociável',
            'Permita tempo para socialização',
            'Reconheça suas contribuições publicamente',
            'Forneça detalhes por escrito'
        ]
    },
    'S': {
        'title': 'Estabilidade',
        'motivation': 'Segurança e Lealdade',
        'characteristics': [
            'Consistente', 'Metódico', 'Cooperativo', 'Estável', 'Paciente',
            'Persistente', 'Possessivo', 'Previsível', 'Agradável', 'Modesto',
            'Calmo', 'Amável', 'Ponderado', 'Acomodado', 'Compreensivo'
        ],
        'strengths': [
            'Lealdade', 
            'Paciência', 
            'Capacidade de ouvir',
            'Trabalho em equipe',
            'Confiabilidade'
        ],
        'weaknesses': [
            'Resistência a mudanças',
            'Pode ser lento para agir', 
            'Evita conflitos',
            'Dificuldade de priorizar',
            'Pode ser muito complacente'
        ],
        'how_to_work_with': [
            'Seja calmo e sistemático',
            'Comunique mudanças com antecedência',
            'Demonstre apreciação sincera',
            'Dê tempo para se adaptar'
        ]
    },
    'C': {
        'title': 'Conformidade',
        'motivation': 'Qualidade e Colaboração',
        'characteristics': [
            'Preciso', 'Cuidadoso', 'Diplomata', 'Exato', 'Prudente',
            'Perfeccionista', 'Julgador', 'Sistemático', 'Elegante', 'Desconfiado',
            'Disciplinado', 'Formal', 'Detalhista', 'Retraído', 'Pontual'
        ],
        'strengths': [
            'Atenção aos detalhes', 
            'Precisão', 
            'Organização',
            'Análise crítica',
            'Qualidade'
        ],
        'weaknesses': [
            'Perfeccionismo excessivo',
            'Análise excessiva', 
            'Pode ser muito crítico',
            'Medo de errar',
            'Resistência a novas abordagens'
        ],
        'how_to_work_with': [
            'Forneça explicações claras e detalhadas',
            'Dê tempo para analisar',
            'Seja preciso e respeite os procedimentos',
            'Valorize altos padrões de qualidade'
        ]
    }
} 
