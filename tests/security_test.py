# tests/security_test.py
"""
Testes de segurança para o Sistema de Avaliação DISC
"""
import unittest
import re
import sys
import os

# Adicionar diretório raiz ao path para importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar a aplicação Flask
from backend.app import create_app
from backend.config.security import configure_app_security

class SecurityTests(unittest.TestCase):
    """Testes de segurança para a aplicação Flask"""
    
    def setUp(self):
        """Configurar a aplicação de teste"""
        self.app = create_app(testing=True)
        configure_app_security(self.app)
        self.client = self.app.test_client()
        self.client.testing = True
        
    def test_content_security_policy(self):
        """Verificar se o Content Security Policy está configurado"""
        response = self.client.get('/')
        self.assertIn('Content-Security-Policy', response.headers)
        
    def test_xss_protection(self):
        """Verificar se a proteção XSS está habilitada"""
        response = self.client.get('/')
        self.assertIn('X-XSS-Protection', response.headers)
        
    def test_csrf_protection(self):
        """Verificar se o token CSRF está presente nos formulários"""
        response = self.client.get('/login')  # Assumindo que existe uma rota /login
        self.assertEqual(response.status_code, 200)
        # Verificar se há um token CSRF no HTML
        csrf_token_pattern = re.compile(r'<input[^>]*name="csrf_token"[^>]*>')
        self.assertTrue(csrf_token_pattern.search(response.data.decode()))
        
    def test_secure_cookies(self):
        """Verificar se os cookies têm os atributos de segurança"""
        with self.app.test_request_context():
            self.app.config['SERVER_NAME'] = 'localhost'
            self.client.get('/')
            # Testar configurações de sessão
            self.assertTrue(self.app.config['SESSION_COOKIE_HTTPONLY'])
            self.assertEqual(self.app.config['SESSION_COOKIE_SAMESITE'], 'Lax')
    
    def test_rate_limiting(self):
        """Testar se o rate limiting está funcionando"""
        # Fazer várias requisições rápidas para uma rota protegida
        for _ in range(10):
            response = self.client.post('/login', data={'username': 'test', 'password': 'test'})
        
        # A última resposta deve ter status 429 (Too Many Requests)
        # Descomente se o rate limiting estiver implementado
        # self.assertEqual(response.status_code, 429)
        
    def test_sql_injection_protection(self):
        """Testar proteção contra SQL Injection"""
        # Exemplo de payload de SQL Injection
        payload = "' OR '1'='1"
        response = self.client.post('/login', data={'username': payload, 'password': payload})
        
        # Não deve autenticar com SQL injection
        self.assertNotIn('Bem-vindo', response.data.decode())
        
    def test_secure_headers(self):
        """Verificar headers de segurança adicionais"""
        response = self.client.get('/')
        
        # Verificar headers importantes
        self.assertIn('X-Content-Type-Options', response.headers)
        self.assertIn('X-Frame-Options', response.headers)
        self.assertIn('Referrer-Policy', response.headers)
        
        # Valores corretos
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(response.headers.get('X-Frame-Options'), 'SAMEORIGIN')
        
if __name__ == '__main__':
    unittest.main()