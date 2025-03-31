# prod_config.py - Configurações NÃO SENSÍVEIS para produção

# Desativa o modo de depuração - ESSENCIAL para produção
DEBUG = False

# Desativa o modo de teste - Garante que flags de teste estejam desligadas
TESTING = False

# Exemplo: Configuração de Logging Específica para Produção (opcional)
# import logging
# LOGGING_LEVEL = logging.INFO
# LOGGING_FILE = '/var/log/sdisc/sdisc_app.log' # Exemplo de caminho em Linux

# Exemplo: Porta padrão para produção (pode ser sobrescrita por Gunicorn/variável PORT)
# PORT = 8000

# NÃO COLOQUE AQUI:
# - SECRET_KEY (Virá da variável de ambiente FLASK_SECRET_KEY)
# - DATABASE_URL (Idealmente virá da variável de ambiente DATABASE_URL)
# - ALLOWED_HOSTS (Configurado no servidor WSGI/Reverse Proxy)
# - Senhas de APIs externas, etc. (Use variáveis de ambiente)

print("INFO: prod_config.py carregado.") # Linha opcional para confirmar carregamento