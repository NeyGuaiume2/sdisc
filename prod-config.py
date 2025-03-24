"""
Configurações para o ambiente de produção.
Este arquivo deve ser mantido seguro e nunca commitado ao repositório.
"""
import os
import secrets

# Gerar uma chave secreta segura para produção
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(16))

# Configurações de ambiente
DEBUG = False
TESTING = False

# Hosts permitidos - atualize com seu domínio real
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'seudominio.com']

# Configuração do banco de dados - por padrão, usa SQLite
# Para produção real, considere usar PostgreSQL ou MySQL
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///app.db')

# Configurações de sessão segura
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_SECURE = True
REMEMBER_COOKIE_HTTPONLY = True

# Configurações de CORS para API
CORS_ORIGINS = ['https://seudominio.com']

# Tempo limite de sessão (30 minutos)
PERMANENT_SESSION_LIFETIME = 1800

# Configurações de logs
LOG_LEVEL = 'ERROR'
LOG_FILE = 'logs/app.log'

# Tempo de expiração do token (em segundos)
TOKEN_EXPIRES = 3600

# Limite de tentativas de login
LOGIN_ATTEMPTS_LIMIT = 5
LOGIN_COOLDOWN_MINUTES = 15
