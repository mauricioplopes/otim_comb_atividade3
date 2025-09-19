
"""
main.py

Programa principal para executar o Tabu Search no problema QBF.
"""

import sys
import time
import traceback
from typing import Optional

from core.ts_qbf import TabuSearchQBF


def print_usage():
    """Imprime instruções de uso do programa."""
    print("Uso: python main.py <tenure> <iterations> <filename> [options]")
    print()
    print("Parâmetros obrigatórios:")
    print("  tenure      : Tamanho da lista tabu (ex: 20)")
    print("  iterations  : Número de iterações (ex: 1000)")
    print("  filename    : Arquivo da instância QBF")
    print()
    print("Opções:")
    print("  debug       : Ativa modo debug detalhado")
    print("  quiet       : Desativa saídas verbosas")
    print("  seed=N      : Define seed aleatória (ex: seed=42)")
    print()
    print("Exemplos:")
    print("  python main.py 20 1000 instances/qbf200")
    print("  python main.py 20 1000 instances/qbf200 debug")
    print("  python main.py 20 1000 instances/qbf200 quiet seed=123")


def parse_arguments(args):
    """
    Analisa os argumentos da linha de comando.
    
    Args:
        args: Lista de argumentos
        
    Returns:
        dict: Dicionário com argumentos processados
    """
    if len(args) < 4:
        return None
    
    try:
        parsed = {
            'tenure': int(args[1]),
            'iterations': int(args[2]),
            'filename': args[3],
            'debug': False,
            'quiet': False,
            'seed': 0
        }
        
        # Processa opções adicionais
        for arg in args[4:]:
            arg_lower = arg.lower()
            
            if arg_lower == 'debug':
                parsed['debug'] = True
            elif arg_lower == 'quiet':
                parsed['quiet'] = True
            elif arg_lower.startswith('seed='):
                try:
                    parsed['seed'] = int(arg_lower.split('=')[1])
                except (ValueError, IndexError):
                    print(f"AVISO: Seed inválida '{arg}', usando seed=0")
            else:
                print(f"AVISO: Opção desconhecida '{arg}' ignorada")
        
        return parsed
        
    except ValueError as e:
        print(f"Erro nos parâmetros: {e}")
        return None


def validate_parameters(params):
    """
    Valida os parâmetros fornecidos.
    
    Args:
        params (dict): Parâmetros a serem validados
        
    Returns:
        bool: True se válidos, False caso contrário
    """
    errors = []
    
    if params['tenure'] <= 0:
        errors.append("Tenure deve ser maior que zero")
    
    if params['iterations'] <= 0:
        errors.append("Iterations deve ser maior que zero")
    
    if params['tenure'] > 100:
        print(f"AVISO: Tenure muito alto ({params['tenure']}), pode impactar performance")
    
    if params['iterations'] > 10000:
        print(f"AVISO: Muitas iterações ({params['iterations']}), execução pode ser lenta")
    
    if errors:
        print("Erros de validação:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True


def run_tabu_search(params):
    """
    Executa o Tabu Search com os parâmetros fornecidos.
    
    Args:
        params (dict): Parâmetros de execução
        
    Returns:
        dict: Resultados da execução
    """
    if not params['quiet']:
        print("=== TABU SEARCH PARA QBF ===")
        print(f"Arquivo: {params['filename']}")
        print(f"Tenure: {params['tenure']}")
        print(f"Iterations: {params['iterations']}")
        print(f"Seed: {params['seed']}")
        if params['debug']:
            print("Modo DEBUG ativado")
        print()
    
    # Cria instância do Tabu Search
    try:
        ts = TabuSearchQBF(
            tenure=params['tenure'],
            iterations=params['iterations'],
            filename=params['filename'],
            random_seed=params['seed']
        )
        
        # Configura verbosidade
        ts.set_verbose(not params['quiet'])
        
        if params['debug'] and not params['quiet']:
            print("Instância carregada com sucesso!")
            ts.print_debug_info()
            print("Iniciando Tabu Search...\n")
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Erro ao carregar instância: {e}",
            'traceback': traceback.format_exc() if params['debug'] else None
        }
    
    # Executa o algoritmo
    try:
        start_time = time.time()
        
        # Aumenta limite de recursão se necessário
        import sys
        original_limit = sys.getrecursionlimit()
        if original_limit < 5000:
            sys.setrecursionlimit(5000)
        
        try:
            best_solution = ts.solve()
        finally:
            # Restaura limite original
            sys.setrecursionlimit(original_limit)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Coleta informações dos resultados
        quality_info = ts.get_solution_quality_info()
        
        return {
            'success': True,
            'best_solution': best_solution,
            'execution_time': execution_time,
            'quality_info': quality_info,
            'tabu_search': ts
        }
        
    except RecursionError as e:
        return {
            'success': False,
            'error': f"Erro de recursão: {e}. Tente reduzir o número de iterações ou o tamanho da instância.",
            'traceback': traceback.format_exc() if params['debug'] else None
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Erro durante execução: {e}",
            'traceback': traceback.format_exc() if params['debug'] else None
        }


def print_results(results, params):
    """
    Imprime os resultados da execução.
    
    Args:
        results (dict): Resultados da execução
        params (dict): Parâmetros de execução
    """
    if not results['success']:
        print(f"ERRO: {results['error']}")
        if results.get('traceback') and params['debug']:
            print("\nTraceback:")
            print(results['traceback'])
        return
    
    # Resultados principais
    best_sol = results['best_solution']
    exec_time = results['execution_time']
    quality = results['quality_info']
    
    if not params['quiet']:
        print("\n" + "="*50)
        print("RESULTADOS FINAIS")
        print("="*50)
        
        print(f"Melhor solução encontrada:")
        print(f"  Custo (invertido): {best_sol.cost:.6f}")
        print(f"  Valor real QBF: {quality['best_real_value']:.6f}")
        print(f"  Variáveis selecionadas: {len(best_sol)}")
        print(f"  Elementos: {best_sol.get_elements()}")
        
        print(f"\nInformações de execução:")
        print(f"  Tempo: {exec_time:.3f} segundos")
        print(f"  Iterações: {quality['iterations']}")
        print(f"  Tamanho do domínio: {quality['domain_size']}")
        print(f"  Taxa de ocupação: {len(best_sol)/quality['domain_size']*100:.1f}%")
        
        if params['debug']:
            print(f"\nInformações detalhadas:")
            ts = results['tabu_search']
            ts.print_debug_info()
    
    else:
        # Modo quiet - apenas resultado essencial
        print(f"maxVal = {best_sol}")
        print(f"Time = {exec_time:.3f} seg")


def main():
    """Função principal do programa."""
    # Analisa argumentos
    params = parse_arguments(sys.argv)
    
    if params is None:
        print_usage()
        sys.exit(1)
    
    # Valida parâmetros
    if not validate_parameters(params):
        sys.exit(1)
    
    # Executa Tabu Search
    results = run_tabu_search(params)
    
    # Imprime resultados
    print_results(results, params)
    
    # Código de saída
    sys.exit(0 if results['success'] else 1)


if __name__ == "__main__":
    main()
