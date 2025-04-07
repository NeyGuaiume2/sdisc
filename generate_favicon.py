import os
from PIL import Image, ImageDraw, ImageFont

def create_favicon(text='D', size=16, output_dir='backend/static/images'):
    """
    Cria um favicon simples com a letra representativa do DISC

    Args:
        text (str): Letra a ser exibida no favicon (D, I, S ou C)
        size (int): Tamanho do favicon (recomendado 16, 32, 64)
        output_dir (str): Diretório para salvar o favicon
    """
    # Criar o diretório se não existir
    os.makedirs(output_dir, exist_ok=True)

    # Paleta de cores DISC
    disc_colors = {
        'D': (220, 53, 69),    # Vermelho (Dominância)
        'I': (255, 193, 7),    # Amarelo (Influência)
        'S': (40, 167, 69),    # Verde (Estabilidade)
        'C': (23, 162, 184)    # Azul-petróleo (Conformidade)
    }

    # Selecionar cor baseada na letra
    bg_color = disc_colors.get(text, (100, 100, 100))

    # Criar imagem
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Desenhar círculo de fundo
    draw.ellipse((1, 1, size-1, size-1), fill=bg_color, outline=bg_color)

    # Adicionar letra
    try:
        # Tente usar uma fonte do sistema
        font = ImageFont.truetype("arial.ttf", size=size-2)
    except IOError:
        # Fallback para fonte padrão
        font = ImageFont.load_default()

    # Calcular posição para centralizar a letra
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    position = ((size - text_width) // 2, (size - text_height) // 2)

    # Desenhar letra em branco
    draw.text(position, text, font=font, fill=(255, 255, 255))

    # Salvar em múltiplos tamanhos
    sizes = [16, 32, 48, 64]
    for s in sizes:
        resized = img.resize((s, s), Image.LANCZOS)
        output_path = os.path.join(output_dir, f'favicon-{s}.ico')
        resized.save(output_path, format='ICO')

    # Salvar favicon padrão
    img.save(os.path.join(output_dir, 'favicon.ico'), format='ICO')

    print(f"Favicon gerado com sucesso na pasta {output_dir}")

# Gerar favicons para cada tipo DISC
disc_types = ['D', 'I', 'S', 'C']
for disc_type in disc_types:
    create_favicon(disc_type)