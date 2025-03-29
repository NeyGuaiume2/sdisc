import os

IGNORADOS = {".git", ".gitignore", "__pycache__", "venv", ".pytest_cache", ".github"}

def listar_estrutura(diretorio, prefixo=""):
    estrutura = []
    for item in sorted(os.listdir(diretorio)):
        caminho = os.path.join(diretorio, item)
        if item in IGNORADOS or item.startswith("."):  
            continue  
        if os.path.isdir(caminho):
            estrutura.append(f"{prefixo}{item}/")
            estrutura.extend(listar_estrutura(caminho, prefixo + "    "))
        else:
            estrutura.append(f"{prefixo}{item}")
    return estrutura

def gerar_arquivo_estrutura():
    raiz = os.getcwd()  
    estrutura = listar_estrutura(raiz)
    with open("estrutura_projeto.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(estrutura))
    print("Arquivo 'estrutura_projeto.txt' gerado com sucesso.")

if __name__ == "__main__":
    gerar_arquivo_estrutura()
