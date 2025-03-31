import unittest
import os
import sys

# --- Adicionar diretório raiz ao sys.path ---
# Isso permite importar 'backend' como um módulo de nível superior
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
# ------------------------------------------

# --- Importar DEPOIS de ajustar o path ---
from backend.app import create_app # CORRIGIDO: Importar de 'backend.app'
# ------------------------------------------

class TestApp(unittest.TestCase):

    def setUp(self):
        """Configura o ambiente de teste antes de cada teste."""
        # Usar a factory para criar a app em modo de teste
        # testing=True geralmente configura um banco de dados em memória, etc.
        self.app = create_app(testing=True)
        self.app_context = self.app.app_context()
        self.app_context.push() # Ativa o contexto da aplicação
        self.client = self.app.test_client() # Cria um cliente de teste

    def tearDown(self):
        """Limpa o ambiente após cada teste."""
        self.app_context.pop() # Remove o contexto da aplicação

    def test_index_route(self):
        """Testa se a rota principal '/' retorna status 200."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Você pode adicionar mais verificações, como checar conteúdo HTML
        self.assertIn(b'Avalia', response.data) # Verifica se parte do título/texto está presente

    def test_quiz_route(self):
        """Testa se a rota '/quiz' retorna status 200."""
        response = self.client.get('/quiz')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Question', response.data) # Verifica se a palavra 'Question' está presente

    def test_404_error(self):
        """Testa se uma rota inexistente retorna 404."""
        response = self.client.get('/rota-que-nao-existe')
        self.assertEqual(response.status_code, 404)
        # Verifica se a mensagem padrão de 404 (ou a do seu template) está presente
        self.assertIn(b'Not Found', response.data)

    # Adicione mais testes conforme necessário para outras rotas ou funcionalidades do app.py

if __name__ == '__main__':
    unittest.main()