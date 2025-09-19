#!/usr/bin/env python3
"""
__init__.py

Arquivo de inicialização do pacote Tabu Search QBF.
Define as importações principais e metadados do pacote.
"""

__version__ = "1.0.0"
__author__ = "Convertido do framework Java original"
__description__ = "Implementação do Tabu Search para Função Binária Quadrática (QBF)"

# Importações principais
from .solution import Solution
from .evaluator import Evaluator
from .qbf import QBF, QBFInverse
from .abstract_ts import AbstractTabuSearch
from .ts_qbf import TabuSearchQBF

# Lista de símbolos exportados
__all__ = [
    'Solution',
    'Evaluator', 
    'QBF',
    'QBFInverse',
    'AbstractTabuSearch',
    'TabuSearchQBF'
]

# Configurações globais
DEFAULT_TENURE = 20
DEFAULT_ITERATIONS = 1000
DEFAULT_RANDOM_SEED = 0

def create_qbf_solver(filename: str, tenure: int = DEFAULT_TENURE, 
                      iterations: int = DEFAULT_ITERATIONS, 
                      random_seed: int = DEFAULT_RANDOM_SEED) -> TabuSearchQBF:
    """
    Factory function para criar um solver QBF com configurações padrão.
    
    Args:
        filename (str): Arquivo da instância QBF
        tenure (int): Tamanho da lista tabu
        iterations (int): Número de iterações
        random_seed (int): Seed para números aleatórios
        
    Returns:
        TabuSearchQBF: Instância configurada do solver
    """
    return TabuSearchQBF(tenure, iterations, filename, random_seed)

def get_version_info() -> dict:
    """
    Retorna informações sobre a versão do pacote.
    
    Returns:
        dict: Informações de versão
    """
    return {
        'version': __version__,
        'author': __author__,
        'description': __description__
    }
