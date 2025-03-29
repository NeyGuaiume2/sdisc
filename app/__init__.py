# Pacote principal da aplicação

# Reexporta a função create_app do backend
__all__ = ['create_app']
from backend.app import create_app  # Importe da localização correta
__all__ = ['create_app']