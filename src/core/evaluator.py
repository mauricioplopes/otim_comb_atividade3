#!/usr/bin/env python3
"""
evaluator.py

Interface para avaliadores de função objetivo.
Define os métodos que todo avaliador deve implementar.
"""

from abc import ABC, abstractmethod
from typing import Any
from core.solution import Solution


class Evaluator(ABC):
    """
    Interface abstrata para avaliadores de função objetivo.
    Define os métodos essenciais que toda função objetivo deve implementar.
    """
    
    @abstractmethod
    def get_domain_size(self) -> int:
        """
        Retorna o tamanho do domínio do problema.
        
        Returns:
            int: Número de variáveis de decisão
        """
        pass
    
    @abstractmethod
    def evaluate(self, solution: Solution) -> float:
        """
        Avalia uma solução completa.
        
        Args:
            solution (Solution): Solução a ser avaliada
            
        Returns:
            float: Valor da função objetivo para a solução
        """
        pass
    
    @abstractmethod
    def evaluate_insertion_cost(self, element: Any, solution: Solution) -> float:
        """
        Avalia o custo de inserir um elemento na solução.
        
        Args:
            element: Elemento a ser inserido
            solution (Solution): Solução atual
            
        Returns:
            float: Variação do custo ao inserir o elemento
        """
        pass
    
    @abstractmethod
    def evaluate_removal_cost(self, element: Any, solution: Solution) -> float:
        """
        Avalia o custo de remover um elemento da solução.
        
        Args:
            element: Elemento a ser removido
            solution (Solution): Solução atual
            
        Returns:
            float: Variação do custo ao remover o elemento
        """
        pass
    
    @abstractmethod
    def evaluate_exchange_cost(self, element_in: Any, element_out: Any, solution: Solution) -> float:
        """
        Avalia o custo de trocar dois elementos.
        
        Args:
            element_in: Elemento a entrar na solução
            element_out: Elemento a sair da solução
            solution (Solution): Solução atual
            
        Returns:
            float: Variação do custo ao fazer a troca
        """
        pass
