import secrets
import os
import re

def generate_secret_key():
    """Gera uma chave secreta segura usando o módulo secrets"""
    return secrets.token_hex(32)

def update_prod_config(new_secret_key):
    """Atualiza a SECRET_KEY no arquivo prod_config.py"""
    config_path = 'prod_config.py'
    
    # Verifica se o arquivo existe
    if not os.path.exists(config_path):
        print(f"Erro: O arquivo {config_path} não foi encontrado.")
        return False
    
    # Lê o conteúdo atual
    with open(config_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Substitui a SECRET_KEY existente
    if 'SECRET_KEY' in content:
        new_content = re.sub(
            r"SECRET_KEY\s*=\s*['\"](.*?)['\"]", 
            f"SECRET_KEY = '{new_secret_key}'", 
            content
        )
        
        # Escreve o novo conteúdo
        with open(config_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        return True
    else:
        print("Erro: Não foi possível encontrar a variável SECRET_KEY no arquivo.")
        return False

if __name__ == "__main__":
    print("Gerando nova chave secreta para o projeto DISC...")
    
    # Gera a nova chave
    secret_key = generate_secret_key()
    
    # Atualiza o arquivo de configuração
    if update_prod_config(secret_key):
        print("\n✅ Secret Key gerada e atualizada com sucesso!")
        print(f"\nNova SECRET_KEY: {secret_key}")
        print("\nEssa chave foi automaticamente salva no arquivo prod_config.py")
        print("\nOBS: Em ambientes de produção, considere usar variáveis de ambiente")
        print("     para armazenar informações sensíveis como esta.")
    else:
        print("\n❌ Falha ao atualizar o arquivo de configuração.")
        print(f"\nChave gerada (salve manualmente): {secret_key}")
