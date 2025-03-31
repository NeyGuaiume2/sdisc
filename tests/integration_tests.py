"""
Testes de integração para o sistema DISC.
Verifica se todos os componentes estão funcionando corretamente juntos.
"""
import os
import sys
import unittest
import json
import tempfile
import random
from datetime import datetime

# Adicionar diretório raiz ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import app, db
from backend.models.disc import DISC
from backend.models.disc_result import DISCResult
from backend.score_calculator import calculate_disc_score


class IntegrationTestCase(unittest.TestCase):
    """Testes de integração para o sistema DISC."""

    def setUp(self):
        """Configurar ambiente de teste."""
        # Configurar app para teste
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        # Criar banco de dados temporário
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.config['DATABASE']}"
        
        # Criar tabelas
        with app.app_context():
            db.create_all()
        
        # Criar cliente de teste
        self.client = app.test_client()

    def tearDown(self):
        """Limpar após teste."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_homepage(self):
        """Testar se a página inicial carrega."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'DISC', response.data)

    def test_quiz_page(self):
        """Testar se a página do questionário carrega."""
        response = self.client.get('/quiz')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'question', response.data.lower())

    def test_full_assessment_flow(self):
        """Testar o fluxo completo de avaliação."""
        # Gerar dados de teste para o questionário
        test_responses = []
        
        # Gerar 24 conjuntos de respostas (1 MAIS e 1 MENOS para cada conjunto de 4 opções)
        for _ in range(24):
            options = ['A', 'B', 'C', 'D']
            most = random.choice(options)
            options.remove(most)
            least = random.choice(options)
            test_responses.append({
                'most': most,
                'least': least
            })
        
        # Enviar respostas
        response = self.client.post(
            '/api/submit_assessment',
            data=json.dumps({
                'name': 'Teste Integração',
                'email': 'teste@exemplo.com',
                'responses': test_responses
            }),
            content_type='application/json'
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('result_id', result)
        
        # Verificar se o resultado foi salvo no banco de dados
        with app.app_context():
            saved_result = DISCResult.query.get(result['result_id'])
            self.assertIsNotNone(saved_result)
            self.assertEqual(saved_result.name, 'Teste Integração')
            
        # Testar página de resultados
        response = self.client.get(f"/results/{result['result_id']}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'DISC', response.data)
        self.assertIn(b'profile', response.data.lower())

    def test_score_calculator(self):
        """Testar o cálculo de pontuação DISC."""
        # Criar dados de teste com distribuição conhecida
        test_responses = []
        
        # Simular perfil com alta dominância
        for _ in range(6):
            test_responses.append({'most': 'A', 'least': 'C'})
        
        # Simular perfil com influência média
        for _ in range(6):
            test_responses.append({'most': 'B', 'least': 'D'})
        
        # Simular perfil com estabilidade e conformidade baixas
        for _ in range(12):
            test_responses.append({'most': 'A', 'least': 'D'})
        
        # Calcular pontuação
        score = calculate_disc_score(test_responses)
        
        # Verificar resultados conforme esperado
        self.assertGreater(score['D'], score['I'])  # Dominância maior que Influência
        self.assertGreater(score['I'], score['S'])  # Influência maior que Estabilidade
        self.assertGreater(score['I'], score['C'])  # Influência maior que Conformidade
        self.assertLessEqual(score['S'], 0)         # Estabilidade deve ser negativa ou zero
        self.assertLessEqual(score['C'], 0)         # Conformidade deve ser negativa ou zero

    def test_security_headers(self):
        """Verificar se os cabeçalhos de segurança estão configurados."""
        response = self.client.get('/')
        headers = response.headers
        
        # Verificar cabeçalhos de segurança essenciais
        self.assertIn('Content-Security-Policy', headers)
        self.assertIn('X-Content-Type-Options', headers)
        self.assertIn('X-Frame-Options', headers)


if __name__ == '__main__':
    unittest.main()
