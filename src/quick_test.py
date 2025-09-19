"""
quick_test.py

Teste rápido para verificar se o erro de recursão foi corrigido.
"""

import tempfile
import os
from core.solution import Solution

def test_solution_string_methods():
    """Testa se os métodos __str__ e __repr__ funcionam sem recursão."""
    print("=== TESTE DOS MÉTODOS DE STRING ===")
    
    try:
        # Testa solução vazia
        sol = Solution()
        print(f"Solução vazia: {sol}")
        
        # Testa solução com elementos
        sol.add_element(1)
        sol.add_element(3)
        sol.add_element(5)
        sol.cost = -10.5
        
        print(f"Solução com elementos: {sol}")
        print(f"Repr: {repr(sol)}")
        
        return True
        
    except Exception as e:
        print(f"Erro nos métodos de string: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_small_test_instance():
    """Cria uma instância pequena para teste."""
    content = """5
1 -2 3 0 1
2 0 -1 3
-1 1 0
3 -1
0"""
    
    fd, filepath = tempfile.mkstemp(suffix='.qbf', text=True)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        return filepath
    except:
        os.close(fd)
        raise

def test_qbf_loading():
    """Testa apenas carregamento da QBF."""
    print("\n=== TESTE DE CARREGAMENTO QBF ===")
    
    filepath = create_small_test_instance()
    
    try:
        from core.qbf import QBF
        
        qbf = QBF(filepath)
        print(f"QBF carregada: {qbf.get_domain_size()} variáveis")
        
        # Testa solução simples
        sol = Solution()
        sol.add_element(0)
        result = qbf.evaluate(sol)
        print(f"Avaliação simples: {result}")
        
        return True
        
    except Exception as e:
        print(f"Erro no carregamento QBF: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        os.unlink(filepath)

def test_basic_execution():
    """Testa execução básica sem verbose."""
    print("\n=== TESTE DE EXECUÇÃO BÁSICA ===")
    
    filepath = create_small_test_instance()
    
    try:
        from core.ts_qbf import TabuSearchQBF
        
        # Configuração muito pequena
        ts = TabuSearchQBF(tenure=2, iterations=3, filename=filepath, random_seed=42)
        ts.set_verbose(False)  # SEM verbose para evitar prints problemáticos
        
        print("Executando Tabu Search...")
        
        best_solution = ts.solve()
        
        print(f"Execução OK! Melhor custo: {best_solution.cost}")
        print(f"Elementos: {list(best_solution)}")  # Usa list() para evitar __str__
        
        return True
        
    except Exception as e:
        print(f"Erro na execução básica: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        os.unlink(filepath)

def main():
    print("TESTE RÁPIDO - Verificação de Correções")
    print("="*50)
    
    # Testa primeiro os métodos de string
    success1 = test_solution_string_methods()
    
    if not success1:
        print("\nErro básico nos métodos de string - parando aqui")
        return False
    
    # Testa carregamento QBF
    success2 = test_qbf_loading()
    
    # Testa execução básica
    success3 = test_basic_execution()
    
    if success1 and success2 and success3:
        print("\nTodos os testes passaram!")
        print("O erro de recursão foi corrigido.")
        return True
    else:
        print("\nAlguns testes falharam!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
