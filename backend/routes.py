# backend/routes.py

import sys
import os
from io import BytesIO
from typing import Dict, Any, Optional, List, Tuple # Adicionado Tuple

from flask import (
    Blueprint, render_template, request, jsonify,
    redirect, url_for, current_app, session, abort,
    Response, send_file
)

# --- Imports do ReportLab ---
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    BaseDocTemplate, PageTemplate, Frame, Flowable # Adicionado para Page Numbers e Header/Footer se necessário
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT # Adicionado TA_RIGHT

# --- Importações locais ---
try:
    from .disc_data import disc_descriptions, disc_questions
    from .score_calculator import calculate_disc_scores
    from .db import db
    from .models.disc_result import DISCResult
    from .interpretation_logic import get_all_interpretations # Função principal
    # Se você precisar da função de intensidade no PDF também:
    from .interpretation_logic import get_intensity_key
except ImportError as e:
    print(f"ERRO CRÍTICO: Falha ao importar dependências essenciais do backend: {e}")
    import traceback
    traceback.print_exc()
    raise ImportError(f"Erro ao importar módulos do backend: {e}") from e

# --- DEFINIÇÃO DO BLUEPRINT ---
main_bp = Blueprint('main', __name__)

# --- Estilos Globais para ReportLab ---
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, spaceAfter=6))
styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT)) # Estilo para alinhar à direita (pag num)
styles.add(ParagraphStyle(name='Footer', alignment=TA_CENTER, textColor=colors.grey, fontSize=8)) # Estilo Footer
styles.add(ParagraphStyle(name='H2', parent=styles['h2'], spaceBefore=12, spaceAfter=8)) # Ajuste H2
styles.add(ParagraphStyle(name='H3', parent=styles['h3'], spaceBefore=10, spaceAfter=6)) # Ajuste H3
styles.add(ParagraphStyle(name='H4PDF', parent=styles['h4'], spaceBefore=8, spaceAfter=4, alignment=TA_LEFT)) # H4 para subtítulos PDF
styles.add(ParagraphStyle(name='SubTitlePDF', parent=styles['Normal'], fontName='Helvetica-Bold', spaceBefore=6, spaceAfter=3)) # Subtítulos menores
styles.add(ParagraphStyle(name='ListItem', parent=styles['Normal'], leftIndent=18, spaceAfter=3))
styles.add(ParagraphStyle(name='AlertInfoPDF', parent=styles['Normal'], backColor=colors.lightblue, borderColor=colors.darkblue, borderPadding=5, spaceBefore=8, spaceAfter=8, leading=14)) # Estilo alerta
styles.add(ParagraphStyle(name='AlertWarningPDF', parent=styles['Normal'], backColor=colors.lightyellow, borderColor=colors.orange, borderPadding=5, spaceBefore=8, spaceAfter=8, leading=14)) # Estilo alerta
styles.add(ParagraphStyle(name='SmallMuted', parent=styles['Normal'], textColor=colors.grey, fontSize=styles['Normal'].fontSize * 0.9))
# Estilo Italic provavelmente já existe, não adicionar

# --- Funções Auxiliares para PDF ---

def normalize_score_to_100(score: Optional[float], min_possible: float = -28.0, max_possible: float = 28.0) -> float:
    """Normaliza o score DISC para uma escala de 0 a 100 (Python version)."""
    if score is None:
        return 0.0 # Ou talvez 50.0? 0 parece mais seguro para gráfico de barra
    # Garante que score é float
    try:
        numeric_score = float(score)
    except (ValueError, TypeError):
        return 0.0

    range_val = max_possible - min_possible
    if range_val == 0:
        return 50.0 # Avoid division by zero

    normalized = ((numeric_score - min_possible) / range_val) * 100.0
    return max(0.0, min(100.0, normalized)) # Clamp between 0 and 100

def add_interpretation_section_pdf(
    story: List[Flowable],
    title: str,
    interpretation_data: Optional[Dict[str, Any]],
    fields_to_include: List[Tuple[str, str, ParagraphStyle]], # Lista de (chave_json, titulo_pdf, estilo_paragrafo)
    title_style: ParagraphStyle = styles['H4PDF'],
    alert_fields: Optional[Dict[str, ParagraphStyle]] = None # Mapeia chave_json para estilo de alerta
):
    """Adiciona uma seção de interpretação formatada ao story do PDF."""
    if not interpretation_data:
        story.append(Paragraph(f"<i>{title}: Dados não disponíveis.</i>", styles['Italic']))
        story.append(Spacer(1, 0.1*inch))
        return

    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.05*inch))

    alert_fields = alert_fields or {}

    for json_key, pdf_subtitle, content_style in fields_to_include:
        content = interpretation_data.get(json_key)
        if content:
            # Define o estilo, verificando se é um campo de alerta
            current_style = alert_fields.get(json_key, content_style)
            current_title_style = styles['SubTitlePDF']

            # Adiciona subtítulo apenas se não for alerta (alertas têm o título implícito)
            if json_key not in alert_fields:
                 story.append(Paragraph(pdf_subtitle, current_title_style))

            if isinstance(content, list):
                for item in content:
                    # Garante que item é string e remove espaços extras
                    item_text = str(item).strip()
                    if item_text:
                        story.append(Paragraph(f"• {item_text}", styles['ListItem']))
                story.append(Spacer(1, 0.05*inch)) # Espaço após lista
            elif isinstance(content, str):
                 # Substitui \n por <br/> para quebras de linha no PDF
                 formatted_content = content.strip().replace('\n', '<br/>')
                 if formatted_content:
                     story.append(Paragraph(formatted_content, current_style))
                     story.append(Spacer(1, 0.1*inch))
            else:
                 # Tenta converter para string se não for lista ou string
                 try:
                     str_content = str(content).strip().replace('\n', '<br/>')
                     if str_content:
                         story.append(Paragraph(str_content, current_style))
                         story.append(Spacer(1, 0.1*inch))
                 except Exception as e:
                      current_app.logger.error(f"Erro ao formatar conteúdo PDF para {json_key}: {e}")

def header_footer(canvas, doc):
    """Adiciona cabeçalho/rodapé simples a cada página."""
    canvas.saveState()
    # Rodapé com número da página
    page_num = canvas.getPageNumber()
    text = f"Página {page_num}"
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(A4[0] - doc.rightMargin - 0.5*cm, doc.bottomMargin - 0.5*cm, text)
    # Pode adicionar um header aqui se desejar
    # canvas.drawString(doc.leftMargin, A4[1] - doc.topMargin + 0.5*cm, "Relatório DISC Confidencial")
    canvas.restoreState()


# --- ROTAS (mantidas iguais, exceto download_pdf) ---

@main_bp.route('/')
# ... (código da rota index igual) ...
def index():
    current_app.logger.info("Acessando rota / (index)")
    error_message = request.args.get('error')
    return render_template('index.html', error_message=error_message)

@main_bp.route('/quiz')
# ... (código da rota quiz igual) ...
def quiz():
    current_app.logger.info("Acessando rota /quiz")
    try:
        questions_list = disc_questions
        total_questions = len(questions_list) if questions_list else 0
        current_app.logger.info(f"Renderizando quiz.html com total_questions={total_questions}")
    except NameError:
        current_app.logger.error("Erro Crítico: 'disc_questions' não definido na rota /quiz, apesar do import inicial.", exc_info=True)
        total_questions = 0
    except Exception as e:
        current_app.logger.error(f"Erro inesperado ao obter/contar disc_questions na rota /quiz: {e}", exc_info=True)
        total_questions = 0
    return render_template('quiz.html', total_questions=total_questions)

@main_bp.route('/api/questions')
# ... (código da rota api/questions igual) ...
def get_questions_api():
    current_app.logger.info("Acessando rota /api/questions")
    try:
        if not disc_questions or not isinstance(disc_questions, list):
            current_app.logger.error("API /api/questions: 'disc_questions' inválida ou não carregada.")
            return jsonify({"error": "Lista de questões não disponível ou inválida."}), 500
        return jsonify(disc_questions)
    except NameError:
        current_app.logger.error("Erro Crítico: 'disc_questions' não definido na API /api/questions, apesar do import inicial.", exc_info=True)
        return jsonify({"error": "Erro interno crítico: dados das questões não encontrados."}), 500
    except Exception as e:
        current_app.logger.exception("API /api/questions: Erro inesperado ao processar requisição.")
        return jsonify({"error": "Erro interno ao obter questões."}), 500

@main_bp.route('/api/calculate', methods=['POST'])
# ... (código da rota api/calculate igual) ...
def calculate_results_api():
    current_app.logger.info("Acessando rota /api/calculate (POST)")
    if not request.is_json:
        current_app.logger.error("/api/calculate: Requisição não é JSON.")
        return jsonify({"success": False, "error": "Requisição deve ser JSON."}), 400

    data = request.get_json()
    if not data:
        current_app.logger.error("/api/calculate: Payload JSON vazio.")
        return jsonify({"success": False, "error": "Payload JSON vazio."}), 400

    raw_answers = data.get('answers')
    user_info = data.get('userInfo', {})
    user_name = user_info.get('name') if isinstance(user_info.get('name'), str) else None
    user_email = user_info.get('email') if isinstance(user_info.get('email'), str) else None

    user_name = user_name.strip() if user_name else None
    user_email = user_email.strip() if user_email else None
    user_name = user_name if user_name else None
    user_email = user_email if user_email else None

    if not raw_answers or not isinstance(raw_answers, list):
        current_app.logger.warning(f"/api/calculate: Payload inválido. 'answers' ausente, não é lista ou está vazio. Recebido: {raw_answers}")
        return jsonify({"success": False, "error": "Payload inválido ('answers' ausente ou formato incorreto)."}), 400

    current_app.logger.info(f"Recebidas {len(raw_answers)} respostas. User: {user_name or user_email or 'Anon'}")
    current_app.logger.debug(f"Payload 'answers' (início): {str(raw_answers)[:200]}...")
    current_app.logger.debug(f"UserInfo recebido: {user_info}")

    try:
        calculated_result_dict = calculate_disc_scores(raw_answers)
        if calculated_result_dict is None or not isinstance(calculated_result_dict, dict):
            current_app.logger.error(f"Falha no cálculo DISC. Retorno de calculate_disc_scores: {calculated_result_dict}")
            return jsonify({"success": False, "error": "Falha interna no cálculo dos scores."}), 500
        current_app.logger.debug(f"Resultado calculado: {calculated_result_dict}")

        new_result_entry = DISCResult(
            user_name=user_name,
            user_email=user_email,
            raw_responses=raw_answers,
            disc_result=calculated_result_dict
        )

        db.session.add(new_result_entry)
        db.session.commit()
        current_app.logger.info(f"Resultado DISC salvo ID: {new_result_entry.id}, Perfil: {new_result_entry.primary_type}/{new_result_entry.secondary_type}, User: {new_result_entry.user_name or new_result_entry.user_email or 'Anon'}")

        session['disc_result_id'] = new_result_entry.id
        session.pop('quiz_results', None)

        return jsonify({"success": True, "result_id": new_result_entry.id})

    except KeyError as e:
        db.session.rollback()
        current_app.logger.error(f"Erro de chave ausente durante cálculo/salvamento: {e}. Verifique o retorno de 'calculate_disc_scores'.", exc_info=True)
        return jsonify({"success": False, "error": f"Erro interno: chave de dados esperada ausente ({e})."}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Erro inesperado durante cálculo ou salvamento do resultado DISC.")
        return jsonify({"success": False, "error": "Erro interno inesperado ao processar o teste."}), 500

@main_bp.route('/results')
# ... (código da rota results igual) ...
def show_results():
    current_app.logger.info("Acessando rota /results")
    result_id = session.get('disc_result_id')
    if not result_id:
        current_app.logger.warning("Tentativa de acessar /results sem result_id na sessão.")
        return redirect(url_for('main.index', error='session_expired'))

    try:
        result_data = db.session.get(DISCResult, result_id)
        if result_data is None:
             current_app.logger.warning(f"Resultado com ID {result_id} não encontrado no DB ao acessar /results. Removendo da sessão.")
             session.pop('disc_result_id', None)
             return redirect(url_for('main.index', error='result_not_found'))

        primary_type = result_data.primary_type
        secondary_type = result_data.secondary_type
        disc_scores = result_data.get_scores()
        scores_for_javascript = disc_scores

        if disc_scores is None:
            current_app.logger.error(f"Scores não puderam ser obtidos do resultado ID {result_id} (get_scores retornou None). Não é possível gerar interpretações.")
            all_interpretations_data = { 'general': {'primary': {}, 'secondary': {}}, 'professional': {'primary': {}, 'secondary': {}} }
            primary_type = '?'
            secondary_type = '?'
        else:
            all_interpretations_data = get_all_interpretations( primary_type, secondary_type, disc_scores )

        current_app.logger.info(f"Exibindo resultados ID: {result_id}, User: {result_data.user_name or result_data.user_email or 'Anon'}, Perfil: {primary_type}/{secondary_type}")
        if primary_type == '?':
             current_app.logger.warning(f"Exibindo resultado ID {result_id} que foi salvo com perfil primário inválido ('?') ou scores não puderam ser lidos. Interpretações podem estar vazias ou incorretas.")

        return render_template(
            'results.html',
            result=result_data,
            interpretations=all_interpretations_data,
            scores_for_chart=scores_for_javascript
        )
    except Exception as e:
        current_app.logger.exception(f"Erro inesperado ao carregar /results para ID {result_id}.")
        abort(500, description="Erro interno ao carregar os resultados.")

# --- Rota para Download do PDF (Refatorada para PDF Completo) ---
@main_bp.route('/results/<int:result_id>/download_pdf')
def download_pdf(result_id):
    current_app.logger.info(f"Gerando PDF completo para resultado ID: {result_id}")

    # 1. Buscar os dados do resultado e interpretações
    try:
        result_data = db.session.get(DISCResult, result_id)
        if result_data is None:
            abort(404, description="Resultado não encontrado.")

        primary_type = result_data.primary_type
        secondary_type = result_data.secondary_type
        scores = result_data.get_scores()

        if scores is None:
            current_app.logger.error(f"Scores não puderam ser obtidos para PDF completo (ID: {result_id}).")
            abort(500, description="Erro ao carregar dados de scores para o PDF.")

        # Obtém todas as interpretações usando a mesma lógica da página de resultados
        all_interpretations = get_all_interpretations(primary_type, secondary_type, scores)

        # Separa para facilitar o acesso
        primary_gen = all_interpretations.get('general', {}).get('primary', {})
        secondary_gen = all_interpretations.get('general', {}).get('secondary', {})
        primary_prof = all_interpretations.get('professional', {}).get('primary', {})
        secondary_prof = all_interpretations.get('professional', {}).get('secondary', {})

        current_app.logger.info(f"Dados carregados para PDF. Perfil: {primary_type}/{secondary_type}. Interpretações obtidas.")

    except Exception as e:
        current_app.logger.exception(f"Erro ao buscar dados ou interpretações para PDF completo (ID: {result_id}).")
        abort(500, description="Erro interno ao preparar dados para o relatório PDF.")

    # 2. Gerar o PDF usando ReportLab
    buffer = BytesIO()
    margin = 1.5 * cm

    # Usar BaseDocTemplate para permitir header/footer
    doc = BaseDocTemplate(buffer, pagesize=A4,
                          leftMargin=margin, rightMargin=margin,
                          topMargin=margin, bottomMargin=margin * 1.5) # Mais espaço no bottom para footer

    # Define o frame principal
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height,
                  id='normal')

    # Cria o PageTemplate com o frame e a função onPage para header/footer
    main_template = PageTemplate(id='main', frames=[frame], onPage=header_footer)
    doc.addPageTemplates([main_template])

    story = []

    # --- Montagem do PDF Completo ---
    story.append(Paragraph("Relatório de Perfil Comportamental DISC", styles['h1']))
    story.append(Spacer(1, 0.3*inch))

    # Informações do Usuário e Data/Hora
    user_info_lines = []
    if result_data.user_name: user_info_lines.append(f"<b>Nome:</b> {result_data.user_name}")
    if result_data.user_email: user_info_lines.append(f"<b>Email:</b> {result_data.user_email}")
    if result_data.timestamp: user_info_lines.append(f"<b>Data:</b> {result_data.timestamp.strftime('%d/%m/%Y %H:%M:%S')} (UTC)")
    else: user_info_lines.append(f"<b>Data:</b> Indisponível")
    for line in user_info_lines: story.append(Paragraph(line, styles['Center']))
    story.append(Spacer(1, 0.4*inch))

    # --- Seção de Resumo e Gráfico ---
    story.append(Paragraph("Resumo do Perfil e Pontuações", styles['H2']))
    story.append(Spacer(1, 0.1*inch))

    # Resumo dos Perfis
    primary_title_pdf = primary_gen.get('title', primary_type)
    secondary_title_pdf = secondary_gen.get('title', secondary_type if secondary_type != '?' else 'N/A')

    story.append(Paragraph(f"<b>Perfil Primário:</b> {primary_type} ({primary_title_pdf}) - Nível: {primary_gen.get('level', '?').capitalize()}", styles['Normal']))
    if secondary_gen and secondary_gen.get('type'):
         story.append(Paragraph(f"<b>Influência Secundária:</b> {secondary_gen['type']} ({secondary_title_pdf}) - Nível: {secondary_gen.get('level', '?').capitalize()}", styles['Normal']))
    else:
         story.append(Paragraph("<b>Influência Secundária:</b> Nenhuma significativa", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

    # Tabela de Scores (Originais)
    score_data = [['Fator', 'Pontuação Original']]
    score_colors = {'D': colors.HexColor('#FF7F7F'), 'I': colors.HexColor('#FFBF7F'), 'S': colors.HexColor('#FFFF7F'), 'C': colors.HexColor('#7FFFFF')}
    for factor, score in scores.items():
        factor_name = disc_descriptions.get(factor, {}).get('title', factor)
        score_data.append([factor_name, str(score)])
    score_table = Table(score_data, colWidths=[2*inch, 1.5*inch]) # Ajuste largura
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkgrey), # Cor Header
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('BACKGROUND', (0,1), (-1,-1), colors.white), # Fundo branco
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.3*inch))

    # Gráfico de Barras (NORMALIZADO 0-100)
    try:
        drawing = Drawing(400, 200)
        # Normaliza os scores para o gráfico
        norm_d = normalize_score_to_100(scores.get('D'))
        norm_i = normalize_score_to_100(scores.get('I'))
        norm_s = normalize_score_to_100(scores.get('S'))
        norm_c = normalize_score_to_100(scores.get('C'))
        bc_data = [(norm_d, norm_i, norm_s, norm_c)] # Reportlab precisa de lista de tuplas/listas

        bc = VerticalBarChart()
        bc.x = 50; bc.y = 50; bc.height = 125; bc.width = 300
        bc.data = bc_data
        bc.strokeColor = colors.black
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = 100 # Eixo vai até 100
        bc.valueAxis.valueStep = 20 # Steps de 20
        bc.valueAxis.labelTextFormat = '%d%%' # Adiciona % ao label do eixo Y
        bc.categoryAxis.labels.boxAnchor = 'ne'; bc.categoryAxis.labels.dx = 8; bc.categoryAxis.labels.dy = -2
        cat_names = [
            disc_descriptions.get('D', {}).get('title', 'D'), disc_descriptions.get('I', {}).get('title', 'I'),
            disc_descriptions.get('S', {}).get('title', 'S'), disc_descriptions.get('C', {}).get('title', 'C')
        ]
        bc.categoryAxis.categoryNames = cat_names
        bc.bars[(0, 0)].fillColor = score_colors.get('D', colors.black)
        bc.bars[(0, 1)].fillColor = score_colors.get('I', colors.black)
        bc.bars[(0, 2)].fillColor = score_colors.get('S', colors.black)
        bc.bars[(0, 3)].fillColor = score_colors.get('C', colors.black)

        chart_title = Paragraph("Gráfico do Perfil (Intensidade Normalizada %)", styles['Center'])
        story.append(chart_title)
        story.append(Spacer(1, 0.1*inch))
        drawing.add(bc)
        story.append(drawing)
        story.append(Spacer(1, 0.3*inch))
    except Exception as chart_err:
        current_app.logger.error(f"Erro ao gerar gráfico normalizado PDF para ID {result_id}: {chart_err}", exc_info=True)
        story.append(Paragraph("<i>Erro ao gerar o gráfico de pontuações.</i>", styles.get('Italic', styles['Normal'])))
        story.append(Spacer(1, 0.3*inch))

    # --- Seção de Interpretação Geral ---
    story.append(Paragraph("Visão Geral do Perfil", styles['H2']))
    story.append(Spacer(1, 0.1*inch))

    # Campos a incluir e seus estilos
    general_fields = [
        ('Descrição', 'Descrição', styles['Justify']),
        ('Motivação', 'Motivação', styles['Justify']),
        ('Características', 'Características', styles['Justify']),
        ('Pontos Fortes', 'Pontos Fortes', styles['Justify']),
        ('Áreas de Desenvolvimento', 'Áreas de Desenvolvimento', styles['Justify']),
        ('Relacionamento/Dicas', 'Relacionamento/Dicas', styles['Justify']),
        ('Como Você É (Tendência Natural)', 'Tendência Natural:', styles['AlertInfoPDF']), # Alerta
        ('Como Pode Melhorar (Reflexão para Crescimento)', 'Reflexão para Crescimento:', styles['AlertWarningPDF']) # Alerta
    ]
    alert_styles_gen = {
        'Como Você É (Tendência Natural)': styles['AlertInfoPDF'],
        'Como Pode Melhorar (Reflexão para Crescimento)': styles['AlertWarningPDF']
    }

    # Geral Primário
    if primary_gen and primary_gen.get('type'):
         title = f"Perfil Primário: {primary_gen['title']} ({primary_gen['type']}) - Nível {primary_gen.get('level', '?').capitalize()}"
         add_interpretation_section_pdf(story, title, primary_gen, general_fields, title_style=styles['H3'], alert_fields=alert_styles_gen)
    else:
         story.append(Paragraph("Interpretação geral primária não disponível.", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

    # Geral Secundário
    if secondary_gen and secondary_gen.get('type'):
        title = f"Influência Secundária: {secondary_gen['title']} ({secondary_gen['type']}) - Nível {secondary_gen.get('level', '?').capitalize()}"
        story.append(Paragraph("<i>Esta influência secundária complementa suas características principais.</i>", styles.get('Italic', styles['Normal'])))
        story.append(Spacer(1, 0.1*inch))
        # Ajusta títulos para indicar influência
        secondary_general_fields = [ (k, f"{v} (Influência)", s) if k not in alert_styles_gen else (k,v,s) for k,v,s in general_fields]
        add_interpretation_section_pdf(story, title, secondary_gen, secondary_general_fields, title_style=styles['H3'], alert_fields=alert_styles_gen)
    elif primary_type != '?' and secondary_type != '?': # Só mostra se o secundário era esperado
        story.append(Paragraph(f"Interpretação da influência secundária ({secondary_type}) não encontrada.", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))


    # --- Seção de Análise Profissional ---
    story.append(Paragraph("Análise Profissional", styles['H2']))
    story.append(Spacer(1, 0.1*inch))

    # Função auxiliar para pegar os campos profissionais (assumindo que são todas as chaves exceto as de controle)
    def get_professional_fields(data: Dict[str, Any]) -> List[Tuple[str, str, ParagraphStyle]]:
        fields = []
        if not data: return fields
        control_keys = ['type', 'level', 'title', 'score']
        for key, value in data.items():
            if key not in control_keys and value: # Inclui apenas se a chave não for de controle e tiver valor
                 fields.append((key, key.replace('_', ' '), styles['Justify'])) # Usa a chave como título
        return fields

    # Profissional Primário
    if primary_prof and primary_prof.get('type'):
         title = f"Tendências Profissionais - {primary_gen.get('title', primary_type)} ({primary_type})" # Usa título geral
         prof_fields = get_professional_fields(primary_prof)
         add_interpretation_section_pdf(story, title, primary_prof, prof_fields, title_style=styles['H3'])
    else:
         story.append(Paragraph("Análise profissional primária não disponível.", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

    # Profissional Secundário
    if secondary_prof and secondary_prof.get('type'):
        title = f"Influência Profissional Secundária - {secondary_gen.get('title', secondary_type)} ({secondary_type})" # Usa título geral
        story.append(Paragraph("<i>Como a influência secundária molda suas tendências profissionais.</i>", styles.get('Italic', styles['Normal'])))
        story.append(Spacer(1, 0.1*inch))
        prof_fields_sec = get_professional_fields(secondary_prof)
        # Ajusta títulos para indicar influência
        secondary_prof_fields = [ (k, f"{v} (Influência)", s) for k,v,s in prof_fields_sec]
        add_interpretation_section_pdf(story, title, secondary_prof, secondary_prof_fields, title_style=styles['H3'])
    elif primary_type != '?' and secondary_type != '?':
        story.append(Paragraph(f"Análise da influência profissional secundária ({secondary_type}) não encontrada.", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

    # --- Fim Conteúdo do PDF ---
    try:
        doc.build(story)
        current_app.logger.info(f"Documento PDF completo construído com sucesso para ID {result_id}.")
    except Exception as pdf_build_err:
        current_app.logger.exception(f"Erro ao construir o documento PDF completo com ReportLab para ID {result_id}.")
        abort(500, "Erro interno ao gerar o arquivo PDF completo.")

    buffer.seek(0)
    safe_user_name = ''.join(c for c in (result_data.user_name or 'Resultado') if c.isalnum() or c in ['_', '-']).rstrip('_').strip()
    safe_user_name = safe_user_name if safe_user_name else 'Resultado'
    filename = f"Relatorio_DISC_{safe_user_name}_{result_id}.pdf" # Nome do arquivo ajustado
    current_app.logger.info(f"Enviando PDF completo gerado: {filename}")

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

# --- Tratamento de Erros (sem alterações) ---
@main_bp.app_errorhandler(404)
# ... (código igual) ...
def page_not_found(e):
    description = getattr(e, "description", "Página não encontrada.")
    current_app.logger.warning(f"Erro 404: {request.path} - Descrição: {description}")
    try:
        return render_template('errors/404.html', error_description=description), 404
    except:
        return f"Erro 404: {description}", 404

@main_bp.app_errorhandler(500)
# ... (código igual) ...
def internal_server_error(e):
    original_exception = getattr(e, "original_exception", e)
    description = getattr(e, "description", "Erro interno do servidor.")
    try:
        current_app.logger.error(f"Erro 500: {request.path} - Descrição: {description}", exc_info=original_exception)
    except Exception as log_err:
        print(f"ERRO GRAVE NO LOGGER: {log_err}")
        print(f"Erro 500 Original: {request.path} - Descrição: {description}\n{original_exception}")

    try:
        db.session.rollback()
        current_app.logger.info("Sessão do DB revertida devido a erro 500.")
    except Exception as rollback_err:
        current_app.logger.error(f"Erro ao tentar reverter sessão do DB: {rollback_err}")

    try:
        return render_template('errors/500.html', error_message=description), 500
    except:
         return f"Erro 500: {description}", 500

@main_bp.app_errorhandler(403)
# ... (código igual) ...
def forbidden_access(e):
    description = getattr(e, "description", "Acesso proibido.")
    current_app.logger.warning(f"Erro 403: {request.path} - Descrição: {description}")
    try:
        return render_template('errors/403.html', error_description=description), 403
    except:
        return f"Erro 403: {description}", 403

# --- FIM DO ARQUIVO ---