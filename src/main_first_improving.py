#!/usr/bin/env python3
"""
main_first_improving.py

Script principal para executar o Tabu Search First-Improving no problema MAX-SC-QBF.
Implementação do item 1: PADRÃO - Busca Tabu com método de busca first-improving.
"""

import sys
import time
from core.ts_qbf_sc_first_improving import TabuSearchQBFScFirstImproving


def main():
    """Função principal"""
    if len(sys.argv) < 4:
        print("Uso: python main_first_improving.py <tenure> <iterations> <filename> [seed]")
        print()
        print("Parâmetros:")
        print("  tenure     : Tamanho da lista tabu (T1)")
        print("  iterations : Número de iterações")
        print("  filename   : Arquivo da instância MAX-SC-QBF")
        print("  seed       : Seed aleatória (opcional, padrão=0)")
        print()
        print("Exemplo:")
        print("  python main_first_improving.py 20 1000 instances/qbf_sc/instance01.txt")
        return
    
    try:
        # Parse dos argumentos
        tenure = int(sys.argv[1])
        iterations = int(sys.argv[2])
        filename = sys.argv[3]
        seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        
        print("=" * 60)
        print("TABU SEARCH - MAX-SC-QBF (FIRST-IMPROVING)")
        print("=" * 60)
        print(f"Instância: {filename}")
        print(f"Tenure (T1): {tenure}")
        print(f"Iterações: {iterations}")
        print(f"Seed: {seed}")
        print("Estratégia: First-Improving (PADRÃO)")
        print("-" * 60)
        
        # Cria e configura o solver
        solver = TabuSearchQBFScFirstImproving(tenure, iterations, filename, seed)
        solver.set_verbose(True)
        
        # Executa o algoritmo
        start_time = time.time()
        best_solution = solver.solve()
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Resultados
        print("-" * 60)
        print("RESULTADOS:")
        print(f"Melhor solução encontrada: {best_solution}")
        print(f"Custo da melhor solução: {best_solution.cost:.6f}")
        print(f"Valor objetivo (MAX): {-best_solution.cost:.6f}")  # QBF inversa
        print(f"Tempo de execução: {execution_time:.2f} segundos")
        print(f"Elementos na solução: {len(best_solution)}")
        
        # Estatísticas adicionais
        print("-" * 60)
        print("ESTATÍSTICAS:")
        print(f"Elementos na solução final: {sorted(list(best_solution))}")
        print("=" * 60)
        
    except ValueError as e:
        print(f"Erro nos parâmetros: {e}")
        print("Use números inteiros para tenure, iterations e seed")
    except FileNotFoundError:
        print(f"Erro: Arquivo '{sys.argv[3]}' não encontrado")
    except Exception as e:
        print(f"Erro durante execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()