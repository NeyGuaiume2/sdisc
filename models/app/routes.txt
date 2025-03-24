# Arquivo: c:\pyp\sdisc\app\routes.py

# Adicione as seguintes rotas ao arquivo routes.py

@app.route('/results/<session_id>')
def view_results(session_id):
    """Exibe os resultados da avaliação DISC"""
    # Buscar resultado pelo session_id
    result = DISCResult.query.filter_by(session_id=session_id).first_or_404()
    
    # Obter dados para o gráfico
    chart_data = {
        'labels': ['Dominância', 'Influência', 'Estabilidade', 'Conformidade'],
        'values': [result.d_score, result.i_score, result.s_score, result.c_score]
    }
    
    # Obter interpretações de perfil
    profile_interpretations = get_profile_interpretations(result)
    
    return render_template(
        'results.html',
        result=result,
        chart_data=chart_data,
        profile_interpretations=profile_interpretations
    )

@app.route('/api/results/<session_id>')
def get_results_data(session_id):
    """API para obter dados dos resultados em formato JSON"""
    result = DISCResult.query.filter_by(session_id=session_id).first_or_404()
    
    # Criar dicionário com todos os dados necessários
    data = {
        'scores': {
            'D': result.d_score,
            'I': result.i_score,
            'S': result.s_score,
            'C': result.c_score
        },
        'intensities': {
            'D': result.d_intensity,
            'I': result.i_intensity,
            'S': result.s_intensity,
            'C': result.c_intensity
        },
        'profiles': {
            'primary': result.primary_profile,
            'secondary': result.secondary_profile
        },
        'date': result.date_created.strftime('%d/%m/%Y')
    }
    
    return jsonify(data)

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard administrativo para visualizar estatísticas"""
    # Obter todas as avaliações (limitando a 100 para performance)
    results = DISCResult.query.order_by(DISCResult.date_created.desc()).limit(100).all()
    
    # Calcular médias para cada perfil
    avg_d = sum([r.d_score for r in results]) / len(results) if results else 0
    avg_i = sum([r.i_score for r in results]) / len(results) if results else 0
    avg_s = sum([r.s_score for r in results]) / len(results) if results else 0
    avg_c = sum([r.c_score for r in results]) / len(results) if results else 0
    
    # Contagem de perfis predominantes
    profile_counts = {
        'D': sum(1 for r in results if r.primary_profile == 'D'),
        'I': sum(1 for r in results if r.primary_profile == 'I'),
        'S': sum(1 for r in results if r.primary_profile == 'S'),
        'C': sum(1 for r in results if r.primary_profile == 'C')
    }
    
    return render_template(
        'dashboard.html',
        results=results,
        averages={'D': avg_d, 'I': avg_i, 'S': avg_s, 'C': avg_c},
        profile_counts=profile_counts
    )

def get_profile_interpretations(result):
    """Gera interpretações de perfil com base nos resultados DISC"""
    interpretations = {}
    
    # Interpretação para Dominância
    if result.d_intensity == "Alto":
        interpretations['D'] = {
            'titulo': 'Alta Dominância',
            'descricao': 'Pessoas com alta dominância são diretas, decisivas, determinadas e orientadas a resultados. Gostam de desafios, ação e exercem liderança com facilidade.',
            'pontos_fortes': ['Foco em resultados', 'Determinação', 'Iniciativa', 'Solução de problemas'],
            'areas_desenvolvimento': ['Impaciência', 'Insensibilidade', 'Dificuldade em ouvir', 'Correr riscos desnecessários']
        }
    elif result.d_intensity == "Médio":
        interpretations['D'] = {
            'titulo': 'Dominância Moderada',
            'descricao': 'Pessoas com dominância moderada sabem balancear a assertividade com a cooperação. Podem assumir liderança quando necessário, mas também trabalhar em equipe.',
            'pontos_fortes': ['Equilíbrio entre assertividade e cooperação', 'Adaptabilidade', 'Bom senso de urgência'],
            'areas_desenvolvimento': ['Indecisão ocasional', 'Variação na confiança']
        }
    else:
        interpretations['D'] = {
            'titulo': 'Baixa Dominância',
            'descricao': 'Pessoas com baixa dominância são colaborativas, apoiadoras e preferem trabalhar em ambientes harmoniosos. Evitam confrontos e valorizam a estabilidade.',
            'pontos_fortes': ['Cooperação', 'Trabalho em equipe', 'Diplomacia', 'Sensibilidade'],
            'areas_desenvolvimento': ['Confrontar quando necessário', 'Tomar decisões difíceis', 'Autoconfiança']
        }
    
    # Interpretação para Influência
    if result.i_intensity == "Alto":
        interpretations['I'] = {
            'titulo': 'Alta Influência',
            'descricao': 'Pessoas com alta influência são extrovertidas, entusiasmadas, otimistas e gostam de interagir. São persuasivas e motivadoras, valorizando relações sociais.',
            'pontos_fortes': ['Comunicação', 'Entusiasmo', 'Networking', 'Persuasão'],
            'areas_desenvolvimento': ['Desorganização', 'Impulsividade', 'Falar mais que ouvir', 'Atenção aos detalhes']
        }
    elif result.i_intensity == "Médio":
        interpretations['I'] = {
            'titulo': 'Influência Moderada',
            'descricao': 'Pessoas com influência moderada equilibram socialização com tarefas. São razoavelmente comunicativas, mas também conseguem se concentrar no trabalho.',
            'pontos_fortes': ['Equilíbrio entre sociabilidade e foco', 'Comunicação eficaz', 'Versatilidade'],
            'areas_desenvolvimento': ['Consistência na comunicação', 'Gerenciamento de impressões']
        }
    else:
        interpretations['I'] = {
            'titulo': 'Baixa Influência',
            'descricao': 'Pessoas com baixa influência são mais reservadas e preferem trabalhar nos bastidores. Valorizam fatos e dados mais que emoções ou popularidade.',
            'pontos_fortes': ['Análise', 'Objetividade', 'Reflexão', 'Foco no conteúdo'],
            'areas_desenvolvimento': ['Expressão de ideias', 'Networking', 'Autopromoção']
        }
    
    # Continuar com interpretações para S e C (seguindo o mesmo padrão)
    # Interpretação para Estabilidade
    if result.s_intensity == "Alto":
        interpretations['S'] = {
            'titulo': 'Alta Estabilidade',
            'descricao': 'Pessoas com alta estabilidade são pacientes, leais e previsíveis. Valorizam a consistência e a segurança, sendo excelentes em fornecer apoio e manter a harmonia.',
            'pontos_fortes': ['Paciência', 'Lealdade', 'Consistência', 'Trabalho em equipe'],
            'areas_desenvolvimento': ['Resistência à mudança', 'Dificuldade em dizer não', 'Excesso de acomodação']
        }
    elif result.s_intensity == "Médio":
        interpretations['S'] = {
            'titulo': 'Estabilidade Moderada',
            'descricao': 'Pessoas com estabilidade moderada se adaptam às mudanças quando necessário, mas ainda valorizam certo nível de consistência. São flexíveis sem perder a confiabilidade.',
            'pontos_fortes': ['Adaptabilidade', 'Confiabilidade', 'Equilíbrio entre mudança e estabilidade'],
            'areas_desenvolvimento': ['Clareza nas preferências', 'Estabelecimento de prioridades']
        }
    else:
        interpretations['S'] = {
            'titulo': 'Baixa Estabilidade',
            'descricao': 'Pessoas com baixa estabilidade são flexíveis, adaptáveis e gostam de variedade. Preferem ambientes dinâmicos e não se incomodam com mudanças frequentes.',
            'pontos_fortes': ['Flexibilidade', 'Adaptabilidade', 'Multitarefa', 'Resposta rápida'],
            'areas_desenvolvimento': ['Constância', 'Paciência', 'Conclusão de projetos']
        }
    
    # Interpretação para Conformidade
    if result.c_intensity == "Alto":
        interpretations['C'] = {
            'titulo': 'Alta Conformidade',
            'descricao': 'Pessoas com alta conformidade são analíticas, organizadas, detalhistas e sistemáticas. Valorizam precisão, qualidade e o seguimento de procedimentos.',
            'pontos_fortes': ['Atenção aos detalhes', 'Análise crítica', 'Organização', 'Qualidade'],
            'areas_desenvolvimento': ['Perfeccionismo', 'Criticismo', 'Análise excessiva', 'Medo de errar']
        }
    elif result.c_intensity == "Médio":
        interpretations['C'] = {
            'titulo': 'Conformidade Moderada',
            'descricao': 'Pessoas com conformidade moderada valorizam a qualidade e os processos, mas conseguem ser flexíveis quando necessário. Equilibram atenção aos detalhes com praticidade.',
            'pontos_fortes': ['Equilíbrio entre padrões e flexibilidade', 'Pensamento lógico', 'Organização prática'],
            'areas_desenvolvimento': ['Consistência nos padrões', 'Definição clara de expectativas']
        }
    else:
        interpretations['C'] = {
            'titulo': 'Baixa Conformidade',
            'descricao': 'Pessoas com baixa conformidade são pragmáticas e focadas em resultados mais que em processos. São orientadas à ação e preferem abordagens informais.',
            'pontos_fortes': ['Pragmatismo', 'Rapidez', 'Foco em soluções', 'Criatividade'],
            'areas_desenvolvimento': ['Organização', 'Planejamento', 'Atenção aos detalhes']
        }
    
    return interpretations