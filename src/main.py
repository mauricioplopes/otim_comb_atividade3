#!/usr/bin/env python3
"""
main.py

Programa principal para executar o Tabu Search no problema MAX-SC-QBF.
Suporta diferentes métodos de busca: best-improving (padrão) e first-improving.
"""

import sys
import time
import traceback
from typing import Optional

from core.ts_qbf_sc import TabuSearchQBFSc
from core.ts_qbf_sc_first_improving import TabuSearchQBFScFirstImproving
from core.ts_qbf_sc_probabilistic import TabuSearchQBFScProbabilistic
from core.ts_qbf_sc_intensification import TabuSearchQBFScIntensification


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
    print("  method=X    : Método de busca")
    print("                best-improving | first-improving | probabilistic | intensification")
    print("                Padrão: best-improving")
    print("  alpha=X     : Parâmetro alpha para Probabilistic TS (padrão: 2.0)")
    print("  elite=X     : Tamanho da elite list para Intensification (padrão: 5)")
    print("  period=X    : Período de intensificação (padrão: 50)")
    print("  debug       : Ativa modo debug detalhado")
    print("  quiet       : Desativa saídas verbosas")
    print("  seed=N      : Define seed aleatória (ex: seed=42)")
    print()
    print("Métodos disponíveis:")
    print("  best-improving  : Explora toda vizinhança, escolhe melhor movimento")
    print("  first-improving : Para no primeiro movimento que melhora a solução")
    print("  probabilistic   : First-improving + aceitação probabilística de movimentos tabu")
    print("  intensification : First-improving + intensificação em regiões promissoras")
    print()
    print("Configurações da Atividade 3:")
    print("  1. PADRÃO:        method=first-improving")
    print("  2. PADRÃO+BEST:   method=best-improving")
    print("  3. PADRÃO+TENURE: method=first-improving (com tenure diferente)")
    print("  4. PADRÃO+METHOD1: method=probabilistic")
    print("  5. PADRÃO+METHOD2: method=intensification")
    print()
    print("Exemplos:")
    print("  python main.py 20 1000 instances/qbf200")
    print("  python main.py 20 1000 instances/qbf200 method=first-improving")
    print("  python main.py 20 1000 instances/qbf200 method=probabilistic alpha=1.5")
    print("  python main.py 20 1000 instances/qbf200 method=intensification elite=8 period=30")
    print("  python main.py 50 1000 instances/qbf200 method=first-improving  # tenure diferente")


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
            'method': 'best-improving',  # Padrão
            'alpha': 2.0,  # Parâmetro para Probabilistic TS
            'elite_size': 5,  # Parâmetro para Intensification
            'intensification_period': 50,  # Parâmetro para Intensification
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
            elif arg_lower.startswith('method='):
                try:
                    method = arg_lower.split('=')[1]
                    if method in ['best-improving', 'first-improving', 'probabilistic', 'intensification']:
                        parsed['method'] = method
                    else:
                        print(f"AVISO: Método inválido '{method}', usando best-improving")
                        print("Métodos válidos: best-improving, first-improving, probabilistic, intensification")
                except (ValueError, IndexError):
                    print(f"AVISO: Formato de método inválido '{arg}', usando best-improving")
            elif arg_lower.startswith('alpha='):
                try:
                    parsed['alpha'] = float(arg_lower.split('=')[1])
                    if parsed['alpha'] <= 0:
                        print(f"AVISO: Alpha deve ser positivo, usando 2.0")
                        parsed['alpha'] = 2.0
                except (ValueError, IndexError):
                    print(f"AVISO: Valor alpha inválido '{arg}', usando 2.0")
            elif arg_lower.startswith('elite='):
                try:
                    parsed['elite_size'] = int(arg_lower.split('=')[1])
                    if parsed['elite_size'] <= 0:
                        print(f"AVISO: Elite size deve ser positivo, usando 5")
                        parsed['elite_size'] = 5
                except (ValueError, IndexError):
                    print(f"AVISO: Valor elite inválido '{arg}', usando 5")
            elif arg_lower.startswith('period='):
                try:
                    parsed['intensification_period'] = int(arg_lower.split('=')[1])
                    if parsed['intensification_period'] <= 0:
                        print(f"AVISO: Período deve ser positivo, usando 50")
                        parsed['intensification_period'] = 50
                except (ValueError, IndexError):
                    print(f"AVISO: Valor period inválido '{arg}', usando 50")(f"AVISO: Valor alpha inválido '{arg}', usando 2.0")
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
        params (dict): Dicionário de parâmetros
        
    Returns:
        bool: True se parâmetros são válidos
    """
    if params['tenure'] <= 0:
        print("ERRO: Tenure deve ser positivo")
        return False
    
    if params['iterations'] <= 0:
        print("ERRO: Número de iterações deve ser positivo")
        return False
    
    if params['tenure'] > 1000:
        print("AVISO: Tenure muito alto pode afetar performance")
    
    if params['iterations'] > 100000:
        print("AVISO: Número de iterações muito alto pode demorar muito")
    
    return True


def create_tabu_search(params):
    """
    Cria a instância apropriada do Tabu Search baseada no método escolhido.
    
    Args:
        params (dict): Parâmetros de configuração
        
    Returns:
        TabuSearchQBFSc: Instância do solver apropriado
    """
    if params['method'] == 'first-improving':
        return TabuSearchQBFScFirstImproving(
            params['tenure'], 
            params['iterations'], 
            params['filename'], 
            params['seed']
        )
    elif params['method'] == 'probabilistic':
        return TabuSearchQBFScProbabilistic(
            params['tenure'], 
            params['iterations'], 
            params['filename'], 
            params['seed'],
            params['alpha']
        )
    elif params['method'] == 'intensification':
        return TabuSearchQBFScIntensification(
            params['tenure'], 
            params['iterations'], 
            params['filename'], 
            params['seed'],
            params['elite_size'],
            params['intensification_period']
        )
    else:  # best-improving (padrão)
        return TabuSearchQBFSc(
            params['tenure'], 
            params['iterations'], 
            params['filename'], 
            params['seed']
        )


def run_tabu_search(params):
    """
    Executa o Tabu Search com os parâmetros fornecidos.
    
    Args:
        params (dict): Parâmetros de configuração
        
    Returns:
        dict: Resultados da execução
    """
    try:
        # Cria solver apropriado
        ts = create_tabu_search(params)
        
        # Configura verbosidade
        ts.set_verbose(not params['quiet'])
        
        if not params['quiet']:
            print("="*60)
            print("TABU SEARCH - MAX-SC-QBF")
            print("="*60)
            print(f"Instância: {params['filename']}")
            print(f"Tenure: {params['tenure']}")
            print(f"Iterações: {params['iterations']}")
            print(f"Método: {params['method'].upper()}")
            print(f"Seed: {params['seed']}")
            if params['method'] == 'probabilistic':
                print(f"Alpha (Probabilistic): {params['alpha']}")
            elif params['method'] == 'intensification':
                print(f"Elite Size (Intensification): {params['elite_size']}")
                print(f"Período (Intensification): {params['intensification_period']}")
            print("-"*60)
        
        # Executa algoritmo
        start_time = time.time()
        best_solution = ts.solve()
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Calcula valor real da QBF (negativo da QBF inversa)
        real_qbf_value = -best_solution.cost
        
        return {
            'success': True,
            'best_solution': best_solution,
            'execution_time': execution_time,
            'method': params['method'],
            'tabu_search': ts,
            'quality_info': {
                'best_real_value': real_qbf_value,
                'iterations': params['iterations'],
                'domain_size': ts.obj_function.get_domain_size() if hasattr(ts.obj_function, 'get_domain_size') else len(ts.candidate_list)
            }
        }
        
    except FileNotFoundError:
        return {
            'success': False,
            'error': f"Arquivo '{params['filename']}' não encontrado",
            'traceback': traceback.format_exc() if params['debug'] else None
        }
    except MemoryError:
        return {
            'success': False,
            'error': "Erro de memória - instância muito grande. " +
                    "Tente reduzir o número de iterações ou o tamanho da instância.",
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
    method = results['method']
    
    if not params['quiet']:
        print("\n" + "="*60)
        print("RESULTADOS FINAIS")
        print("="*60)
        
        print(f"Método utilizado: {method.upper()}")
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
            if hasattr(ts, 'print_debug_info'):
                ts.print_debug_info()
            if hasattr(ts, 'print_probabilistic_info'):
                ts.print_probabilistic_info()
            if hasattr(ts, 'print_intensification_info'):
                ts.print_intensification_info()
        
        print("="*60)
    
    else:
        # Modo quiet - apenas resultado essencial
        print(f"Method: {method}")
        print(f"Value: {quality['best_real_value']:.6f}")
        print(f"Time: {exec_time:.3f}s")
        print(f"Solution: {best_sol.get_elements()}")


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