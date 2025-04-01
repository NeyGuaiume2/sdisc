from playwright.sync_api import sync_playwright
import os
import shutil # Para apagar a pasta de vídeos antigos

# --- Configurações ---
# 1. Diretório onde os vídeos serão salvos (será criado se não existir)
videos_dir = "playwright-videos" # Cria pasta na raiz do projeto

# 2. (Opcional) Apagar vídeos antigos antes de executar?
delete_old_videos = True # Mude para False se quiser manter vídeos de execuções anteriores

# --- Lógica ---

# Apaga o diretório de vídeos antigos, se configurado
if delete_old_videos and os.path.exists(videos_dir):
    print(f"Limpando diretório de vídeos antigos: {videos_dir}")
    try:
        shutil.rmtree(videos_dir)
        print("Diretório antigo removido.")
    except OSError as e:
        print(f"Erro ao remover diretório antigo: {e}")
        # exit() # Descomente para parar se a limpeza falhar

# Garante que o diretório de vídeos existe (cria se necessário)
try:
    os.makedirs(videos_dir, exist_ok=True)
    print(f"Diretório de vídeos pronto: {videos_dir}")
except OSError as e:
     print(f"Erro ao criar diretório de vídeos: {e}")
     exit() # Sai se não conseguir criar a pasta de destino

print("Iniciando Playwright com Chromium padrão...")
print(f"Vídeos serão salvos em: {os.path.abspath(videos_dir)}")

with sync_playwright() as p:
    try:
        # --- USA O CHROMIUM PADRÃO ---
        browser = p.chromium.launch(
            headless=False # Mantenha False para ver o navegador durante o teste
        )
        # -----------------------------
    except Exception as e:
        print(f"Falha ao iniciar o Chromium: {e}")
        exit()

    # --- CRIA O CONTEXTO COM GRAVAÇÃO DE VÍDEO ---
    try:
        context = browser.new_context(
            record_video={
                "dir": videos_dir,  # Pasta onde salvar
                # "size": {"width": 1280, "height": 720} # Opcional: define tamanho
            },
            viewport={'width': 1280, 'height': 720} # Exemplo: define tamanho da janela
        )
        print("Contexto do navegador criado com gravação de vídeo ativada.")
    except Exception as e:
        print(f"Falha ao criar contexto do navegador: {e}")
        browser.close()
        exit()

    page = context.new_page()

    try:
        print("Iniciando a execução do teste...")
        # ==================================================
        # == COLOQUE SEU CÓDIGO DE TESTE PLAYWRIGHT AQUI ==
        # ==================================================
        # Exemplo:
        # Assegure-se que seu servidor Flask está rodando em http://127.0.0.1:5000
        print("Acessando a aplicação Flask...")
        page.goto("http://127.0.0.1:5000/")
        print(f"Acessou: {page.title()}")
        page.wait_for_timeout(1000)

        print("Procurando link para iniciar o teste...")
        # Use um seletor robusto que funcione na sua página index.html
        # Exemplos: por texto, por id, por classe, etc.
        quiz_link = page.locator('a:text-matches("Iniciar Teste", "i")').first # Case-insensitive
        # quiz_link = page.locator('#start-quiz-button') # Se tiver um ID

        if quiz_link.is_visible():
             print("Clicando no link do quiz...")
             quiz_link.click()
             print("Esperando pela URL do quiz...")
             page.wait_for_url("**/quiz", timeout=10000) # Espera até 10s
             print(f"Página do Quiz carregada: {page.title()}")
             page.wait_for_timeout(2000) # Pausa para visualização
        else:
             print("ERRO: Link para iniciar o teste não encontrado ou não visível.")
             # Você pode querer parar o teste aqui ou tirar um screenshot
             page.screenshot(path=os.path.join(videos_dir, 'erro_link_nao_encontrado.png'))


        # Adicione aqui a lógica para responder o quiz, submeter, ir para resultados, etc.
        # Exemplo: Clicar na primeira opção "mais" da primeira pergunta
        # first_mais = page.locator('.question-group').first.locator('input[name="q1_mais"]').first
        # if first_mais.is_visible():
        #      print("Selecionando primeira opção 'mais'...")
        #      first_mais.click()
        #      page.wait_for_timeout(500)
        # else:
        #      print("ERRO: Primeira opção 'mais' não encontrada.")

        # ... continue com as interações ...

        print("Simulando fim do teste...")
        page.wait_for_timeout(2000)

        # ==================================================
        # == FIM DO SEU CÓDIGO DE TESTE                  ==
        # ==================================================
        print("Execução do teste concluída.")

    except Exception as e:
        print(f"ERRO DURANTE A EXECUÇÃO DO TESTE: {e}")
        # Tira um screenshot no momento do erro para ajudar a depurar
        screenshot_path = os.path.join(videos_dir, 'erro_execucao_teste.png')
        try:
            page.screenshot(path=screenshot_path)
            print(f"Screenshot do erro salvo em: {screenshot_path}")
        except Exception as screen_e:
            print(f"Não foi possível salvar screenshot do erro: {screen_e}")
        # O vídeo ainda será salvo (até o ponto do erro) quando o contexto for fechado

    finally:
        # --- FECHAR CONTEXTO E BROWSER É ESSENCIAL ---
        print("Fechando contexto (salvando vídeo)...")
        context.close() # Salva o vídeo
        print("Fechando navegador...")
        browser.close()
        print("Playwright finalizado.")