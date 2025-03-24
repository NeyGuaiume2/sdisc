"""
Módulo de segurança para o sistema de avaliação DISC.
Fornece funções para proteção contra ataques comuns e
configuração segura da aplicação Flask.
"""

import secrets
from flask import Flask, request, abort
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix

def configure_security(app: Flask) -> None:
    """
    Configura medidas de segurança para a aplicação Flask.
    
    Args:
        app: A instância da aplicação Flask
    """
    # Geração de chave secreta segura
    if app.config.get('SECRET_KEY') == 'development-key':
        app.config['SECRET_KEY'] = secrets.token_hex(32)
    
    # Configuração de cabeçalhos de segurança com Talisman
    csp = {
        'default-src': "'self'",
        'style-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
        'script-src': ["'self'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com"],
        'img-src': ["'self'", "data:"],
        'font-src': ["'self'", "https://cdn.jsdelivr.net"]
    }
    
    Talisman(
        app,
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src'],
        force_https=app.config.get('FORCE_HTTPS', True),
        strict_transport_security=True,
        strict_transport_security_preload=True,
        session_cookie_secure=app.config.get('SESSION_COOKIE_SECURE', True),
        session_cookie_http_only=True,
        feature_policy={
            'geolocation': "'none'",
            'microphone': "'none'",
            'camera': "'none'"
        }
    )
    
    # Adiciona suporte para proxy reverso
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Adiciona proteção contra falsificação de solicitação entre sites (CSRF)
    @app.before_request
    def csrf_protect():
        if request.method == "POST" and request.path != "/api/submit_quiz":
            token = request.headers.get('X-CSRF-Token')
            if not token or token != app.config.get('CSRF_TOKEN'):
                abort(403)

def generate_csrf_token() -> str:
    """
    Gera um token CSRF seguro.
    
    Returns:
        Um token hexadecimal seguro.
    """
    return secrets.token_hex(32)

def sanitize_input(input_string: str) -> str:
    """
    Sanitiza a entrada do usuário para prevenir injeção de HTML/scripts.
    
    Args:
        input_string: A string para sanitizar
        
    Returns:
        A string sanitizada
    """
    # Implementação básica - em produção, use uma biblioteca dedicada como bleach
    import html
    return html.escape(input_string)