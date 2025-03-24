import sys
import os
import unittest

# Adiciona o diretório principal ao path para importação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.disc_model import calculate_disc_scores

class TestDISCScoring(unittest.TestCase):
    def test_calculate_disc_scores_balanced(self):
        """Testa um caso equilibrado onde todas as pontuações são iguais"""
        responses = {
            'D': {'mais': 6, 'menos': 0},
            'I': {'mais': 6, 'menos': 0},
            'S': {'mais': 6, 'menos': 0},
            'C': {'mais': 6, 'menos': 0}
        }
        
        scores = calculate_disc_scores(responses)
        
        # Verifica se todas as pontuações são iguais
        self.assertEqual(scores['D'], scores['I'])
        self.assertEqual(scores['I'], scores['S'])
        self.assertEqual(scores['S'], scores['C'])
    
    def test_calculate_disc_scores_dominant(self):
        """Testa um caso com predominância clara de Dominância"""
        responses = {
            'D': {'mais': 24, 'menos': 0},
            'I': {'mais': 0, 'menos': 8},
            'S': {'mais': 0, 'menos': 8},
            'C': {'mais': 0, 'menos': 8}
        }
        
        scores = calculate_disc_scores(responses)
        
        # Verifica se D é a pontuação mais alta
        self.assertGreater(scores['D'], scores['I'])
        self.assertGreater(scores['D'], scores['S'])
        self.assertGreater(scores['D'], scores['C'])
    
    def test_calculate_disc_scores_negative(self):
        """Testa um caso com pontuações negativas"""
        responses = {
            'D': {'mais': 0, 'menos': 10},
            'I': {'mais': 12, 'menos': 2},
            'S': {'mais': 6, 'menos': 6},
            'C': {'mais': 6, 'menos': 6}
        }
        
        scores = calculate_disc_scores(responses)
        
        # Verifica se D tem pontuação negativa
        self.assertLess(scores['D'], 0)
        # Verifica se I tem pontuação positiva
        self.assertGreater(scores['I'], 0)
        # Verifica se S e C têm pontuação zero
        self.assertEqual(scores['S'], 0)
        self.assertEqual(scores['C'], 0)

if __name__ == '__main__':
    unittest.main()