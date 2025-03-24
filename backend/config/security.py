# backend/config/security.py
import secrets
import os
from flask import Flask
from flask_talisman import Talisman
from datetime import timedelta

def configure_app_security(app: Flask) -> None:
    """
    Configura as medidas de segurança para o aplicativo Flask
    
    Args:
        app: Instância do aplicativo Flask
    """
    # Gerar uma chave secreta forte se não existir no ambiente
    if not app.config.get('SECRET_KEY'):
        # Em produção, essa chave deve ser configurada como variável de ambiente
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    
    # Configurar sessões seguras
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Configurar proteções contra CSRF
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hora
    
    # Configurar cabeçalhos de segurança com Talisman
    csp = {
        'default-src': ["'self'"],
        'script-src': ["'self'", "'unsafe-inline'", 'https://cdn.jsdelivr.net'],
        'style-src': ["'self'", "'unsafe-inline'", 'https://cdn.jsdelivr.net'],
        'img-src': ["'self'", 'data:'],
        'font-src': ["'self'", 'https://cdn.jsdelivr.net'],
    }
    
    # Inicializar Talisman para gerenciar cabeçalhos de segurança
    Talisman(app, 
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src'],
        force_https=False,  # Definir como True em produção
        strict_transport_security=True,
        strict_transport_security_preload=True,
        session_cookie_secure=True,
        session_cookie_http_only=True,
        feature_policy={
            'geolocation': "'none'",
            'microphone': "'none'",
            'camera': "'none'",
            'payment': "'none'",
        }
    )
    
    # Outras configurações de segurança
    app.config['TEMPLATES_AUTO_RELOAD'] = False  # Desativar em produção
    
    # Configurações para proteger contra ataques de força bruta
    app.config['LOGIN_RATE_LIMIT'] = '5 per minute'

def create_dot_env_file():
    """
    Cria um arquivo .env com configurações seguras
    """
    env_path = os.path.join(os.getcwd(), '.env')
    
    # Verifica se o arquivo já existe
    if os.path.exists(env_path):
        print("Arquivo .env já existe. Não será sobrescrito.")
        return
    
    # Gera uma chave secreta
    secret_key = secrets.token_hex(32)
    
    # Conteúdo do arquivo .env
    env_content = f"""# Configurações de Segurança
SECRET_KEY={secret_key}
FLASK_ENV=development
DEBUG=True

# Em produção, defina estas variáveis como:
# FLASK_ENV=production
# DEBUG=False
# SESSION_COOKIE_SECURE=True

# Configurações do banco de dados
DATABASE_URL=sqlite:///disc_assessment.db

# Configurações de email (se implementar recuperação de senha)
# MAIL_SERVER=smtp.example.com
# MAIL_PORT=587
# MAIL_USE_TLS=True
# MAIL_USERNAME=seu_email@example.com
# MAIL_PASSWORD=sua_senha_segura
"""
    
    # Escreve o arquivo
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"Arquivo .env criado com sucesso em: {env_path}")

if __name__ == "__main__":
    create_dot_env_file()