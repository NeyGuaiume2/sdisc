import sys
import os
import unittest
from flask import Flask

# Adiciona o diretório principal ao path para importação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models.database import init_db, db

class TestAppBasic(unittest.TestCase):
    def setUp(self):
        """Configura o ambiente de teste antes de cada teste"""
        self.app = create_app(test_config={
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            init_db()
    
    def tearDown(self):
        """Limpa depois de cada teste"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_home_page(self):
        """Testa se a página inicial carrega corretamente"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_quiz_page(self):
        """Testa se a página do questionário carrega corretamente"""
        response = self.client.get('/quiz')
        self.assertEqual(response.status_code, 200)
    
    def test_non_existent_page(self):
        """Testa se uma página não existente retorna 404"""
        response = self.client.get('/page_that_does_not_exist')
        self.assertEqual(response.status_code, 404)

class TestDISCQuiz(unittest.TestCase):
    def setUp(self):
        """Configura o ambiente de teste antes de cada teste"""
        self.app = create_app(test_config={
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            init_db()
    
    def tearDown(self):
        """Limpa depois de cada teste"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_submit_quiz_results(self):
        """Testa a submissão de resultados do questionário"""
        # Cria dados simulados para o questionário
        test_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'responses': {
                'q1_mais': 'D', 'q1_menos': 'S',
                'q2_mais': 'I', 'q2_menos': 'C',
                # Adicione mais respostas conforme necessário
            }
        }
        
        response = self.client.post('/api/submit_quiz', 
                                   json=test_data,
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        # Verifica se o resultado contém um ID de resultado válido
        self.assertIn('result_id', response.get_json())

if __name__ == '__main__':
    unittest.main()