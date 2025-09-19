#!/usr/bin/env python3
"""
test_basic.py

Testes básicos para verificar funcionamento do Tabu Search QBF.
"""

import unittest
import tempfile
import os
from core.solution import Solution
from core.qbf import QBF, QBFInverse
from core.ts_qbf import TabuSearchQBF


class TestSolution(unittest.TestCase):
    """Testes para a classe Solution."""
    
    def test_creation(self):
        """Testa criação de solução."""
        sol = Solution()
        self.assertEqual(len(sol), 0)
        self.assertEqual(sol.cost, float('inf'))
        self.assertTrue(sol.is_empty())
    
    def test_add_remove_elements(self):
        """Testa adição e remoção de elementos."""
        sol = Solution()
        
        # Adiciona elementos
        sol.add_element(1)
        sol.add_element(3)
        sol.add_element(5)
        
        self.assertEqual(len(sol), 3)
        self.assertFalse(sol.is_empty())
        self.assertTrue(sol.contains_element(1))
        self.assertTrue(sol.contains_element(3))
        self.assertTrue(sol.contains_element(5))
        self.assertFalse(sol.contains_element(2))
        
        # Remove elemento
        self.assertTrue(sol.remove_element(3))
        self.assertEqual(len(sol), 2)
        self.assertFalse(sol.contains_element(3))
        
        # Tenta remover elemento que não existe
        self.assertFalse(sol.remove_element(10))
    
    def test_copy(self):
        """Testa cópia de solução."""
        sol1 = Solution()
        sol1.add_element(1)
        sol1.add_element(2)
        sol1.cost = 10.5
        
        sol2 = sol1.copy()
        
        self.assertEqual(len(sol2), 2)
        self.assertEqual(sol2.cost, 10.5)
        self.assertTrue(sol2.contains_element(1))
        self.assertTrue(sol2.contains_element(2))
        
        # Modifica original, cópia não deve mudar
        sol1.add_element(3)
        self.assertEqual(len(sol1), 3)
        self.assertEqual(len(sol2), 2)


class TestQBF(unittest.TestCase):
    """Testes para a classe QBF."""
    
    def create_test_instance(self, size=3):
        """Cria instância de teste temporária."""
        content = f"{size}\n"
        
        # Matriz triangular superior simples
        if size == 3:
            content += "1 2 3\n"  # a00, a01, a02
            content += "4 5\n"    # a11, a12  
            content += "6\n"      # a22
        
        # Cria arquivo temporário
        fd, filepath = tempfile.mkstemp(suffix='.qbf', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)
            return filepath
        except:
            os.close(fd)
            raise
    
    def test_file_reading(self):
        """Testa leitura de arquivo."""
        filepath = self.create_test_instance(3)
        
        try:
            qbf = QBF(filepath)
            
            self.assertEqual(qbf.get_domain_size(), 3)
            self.assertIsNotNone(qbf.A)
            self.assertEqual(len(qbf.A), 3)
            self.assertEqual(len(qbf.A[0]), 3)
            
            # Verifica alguns valores da matriz
            self.assertEqual(qbf.A[0][0], 1.0)
            self.assertEqual(qbf.A[0][1], 2.0)
            self.assertEqual(qbf.A[0][2], 3.0)
            self.assertEqual(qbf.A[1][1], 4.0)
            self.assertEqual(qbf.A[1][2], 5.0)
            self.assertEqual(qbf.A[2][2], 6.0)
            
            # Parte inferior deve ser zero
            self.assertEqual(qbf.A[1][0], 0.0)
            self.assertEqual(qbf.A[2][0], 0.0)
            self.assertEqual(qbf.A[2][1], 0.0)
            
        finally:
            os.unlink(filepath)
    
    def test_evaluation(self):
        """Testa avaliação de soluções."""
        filepath = self.create_test_instance(3)
        
        try:
            qbf = QBF(filepath)
            
            # Solução vazia
            sol_empty = Solution()
            result = qbf.evaluate(sol_empty)
            self.assertEqual(result, 0.0)
            
            # Solução com um elemento
            sol_one = Solution()
            sol_one.add_element(0)
            result = qbf.evaluate(sol_one)
            self.assertEqual(result, 1.0)  # A[0][0] = 1
            
            # Solução com múltiplos elementos
            sol_multi = Solution()
            sol_multi.add_element(0)
            sol_multi.add_element(1)
            result = qbf.evaluate(sol_multi)
            # x = [1,1,0], f(x) = 1*1 + 2*1*1 + 1*4 = 1 + 2 + 4 = 7
            self.assertEqual(result, 7.0)
            
        finally:
            os.unlink(filepath)


class TestTabuSearchQBF(unittest.TestCase):
    """Testes para TabuSearchQBF."""
    
    def create_test_instance(self):
        """Cria instância pequena para teste."""
        content = "5\n"
        content += "2 -1 3 0 1\n"   # Linha 0
        content += "1 0 -1 2\n"     # Linha 1  
        content += "3 1 -1\n"       # Linha 2
        content += "0 2\n"          # Linha 3
        content += "1\n"            # Linha 4
        
        fd, filepath = tempfile.mkstemp(suffix='.qbf', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)
            return filepath
        except:
            os.close(fd)
            raise
    
    def test_solver_creation(self):
        """Testa criação do solver."""
        filepath = self.create_test_instance()
        
        try:
            ts = TabuSearchQBF(tenure=5, iterations=10, filename=filepath, random_seed=42)
            
            self.assertEqual(ts.tenure, 5)
            self.assertEqual(ts.iterations, 10)
            self.assertIsNotNone(ts.qbf)
            self.assertEqual(ts.qbf.get_domain_size(), 5)
            
        finally:
            os.unlink(filepath)
    
    def test_basic_execution(self):
        """Testa execução básica do algoritmo."""
        filepath = self.create_test_instance()
        
        try:
            # Configuração pequena para teste rápido
            ts = TabuSearchQBF(tenure=3, iterations=5, filename=filepath, random_seed=42)
            ts.set_verbose(False)  # Desabilita saídas durante teste
            
            # Executa algoritmo
            best_solution = ts.solve()
            
            # Verifica se retornou uma solução
            self.assertIsNotNone(best_solution)
            self.assertIsInstance(best_solution, Solution)
            
            # Verifica se a solução tem custo definido
            self.assertIsNotNone(best_solution.cost)
            self.assertNotEqual(best_solution.cost, float('inf'))
            
            # Verifica se informações de qualidade estão disponíveis
            quality_info = ts.get_solution_quality_info()
            self.assertIsNotNone(quality_info)
            self.assertEqual(quality_info['domain_size'], 5)
            self.assertEqual(quality_info['iterations'], 5)
            self.assertEqual(quality_info['tenure'], 3)
            
        finally:
            os.unlink(filepath)


def run_tests():
    """Executa todos os testes."""
    # Cria suite de testes
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adiciona classes de teste
    suite.addTests(loader.loadTestsFromTestCase(TestSolution))
    suite.addTests(loader.loadTestsFromTestCase(TestQBF))
    suite.addTests(loader.loadTestsFromTestCase(TestTabuSearchQBF))
    
    # Executa testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=== EXECUTANDO TESTES BÁSICOS ===")
    success = run_tests()
    
    if success:
        print("\n✓ Todos os testes passaram!")
        exit(0)
    else:
        print("\n✗ Alguns testes falharam!")
        exit(1)
