import unittest
import os
import sys

# --- Adicionar diretório raiz ao sys.path ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
# ------------------------------------------

# --- Importar DEPOIS de ajustar o path ---
# CORRIGIDO: Importar a função correta do local correto
from backend.score_calculator import calculate_disc_scores, get_profile_summary, generate_detailed_report
# ------------------------------------------

class TestDiscScoring(unittest.TestCase):

    def test_calculate_disc_scores_balanced(self):
        """Testa o cálculo com respostas balanceadas (espera scores próximos de zero)."""
        responses = {}
        # Simular respostas onde cada letra é escolhida igualmente como MAIS e MENOS
        # Exemplo muito simplificado:
        for i in range(1, 7): responses[str(i)] = {'mais': 'A', 'menos': 'B'}
        for i in range(7, 13): responses[str(i)] = {'mais': 'B', 'menos': 'A'}
        for i in range(13, 19): responses[str(i)] = {'mais': 'C', 'menos': 'D'}
        for i in range(19, 25): responses[str(i)] = {'mais': 'D', 'menos': 'C'}

        result = calculate_disc_scores(responses)

        # Em um cenário perfeitamente balanceado, os scores DISC devem ser 0
        self.assertEqual(result['disc_scores']['D'], 0)
        self.assertEqual(result['disc_scores']['I'], 0)
        self.assertEqual(result['disc_scores']['S'], 0)
        self.assertEqual(result['disc_scores']['C'], 0)
        self.assertEqual(result['disc_levels']['D'], "Médio") # Score 0 é Médio
        self.assertEqual(result['disc_levels']['I'], "Médio")
        self.assertEqual(result['disc_levels']['S'], "Médio")
        self.assertEqual(result['disc_levels']['C'], "Médio")
        # O tipo primário pode variar se houver empate em 0, mas podemos testar se é um dos 4
        self.assertIn(result['primary_type'], ['D', 'I', 'S', 'C'])

    def test_calculate_disc_scores_high_d(self):
        """Testa o cálculo com alta Dominância (D)."""
        responses = {}
        # Muitas respostas 'A' como MAIS, poucas como MENOS
        for i in range(1, 13): responses[str(i)] = {'mais': 'A', 'menos': 'C'} # A+ vs C-
        for i in range(13, 25): responses[str(i)] = {'mais': 'B', 'menos': 'D'} # B+ vs D-

        result = calculate_disc_scores(responses)

        # Espera-se score D alto, I e S baixos/negativos, C baixo/negativo
        self.assertGreater(result['disc_scores']['D'], 5) # Espera D bem alto
        self.assertLess(result['disc_scores']['S'], 0)    # Espera S negativo
        self.assertLess(result['disc_scores']['C'], 0)    # Espera C negativo
        self.assertEqual(result['primary_type'], 'D')
        self.assertEqual(result['disc_levels']['D'], "Alto")
        self.assertEqual(result['disc_levels']['S'], "Baixo")
        self.assertEqual(result['disc_levels']['C'], "Baixo")

    def test_calculate_disc_scores_high_s(self):
        """Testa o cálculo com alta Estabilidade (S)."""
        responses = {}
        # Muitas respostas 'C' como MAIS, poucas como MENOS
        for i in range(1, 13): responses[str(i)] = {'mais': 'C', 'menos': 'A'} # C+ vs A-
        for i in range(13, 25): responses[str(i)] = {'mais': 'D', 'menos': 'B'} # D+ vs B-

        result = calculate_disc_scores(responses)

        self.assertGreater(result['disc_scores']['S'], 5) # Espera S alto
        self.assertLess(result['disc_scores']['D'], 0)    # Espera D negativo
        self.assertLess(result['disc_scores']['I'], 0)    # Espera I negativo
        self.assertEqual(result['primary_type'], 'S')
        self.assertEqual(result['disc_levels']['S'], "Alto")
        self.assertEqual(result['disc_levels']['D'], "Baixo")
        self.assertEqual(result['disc_levels']['I'], "Baixo")

    def test_get_profile_summary(self):
        """Testa a geração do resumo do perfil."""
        # Usar resultado do teste high_d como exemplo
        responses_high_d = {}
        for i in range(1, 13): responses_high_d[str(i)] = {'mais': 'A', 'menos': 'C'}
        for i in range(13, 25): responses_high_d[str(i)] = {'mais': 'B', 'menos': 'D'}
        result_high_d = calculate_disc_scores(responses_high_d)

        summary = get_profile_summary(result_high_d)
        self.assertIsInstance(summary, str)
        # CORRIGIDO: A string exata gerada pela função usa "Dominância" (substantivo)
        self.assertIn("predominantemente Dominância", summary)
        self.assertIn("(D)", summary)
        self.assertIn("como secundário", summary)
        self.assertIn(f"({result_high_d['secondary_type']})", summary) # Verifica tipo secundário
        self.assertIn("D (Dominância): Alto", summary) # Verifica nível D
        self.assertIn("S (Estabilidade): Baixo", summary) # Verifica nível S

    def test_generate_detailed_report(self):
        """Testa a geração do relatório detalhado."""
        # Usar resultado do teste high_s como exemplo
        responses_high_s = {}
        for i in range(1, 13): responses_high_s[str(i)] = {'mais': 'C', 'menos': 'A'}
        for i in range(13, 25): responses_high_s[str(i)] = {'mais': 'D', 'menos': 'B'}
        result_high_s = calculate_disc_scores(responses_high_s)

        report = generate_detailed_report(result_high_s)
        self.assertIsInstance(report, dict)
        self.assertIn('summary', report)
        self.assertIn('primary_strengths', report)
        self.assertIsInstance(report['primary_strengths'], list) # Espera lista de forças
        self.assertIn('primary_weaknesses', report)
        self.assertIn('development_areas_list', report)
        self.assertIsInstance(report['development_areas_list'], list)
        # Verifica se a área de desenvolvimento para S está presente
        self.assertTrue(any("Ser mais assertivo" in area for area in report['development_areas_list']))

    # Adicione mais casos de teste para cobrir outros perfis (I, C) e cenários de borda.

if __name__ == '__main__':
    unittest.main()