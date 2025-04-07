# backend/interpretations.py

import re # Importado para parsing

# Mapeamento das seções dos Markdowns para chaves do dicionário
# Usaremos chaves consistentes para facilitar o acesso no template.
# 'descricao' -> Descrição
# 'motivacao' -> Motivação
# 'caracteristicas' -> Características Comuns
# 'pontos_fortes' -> Pontos Fortes
# 'areas_desenvolvimento' -> Áreas de Desenvolvimento
# 'relacionamento_dicas' -> Como se Relacionar (Dicas)
# 'como_voce_e' -> Como você é
# 'como_pode_melhorar' -> Como pode melhorar

interpretations_data = {
    # --- Perfil D ---
    'D': {
        'moderate': { # Score 0-10 (Ajuste faixa se necessário)
            'descricao': "Você apresenta uma liderança assertiva e orientada a resultados, demonstrando firmeza sem perder a capacidade de ponderação.",
            'motivacao': "Impulsionado por desafios e pela conquista de metas, você busca resultados de forma decidida, mas equilibrada.",
            'caracteristicas': "Determinado, focado e assertivo, com habilidade para tomar decisões sem impor excessivamente.",
            'pontos_fortes': "Liderança natural, tomada de decisão ponderada, iniciativa e clareza de objetivos.",
            'areas_desenvolvimento': "Pode aprimorar a empatia e a paciência, aprendendo a delegar responsabilidades e a ouvir os demais.",
            'relacionamento_dicas': "Seja objetivo e direto, mas abra espaço para o feedback e a colaboração.",
            'como_voce_e': "Você é determinado, focado em resultados e toma decisões com confiança.", # Exemplo de texto adaptado
            'como_pode_melhorar': "Trabalhe a escuta ativa e considere o impacto das suas ações nas pessoas ao redor." # Exemplo
        },
        'significant': { # Score 11-18 (Ajuste faixa se necessário)
            'descricao': "Sua forte orientação para resultados e assertividade são marcantes. Você é direto, competitivo e busca controle sobre as situações.",
            'motivacao': "Fortemente motivado por desafios, autonomia e pela obtenção rápida de resultados tangíveis.",
            'caracteristicas': "Direto, decisivo, competitivo, assertivo, independente, exigente e rápido.",
            'pontos_fortes': "Excelente em liderança sob pressão, resolução de problemas complexos, tomada de decisão rápida e foco intenso em metas.",
            'areas_desenvolvimento': "Precisa desenvolver a paciência com processos e pessoas, a sensibilidade interpessoal e a capacidade de delegar efetivamente.",
            'relacionamento_dicas': "Comunique-se de forma clara e objetiva, respeite a necessidade de autonomia, mas também demonstre interesse pelas opiniões alheias.",
            'como_voce_e': "Você é altamente focado em resultados, direto e gosta de estar no controle.",
            'como_pode_melhorar': "Desenvolva a empatia e a colaboração para equilibrar sua forte assertividade."
        },
        'high': { # Score 19+ (Ajuste faixa se necessário)
            'descricao': "Você possui uma Dominância muito elevada, sendo extremamente assertivo, direto, competitivo e focado em superar desafios e controlar o ambiente.",
            'motivacao': "Movido por poder, autoridade, controle e a superação de grandes desafios e da concorrência.",
            'caracteristicas': "Extremamente direto, enérgico, exigente, rápido, impaciente, controlador e visionário.",
            'pontos_fortes': "Capacidade excepcional de liderança em crises, visão estratégica, assume riscos calculados, alta energia e persistência.",
            'areas_desenvolvimento': "Risco de ser percebido como intimidador ou insensível. Necessita fortemente desenvolver a escuta, a empatia, a paciência e a colaboração genuína.",
            'relacionamento_dicas': "Mantenha a comunicação concisa e focada em resultados, mas invista tempo em entender as perspectivas dos outros e em construir confiança através da colaboração.",
            'como_voce_e': "Sua presença é marcante pela força, determinação e foco absoluto em vencer.",
            'como_pode_melhorar': "O maior desafio é equilibrar sua imensa força com a sensibilidade necessária para liderar e colaborar efetivamente a longo prazo."
        },
    },
    # --- Perfil I ---
    'I': {
        'moderate': {
            'descricao': "Você é comunicativo e entusiasta, valorizando as relações interpessoais e influenciando os outros de maneira positiva e equilibrada.",
            'motivacao': "Motivado pelo reconhecimento social, trabalho em equipe e um ambiente positivo e estimulante.",
            'caracteristicas': "Sociável, otimista, persuasivo, expressivo e colaborativo, sem excessos.",
            'pontos_fortes': "Excelente comunicação interpessoal, capacidade de motivar e engajar, otimismo contagiante.",
            'areas_desenvolvimento': "Pode precisar aprimorar a organização, o foco em detalhes e a gestão do tempo.",
            'relacionamento_dicas': "Interaja de forma aberta e amigável, demonstre entusiasmo e valorize suas contribuições sociais.",
            'como_voce_e': "Você é sociável, otimista e gosta de interagir com as pessoas.",
            'como_pode_melhorar': "Desenvolva um pouco mais de atenção aos detalhes e planejamento."
        },
        'significant': {
            'descricao': "Altamente comunicativo, sociável e persuasivo, você tem grande facilidade em criar conexões e influenciar pessoas com seu entusiasmo.",
            'motivacao': "Fortemente motivado por reconhecimento público, popularidade, liberdade de expressão e ambientes sociais dinâmicos.",
            'caracteristicas': "Muito falante, otimista, sociável, persuasivo, emocional, espontâneo e inspirador.",
            'pontos_fortes': "Grande habilidade de networking, persuasão e influência, criação de um ambiente positivo, capacidade de inspirar.",
            'areas_desenvolvimento': "Pode ter dificuldade com organização, seguir rotinas, análise crítica de detalhes e tomada de decisões baseadas puramente em lógica.",
            'relacionamento_dicas': "Permita que se expressem, ouça suas ideias com entusiasmo, ofereça reconhecimento e evite rotinas muito rígidas.",
            'como_voce_e': "Você adora interagir, é muito persuasivo e otimista.",
            'como_pode_melhorar': "Trabalhe a organização, a gestão do tempo e a atenção aos detalhes."
        },
        'high': {
            'descricao': "Extremamente extrovertido, entusiasmado e sociável, você busca constantemente interação e tem uma necessidade elevada de reconhecimento e aceitação social.",
            'motivacao': "Movido intensamente pela aclamação social, popularidade, estar no centro das atenções e ambientes altamente estimulantes.",
            'caracteristicas': "Exuberante, muito falante, emocionalmente expressivo, busca aprovação, impulsivo, otimista ao extremo.",
            'pontos_fortes': "Capacidade excepcional de conectar e energizar pessoas, carisma magnético, otimismo inabalável, grande poder de influência.",
            'areas_desenvolvimento': "Forte tendência à desorganização, dificuldade em lidar com tarefas detalhadas ou rotineiras, pode parecer superficial ou falar excessivamente, dificuldade em dizer não.",
            'relacionamento_dicas': "Ofereça muito reconhecimento e feedback positivo, crie um ambiente socialmente estimulante, seja paciente com a falta de estrutura e ajude a manter o foco.",
            'como_voce_e': "Sua energia social é contagiante e você busca ativamente a conexão com os outros.",
            'como_pode_melhorar': "É crucial desenvolver disciplina, foco em tarefas e a capacidade de análise objetiva para complementar seu carisma."
        },
    },
    # --- Perfil S ---
    'S': {
        'moderate': {
            'descricao': "Você valoriza a estabilidade e a harmonia, sendo um colaborador paciente, leal e previsível.",
            'motivacao': "Motivado por segurança, ambientes previsíveis e relações de confiança e apoio mútuo.",
            'caracteristicas': "Calmo, paciente, leal, bom ouvinte, cooperativo e metódico.",
            'pontos_fortes': "Excelente em trabalho em equipe, confiabilidade, consistência, apoio aos colegas.",
            'areas_desenvolvimento': "Pode ter dificuldade em lidar com mudanças rápidas, tomar iniciativas ou expressar discordância.",
            'relacionamento_dicas': "Ofereça um ambiente seguro e estável, comunique mudanças com antecedência e valorize sua lealdade.",
            'como_voce_e': "Você é calmo, paciente e valoriza a segurança e a cooperação.",
            'como_pode_melhorar': "Desenvolva um pouco mais de assertividade e flexibilidade diante de mudanças."
        },
        'significant': {
            'descricao': "Muito paciente, leal e metódico, você busca ativamente por segurança, estabilidade e harmonia nas relações e no ambiente de trabalho.",
            'motivacao': "Fortemente motivado por segurança, estabilidade, relacionamentos duradouros e processos bem definidos.",
            'caracteristicas': "Extremamente calmo, paciente, leal, previsível, resistente a mudanças, ótimo ouvinte, metódico.",
            'pontos_fortes': "Altamente confiável e consistente, excelente em seguir procedimentos, promove harmonia na equipe, grande capacidade de escuta e apoio.",
            'areas_desenvolvimento': "Pode ter grande resistência a mudanças, dificuldade em tomar decisões rápidas, expressar necessidades próprias ou lidar com conflitos.",
            'relacionamento_dicas': "Crie um ambiente seguro e previsível, comunique mudanças de forma gradual e clara, seja paciente e demonstre apreço pela sua lealdade.",
            'como_voce_e': "Você é a personificação da calma, lealdade e estabilidade.",
            'como_pode_melhorar': "Trabalhe a adaptabilidade a mudanças e a expressão assertiva de suas opiniões."
        },
        'high': {
            'descricao': "Você tem uma necessidade extrema de estabilidade, segurança e previsibilidade. É excepcionalmente paciente, leal e avesso a mudanças e conflitos.",
            'motivacao': "Movido intensamente pela segurança absoluta, rotina, relacionamentos profundos e estáveis, e um ambiente sem conflitos.",
            'caracteristicas': "Extremamente calmo, metódico, previsível, muito resistente a mudanças, evita conflitos a todo custo, excepcionalmente leal.",
            'pontos_fortes': "Lealdade e confiabilidade inabaláveis, habilidade excepcional em tarefas que exigem consistência e paciência, promove um ambiente de apoio.",
            'areas_desenvolvimento': "Extrema dificuldade em lidar com qualquer tipo de mudança ou incerteza, pode ser excessivamente passivo, dificuldade em impor limites ou expressar descontentamento.",
            'relacionamento_dicas': "Ofereça máxima segurança e previsibilidade, introduza mudanças de forma muito lenta e com muito apoio, evite confrontos diretos e valorize imensamente sua dedicação.",
            'como_voce_e': "Sua busca por segurança e harmonia define suas ações e relacionamentos.",
            'como_pode_melhorar': "O maior desafio é desenvolver resiliência a mudanças e a capacidade de se posicionar, mesmo que isso gere algum desconforto inicial."
        },
    },
     # --- Perfil C ---
    'C': {
        'moderate': {
            'descricao': "Você é cuidadoso, preciso e organizado, valorizando a qualidade e a exatidão em suas tarefas de forma equilibrada.",
            'motivacao': "Motivado pela qualidade, precisão, lógica e por seguir regras e procedimentos estabelecidos.",
            'caracteristicas': "Analítico, organizado, preciso, diplomático e atento aos detalhes.",
            'pontos_fortes': "Alta qualidade no trabalho, atenção aos detalhes, planejamento cuidadoso, pensamento lógico.",
            'areas_desenvolvimento': "Pode ser percebido como perfeccionista ou excessivamente crítico. Pode ter dificuldade em tomar decisões rápidas ou lidar com ambiguidades.",
            'relacionamento_dicas': "Forneça informações detalhadas e precisas, respeite sua necessidade de análise e evite pressioná-lo por decisões rápidas.",
            'como_voce_e': "Você é analítico, organizado e busca a precisão.",
            'como_pode_melhorar': "Desenvolva maior flexibilidade e agilidade na tomada de decisões."
        },
        'significant': {
            'descricao': "Altamente analítico, preciso e organizado, você busca a perfeição e a exatidão em tudo que faz, seguindo regras e padrões rigorosamente.",
            'motivacao': "Fortemente motivado por qualidade, precisão, lógica, fatos, regras e procedimentos corretos.",
            'caracteristicas': "Muito analítico, detalhista, organizado, sistemático, cauteloso, questionador e preciso.",
            'pontos_fortes': "Excepcional atenção aos detalhes, alta qualidade e precisão no trabalho, planejamento minucioso, pensamento crítico e analítico.",
            'areas_desenvolvimento': "Pode ser excessivamente crítico (consigo e com os outros), resistente a correr riscos, lento na tomada de decisões (paralisia por análise), dificuldade em lidar com ambiguidades.",
            'relacionamento_dicas': "Comunique-se com fatos e dados, forneça informações detalhadas, dê tempo para análise, evite pressão por decisões rápidas e reconheça a qualidade do seu trabalho.",
            'como_voce_e': "Você busca a lógica, a precisão e a qualidade em tudo.",
            'como_pode_melhorar': "Trabalhe a flexibilidade, a tomada de decisão com informações imperfeitas e a comunicação interpessoal menos crítica."
        },
        'high': {
            'descricao': "Você possui uma Conformidade extremamente elevada, sendo excepcionalmente analítico, preciso, organizado e focado em seguir regras e padrões com perfeição.",
            'motivacao': "Movido intensamente pela precisão absoluta, qualidade impecável, lógica, dados comprovados e conformidade com regras e padrões.",
            'caracteristicas': "Extremamente analítico, perfeccionista, cético, questionador, organizado, sistemático, cauteloso ao extremo.",
            'pontos_fortes': "Nível extraordinário de precisão e qualidade, capacidade analítica profunda, planejamento e organização impecáveis, pensamento crítico aguçado.",
            'areas_desenvolvimento': "Risco elevado de perfeccionismo paralisante, excesso de crítica, resistência a qualquer desvio de regras, lentidão extrema na decisão, dificuldade com o 'cinza' (só vê preto e branco).",
            'relacionamento_dicas': "Baseie toda a comunicação em fatos, dados e lógica comprovada, seja extremamente claro e detalhado, evite ambiguidades, dê tempo suficiente (ou mais) para análise e valorize a exatidão.",
            'como_voce_e': "Sua mente analítica busca incansavelmente a perfeição e a ordem lógica.",
            'como_pode_melhorar': "O maior desafio é aceitar o 'bom o suficiente', desenvolver a agilidade, a confiança na intuição (mesmo que mínima) e a capacidade de lidar com a imperfeição do mundo real."
        },
    },

    # --- Textos Genéricos (Fallback) ---
    # Usado quando não há perfil secundário claro ou para descrições gerais
    'secondary_generic_moderate': {
        'descricao': "A influência secundária em seu perfil é moderada, adicionando nuances e habilidades complementares ao seu perfil principal sem dominá-lo. Isso pode trazer flexibilidade ou pontos de vista adicionais.",
        'motivacao': "As motivações secundárias são menos intensas, mas podem influenciar suas decisões em contextos específicos, buscando equilibrar as necessidades do perfil primário.",
        'caracteristicas': "Traz traços adicionais que podem se manifestar em situações particulares, como uma maior atenção a detalhes (se for C) ou mais foco em pessoas (se for I), dependendo do perfil secundário.",
        'pontos_fortes': "A principal força dessa influência moderada é a capacidade de adaptação e a adição de perspectivas que enriquecem seu perfil dominante.",
        'areas_desenvolvimento': "O desafio é reconhecer e utilizar conscientemente essas características secundárias para complementar seu perfil principal, evitando que se tornem fontes de conflito interno.",
        'relacionamento_dicas': "Entender essa influência secundária pode ajudar a prever suas reações em diferentes situações e a comunicar melhor suas necessidades e estilo.",
        'como_voce_e': "Você demonstra flexibilidade ao incorporar traços de um segundo perfil de forma moderada.",
        'como_pode_melhorar': "Aumente a autoconsciência sobre como esses traços secundários influenciam seu comportamento e use-os estrategicamente."
    }
    # Poderiam existir 'secondary_generic_significant', 'secondary_generic_high' se necessário
}


# ---------------------------------------------------------------------------
#  Novas Interpretações Específicas para Perfil Secundário MODERADO (0-10)
# ---------------------------------------------------------------------------
# Parseado do arquivo "perfis secuncarios caso a caso.txt"

secondary_specific_interpretations = {
    ('I', 'D'): {
        'descricao': 'Seu perfil predominante é o Influência (I), marcado por uma natureza comunicativa e entusiasta. O secundário Dominância (D) adiciona um toque de assertividade e foco em resultados, de forma moderada.',
        'motivacao': 'Enquanto o I é motivado pelo reconhecimento e pelas relações interpessoais, o D contribui com o desejo de agir, tomar decisões e alcançar metas.',
        'caracteristicas': 'A influência D se manifesta como uma discreta assertividade, conferindo-lhe a capacidade de direcionar conversas e iniciativas sem perder a espontaneidade do I.',
        'pontos_fortes': 'Você combina carisma e energia com uma determinação moderada, o que favorece a liderança e a iniciativa nas interações.',
        'areas_desenvolvimento': 'Aprimore sua assertividade de forma equilibrada, para que a necessidade de ação não comprometa a naturalidade e o calor humano do I.',
        'relacionamento_dicas': 'Utilize sua comunicação calorosa aliada a uma postura objetiva. Estabeleça metas claras sem se tornar autoritário, valorizando o feedback da equipe.'
    },
    ('S', 'D'): {
        'descricao': 'Com o perfil primário Estabilidade (S), você valoriza a segurança e a colaboração. O secundário Dominância (D) introduz uma leve influência de assertividade e foco em resultados, mantendo a moderação.',
        'motivacao': 'O S busca segurança e apoio, enquanto a influência D impulsiona a agir e tomar decisões pontuais para garantir a estabilidade desejada.',
        'caracteristicas': 'A influência D se manifesta como uma capacidade sutil de tomar a frente quando necessário, sem comprometer a natureza colaborativa e paciente do S.',
        'pontos_fortes': 'Você equilibra a paciência e a cooperação com uma determinação moderada, o que permite defender suas posições de forma calma, mas firme.',
        'areas_desenvolvimento': 'Desenvolva a confiança para expressar suas necessidades e limites, garantindo que sua assertividade moderada seja utilizada de forma eficaz.',
        'relacionamento_dicas': 'Combine sua abordagem calma e estável com uma comunicação clara sobre objetivos e expectativas. Seja firme quando necessário, mas sempre valorizando a harmonia.'
    },
    ('C', 'D'): {
        'descricao': 'Seu perfil primário é Conformidade (C), focado em precisão e análise. O secundário Dominância (D) adiciona uma camada moderada de assertividade e direcionamento para resultados.',
        'motivacao': 'Enquanto o C é motivado pela qualidade e correção, a influência D traz um impulso para aplicar essa precisão na busca por objetivos concretos.',
        'caracteristicas': 'A influência D se manifesta na capacidade de defender suas análises e padrões com firmeza, direcionando tarefas de forma organizada e lógica.',
        'pontos_fortes': 'Você une análise detalhada com uma determinação moderada para garantir que os padrões de qualidade sejam seguidos e os objetivos alcançados.',
        'areas_desenvolvimento': 'Trabalhe a flexibilidade para que a busca pela perfeição (C) e a assertividade (D) não resultem em rigidez excessiva. Aprenda a ponderar entre o ideal e o factível.',
        'relacionamento_dicas': 'Use sua capacidade analítica para apresentar argumentos sólidos (C) e sua assertividade moderada (D) para defender suas conclusões de forma clara e objetiva.'
    },
    ('D', 'I'): {
        'descricao': 'Seu perfil primário é Dominância (D), orientado a resultados e assertivo. O secundário Influência (I) acrescenta uma dose moderada de sociabilidade e entusiasmo.',
        'motivacao': 'Enquanto o D é motivado por desafios e controle, a influência I adiciona o desejo de interagir, persuadir e criar um ambiente mais positivo.',
        'caracteristicas': 'A influência I suaviza a assertividade do D, manifestando-se como uma capacidade de comunicar suas ideias de forma mais envolvente e carismática.',
        'pontos_fortes': 'Você combina determinação e foco em resultados (D) com habilidades de comunicação e persuasão (I), tornando sua liderança mais inspiradora.',
        'areas_desenvolvimento': 'Equilibre a necessidade de controle (D) com a abertura para colaboração (I). Evite que o entusiasmo o desvie dos objetivos principais.',
        'relacionamento_dicas': 'Use sua assertividade (D) para definir direções e seu carisma (I) para engajar e motivar as pessoas. Ouça ativamente para fortalecer as conexões.'
    },
    ('S', 'I'): {
        'descricao': 'Com um perfil primário Estabilidade (S), você busca harmonia e segurança. O secundário Influência (I) adiciona uma camada moderada de extroversão e comunicação.',
        'motivacao': 'Enquanto o S valoriza a segurança e a cooperação, a influência I traz o desejo de interagir socialmente e construir relacionamentos positivos.',
        'caracteristicas': 'A influência I se manifesta como uma maior abertura para o diálogo e interação social, complementando a natureza calma e reservada do S.',
        'pontos_fortes': 'Você combina a lealdade e a paciência (S) com uma comunicação mais aberta e amigável (I), facilitando a criação de um ambiente de equipe coeso e positivo.',
        'areas_desenvolvimento': 'Trabalhe a assertividade para que a busca por harmonia (S) e aceitação social (I) não o impeça de expressar suas necessidades ou discordâncias.',
        'relacionamento_dicas': 'Use sua natureza acolhedora (S) e sua comunicação amigável (I) para construir confiança. Seja claro sobre suas expectativas de forma gentil.'
    },
    ('C', 'I'): {
        'descricao': 'Seu perfil primário é Conformidade (C), focado em análise e precisão. O secundário Influência (I) introduz uma influência moderada de sociabilidade e expressividade.',
        'motivacao': 'Enquanto o C busca precisão e lógica, a influência I adiciona um toque de desejo por interação social e reconhecimento.',
        'caracteristicas': 'A influência I permite que você comunique suas análises e ideias de forma mais acessível e envolvente, superando a possível reserva do C.',
        'pontos_fortes': 'Você combina rigor analítico (C) com habilidades de comunicação interpessoal (I), sendo capaz de explicar conceitos complexos de forma clara e cativante.',
        'areas_desenvolvimento': 'Equilibre a necessidade de dados e fatos (C) com a intuição e a dinâmica social (I). Cuidado para não sacrificar a precisão pelo entusiasmo.',
        'relacionamento_dicas': 'Use sua clareza analítica (C) para estruturar suas ideias e seu carisma moderado (I) para apresentá-las de forma persuasiva e colaborativa.'
    },
    ('D', 'S'): {
        'descricao': 'Com um perfil primário Dominância (D), você é assertivo e focado em resultados. O secundário Estabilidade (S) adiciona uma camada moderada de paciência e consideração pelas pessoas.',
        'motivacao': 'Enquanto o D busca desafios e controle, a influência S traz uma valorização da segurança, da cooperação e de um ritmo mais ponderado.',
        'caracteristicas': 'A influência S modera a impaciência do D, manifestando-se como uma maior capacidade de ouvir e considerar o impacto das decisões na equipe.',
        'pontos_fortes': 'Você combina determinação (D) com uma abordagem mais estável e colaborativa (S), resultando em uma liderança firme, porém mais atenta às pessoas.',
        'areas_desenvolvimento': 'Trabalhe o equilíbrio entre a urgência por resultados (D) e a necessidade de processos estáveis (S). Aprenda a delegar e confiar na equipe.',
        'relacionamento_dicas': 'Seja direto sobre os objetivos (D), mas demonstre paciência e apoio (S) ao lidar com a equipe. Crie um ambiente onde a eficiência e a estabilidade coexistam.'
    },
    ('I', 'S'): {
        'descricao': 'Seu perfil primário é Influência (I), caracterizado pelo entusiasmo e sociabilidade. O secundário Estabilidade (S) adiciona uma influência moderada de calma, paciência e foco em relacionamentos de longo prazo.',
        'motivacao': 'Enquanto o I busca reconhecimento e interação, a influência S valoriza a segurança, a harmonia e a lealdade nas conexões.',
        'caracteristicas': 'A influência S equilibra o entusiasmo do I, trazendo uma abordagem mais calma, atenta e focada em construir confiança e apoio mútuo.',
        'pontos_fortes': 'Você combina carisma e otimismo (I) com lealdade e empatia (S), sendo excelente em construir relacionamentos fortes e criar um ambiente de equipe positivo e estável.',
        'areas_desenvolvimento': 'Evite que a busca por aceitação (I) e harmonia (S) o impeça de tomar decisões difíceis ou de dar feedback construtivo quando necessário.',
        'relacionamento_dicas': 'Use seu entusiasmo (I) para iniciar conexões e sua natureza apoiadora (S) para mantê-las. Demonstre interesse genuíno e ofereça suporte constante.'
    },
    ('C', 'S'): {
        'descricao': 'Com um perfil primário Conformidade (C), você é analítico e preciso. O secundário Estabilidade (S) adiciona uma influência moderada de paciência, cooperação e foco em segurança.',
        'motivacao': 'Enquanto o C busca qualidade e correção, a influência S valoriza a segurança, a previsibilidade e um ambiente de trabalho harmonioso.',
        'caracteristicas': 'A influência S complementa a natureza analítica do C com uma abordagem mais calma, metódica e colaborativa na execução de tarefas.',
        'pontos_fortes': 'Você combina precisão e atenção aos detalhes (C) com paciência e confiabilidade (S), sendo excelente em tarefas que exigem qualidade e consistência.',
        'areas_desenvolvimento': 'Trabalhe a flexibilidade e a agilidade, pois a combinação C+S pode levar a uma resistência a mudanças ou a uma lentidão excessiva na tomada de decisões.',
        'relacionamento_dicas': 'Comunique suas análises (C) de forma calma e estruturada (S). Valorize a colaboração e ofereça suporte baseado em dados e procedimentos claros.'
    },
    ('D', 'C'): {
        'descricao': 'Seu perfil primário é Dominância (D), focado em resultados e assertividade. O secundário Conformidade (C) adiciona uma camada moderada de análise, precisão e atenção aos detalhes.',
        'motivacao': 'Enquanto o D busca desafios e controle, a influência C adiciona uma preocupação com a qualidade, a lógica e a correção dos processos.',
        'caracteristicas': 'A influência C modera a impulsividade do D, trazendo uma abordagem mais planejada, analítica e focada em dados para a tomada de decisão.',
        'pontos_fortes': 'Você combina determinação e foco em resultados (D) com planejamento e análise crítica (C), resultando em decisões assertivas, porém bem fundamentadas.',
        'areas_desenvolvimento': 'Equilibre a necessidade de ação rápida (D) com a análise detalhada (C). Evite a "paralisia por análise" ou a crítica excessiva que pode desmotivar os outros.',
        'relacionamento_dicas': 'Seja direto sobre os objetivos (D), mas apresente dados e lógica (C) para embasar suas decisões. Valorize a precisão e a qualidade no trabalho dos outros.'
    },
    ('I', 'C'): {
        'descricao': 'Com um perfil primário Influência (I), você é comunicativo e entusiasta. O secundário Conformidade (C) adiciona uma influência moderada de organização, análise e atenção aos detalhes.',
        'motivacao': 'Enquanto o I busca interação e reconhecimento, a influência C traz uma valorização da qualidade, da precisão e de um certo grau de estrutura.',
        'caracteristicas': 'A influência C ajuda a organizar o entusiasmo do I, manifestando-se como uma maior atenção aos detalhes na comunicação e no planejamento.',
        'pontos_fortes': 'Você combina persuasão e carisma (I) com uma abordagem mais estruturada e analítica (C), sendo capaz de apresentar ideias de forma envolvente e organizada.',
        'areas_desenvolvimento': 'Trabalhe a paciência e a atenção aos detalhes (C) de forma que sua expressividade (I) seja complementada por uma comunicação mais precisa e fundamentada.',
        'relacionamento_dicas': 'Equilibre a energia e o entusiasmo (I) com uma postura analítica (C), utilizando fatos e dados para reforçar sua mensagem e construir relações de confiança.'
    },
    ('S', 'C'): {
        'descricao': 'Com o perfil primário Estabilidade (S), você preza pela cooperação e harmonia. O secundário Conformidade (C) acrescenta uma leve influência de organização e atenção aos detalhes, de forma moderada.',
        'motivacao': 'Enquanto o S é motivado pela segurança e apoio, o C o impulsiona a buscar clareza e precisão na execução de tarefas.',
        'caracteristicas': 'A influência do C se manifesta discretamente, promovendo uma abordagem estruturada que complementa a natural cooperação do S.',
        'pontos_fortes': 'Essa integração favorece a comunicação clara e fundamentada, enriquecendo o ambiente com uma base de organização e análise sem comprometer a harmonia.',
        'areas_desenvolvimento': 'Busque desenvolver mais flexibilidade e reduzir a autocrítica, para que a busca por precisão não impeça uma interação mais fluida e adaptativa.',
        'relacionamento_dicas': 'Combine sua postura acolhedora (S) com uma comunicação estruturada (C), promovendo um ambiente onde a colaboração e a clareza caminhem juntas.'
    }
}

# Nota: Os textos 'como_voce_e' e 'como_pode_melhorar' não estavam explicitamente
# no arquivo "perfis secuncarios caso a caso.txt" e foram omitidos
# das interpretações específicas acima. Se forem necessários, precisarão ser
# criados ou adaptados das outras seções (ex: 'relacionamento_dicas' ou 'areas_desenvolvimento').