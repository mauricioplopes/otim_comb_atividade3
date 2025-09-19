
"""
abstract_ts.py

Implementação abstrata do algoritmo Tabu Search.
Define a estrutura geral que pode ser especializada para diferentes problemas.
"""

import random
from abc import ABC, abstractmethod
from collections import deque
from typing import List, Any, Optional

from core.solution import Solution
from core.evaluator import Evaluator


class AbstractTabuSearch(ABC):
    """
    Classe abstrata para implementação do algoritmo Tabu Search.
    Define a estrutura geral do algoritmo que deve ser especializada.
    """
    
    # Flag para controlar saídas verbosas
    VERBOSE = True
    
    def __init__(self, obj_function: Evaluator, tenure: int, iterations: int, random_seed: int = 0):
        """
        Inicializa o Tabu Search.
        
        Args:
            obj_function (Evaluator): Função objetivo
            tenure (int): Tamanho da lista tabu (tenure)
            iterations (int): Número de iterações
            random_seed (int): Seed para gerador aleatório
        """
        self.obj_function = obj_function
        self.tenure = tenure
        self.iterations = iterations
        
        # Soluções e custos
        self.best_sol: Optional[Solution] = None
        self.current_sol: Optional[Solution] = None
        self.best_cost: Optional[float] = None
        self.current_cost: Optional[float] = None
        
        # Listas do algoritmo
        self.candidate_list: Optional[List[Any]] = None
        self.restricted_candidate_list: Optional[List[Any]] = None
        self.tabu_list: Optional[deque] = None
        
        # Elemento fake para preenchimento da lista tabu
        self.fake_element = self._get_fake_element()
        
        # Configura gerador aleatório
        random.seed(random_seed)
    
    @abstractmethod
    def _get_fake_element(self) -> Any:
        """
        Retorna um elemento fake usado para preencher a lista tabu.
        
        Returns:
            Any: Elemento que não pode ser confundido com elementos reais
        """
        pass
    
    @abstractmethod
    def make_candidate_list(self) -> List[Any]:
        """
        Cria a lista de candidatos.
        
        Returns:
            List[Any]: Lista com todos os candidatos possíveis
        """
        pass
    
    @abstractmethod
    def make_restricted_candidate_list(self) -> List[Any]:
        """
        Cria a lista restrita de candidatos (RCL).
        
        Returns:
            List[Any]: Lista vazia inicial (será preenchida durante execução)
        """
        pass
    
    @abstractmethod
    def make_tabu_list(self) -> deque:
        """
        Cria e inicializa a lista tabu.
        
        Returns:
            deque: Lista tabu inicializada com elementos fake
        """
        pass
    
    @abstractmethod
    def update_candidate_list(self):
        """
        Atualiza a lista de candidatos de acordo com a solução atual.
        Pode ser usada para recalcular custos ou filtrar candidatos.
        """
        pass
    
    @abstractmethod
    def create_empty_solution(self) -> Solution:
        """
        Cria uma solução vazia.
        
        Returns:
            Solution: Nova solução vazia
        """
        pass
    
    @abstractmethod
    def neighborhood_move(self) -> Optional[Solution]:
        """
        Executa um movimento de vizinhança (inserção, remoção ou troca).
        
        Returns:
            Optional[Solution]: Solução resultante do movimento (pode ser None)
        """
        pass
    
    def constructive_heuristic(self) -> Solution:
        """
        Heurística construtiva para gerar solução inicial.
        Usa estratégia gulosa com lista restrita de candidatos (RCL).
        
        Returns:
            Solution: Solução inicial construída
        """
        # Inicializa estruturas
        self.candidate_list = self.make_candidate_list()
        self.restricted_candidate_list = self.make_restricted_candidate_list()
        self.current_sol = self.create_empty_solution()
        
        # Avalia solução inicial (vazia)
        self.obj_function.evaluate(self.current_sol)
        
        max_iterations = len(self.candidate_list) * 2  # Limite de segurança
        iteration_count = 0
        
        # Loop principal da construção
        while iteration_count < max_iterations:
            # Salva custo atual para critério de parada
            previous_cost = self.current_sol.cost
            self.update_candidate_list()
            
            # Obtém candidatos disponíveis
            available_candidates = self._get_available_candidates()
            
            if not available_candidates:
                if self.VERBOSE:
                    print("Nenhum candidato disponível - finalizando construção")
                break
            
            # Encontra o range de custos dos candidatos
            min_cost = float('inf')
            
            candidate_costs = {}
            for candidate in available_candidates:
                delta_cost = self.obj_function.evaluate_insertion_cost(candidate, self.current_sol)
                candidate_costs[candidate] = delta_cost
                if delta_cost < min_cost:
                    min_cost = delta_cost
            
            # Constrói RCL com candidatos de melhor performance (menor custo)
            self.restricted_candidate_list.clear()
            for candidate, delta_cost in candidate_costs.items():
                if delta_cost <= min_cost:  # Apenas os melhores
                    self.restricted_candidate_list.append(candidate)
            
            if not self.restricted_candidate_list:
                if self.VERBOSE:
                    print("RCL vazia - finalizando construção")
                break
            
            # Seleciona candidato aleatório da RCL
            selected_idx = random.randint(0, len(self.restricted_candidate_list) - 1)
            selected_candidate = self.restricted_candidate_list[selected_idx]
            
            # Adiciona à solução e reavalia
            self.current_sol.add_element(selected_candidate)
            self.obj_function.evaluate(self.current_sol)
            
            # Critério de parada: sem melhoria significativa
            if abs(self.current_sol.cost - previous_cost) < 1e-10:
                if self.VERBOSE:
                    print(f"Sem melhoria significativa - finalizando construção na iteração {iteration_count}")
                break
            
            # Para maximização (QBF inversa com valores negativos), 
            # se o custo está piorando muito, para
            if self.current_sol.cost > previous_cost + abs(previous_cost) * 0.1:
                if self.VERBOSE:
                    print(f"Custo piorando muito - finalizando construção")
                break
            
            iteration_count += 1
        
        if self.VERBOSE:
            print(f"Heurística construtiva finalizada em {iteration_count} iterações")
            print(f"Solução inicial: {self.current_sol}")
        
        return self.current_sol
    
    def _get_available_candidates(self) -> List[Any]:
        """
        Retorna candidatos disponíveis (não estão na solução atual).
        
        Returns:
            List[Any]: Lista de candidatos disponíveis
        """
        return [c for c in self.candidate_list if not self.current_sol.contains_element(c)]
    
    def solve(self) -> Solution:
        """
        Método principal do Tabu Search.
        
        Returns:
            Solution: Melhor solução encontrada
        """
        # Inicializa melhor solução
        self.best_sol = self.create_empty_solution()
        
        # Constrói solução inicial
        self.constructive_heuristic()
        
        # Inicializa lista tabu
        self.tabu_list = self.make_tabu_list()
        
        # Define melhor solução como a inicial
        self.best_sol = self.current_sol.copy()
        
        if self.VERBOSE:
            print(f"Solução inicial: {self.current_sol}")
        
        # Loop principal do Tabu Search
        for iteration in range(self.iterations):
            # Executa movimento de vizinhança
            self.neighborhood_move()
            
            # Atualiza melhor solução se necessário
            if self.current_sol.cost < self.best_sol.cost:
                self.best_sol = self.current_sol.copy()
                if self.VERBOSE:
                    print(f"(Iter. {iteration}) Nova melhor solução: {self.best_sol}")
        
        return self.best_sol
    
    def get_best_solution(self) -> Optional[Solution]:
        """
        Retorna a melhor solução encontrada.
        
        Returns:
            Optional[Solution]: Melhor solução ou None se não foi executado
        """
        return self.best_sol
    
    def get_current_solution(self) -> Optional[Solution]:
        """
        Retorna a solução atual.
        
        Returns:
            Optional[Solution]: Solução atual ou None se não foi executado
        """
        return self.current_sol
    
    def get_tabu_list(self) -> Optional[deque]:
        """
        Retorna a lista tabu atual.
        
        Returns:
            Optional[deque]: Lista tabu ou None se não foi inicializada
        """
        return self.tabu_list
    
    def is_tabu(self, element: Any) -> bool:
        """
        Verifica se um elemento está na lista tabu.
        
        Args:
            element: Elemento a ser verificado
            
        Returns:
            bool: True se o elemento é tabu
        """
        return self.tabu_list is not None and element in self.tabu_list
    
    def aspiration_criteria(self, element: Any, delta_cost: float) -> bool:
        """
        Verifica se um movimento tabu pode ser aceito pelo critério de aspiração.
        
        Args:
            element: Elemento do movimento
            delta_cost (float): Variação de custo do movimento
            
        Returns:
            bool: True se o movimento deve ser aceito apesar de ser tabu
        """
        if self.current_sol is None or self.best_sol is None:
            return False
        
        # Aceita se o movimento resulta em solução melhor que a melhor conhecida
        return self.current_sol.cost + delta_cost < self.best_sol.cost
    
    def add_to_tabu_list(self, element: Any):
        """
        Adiciona um elemento à lista tabu.
        
        Args:
            element: Elemento a ser adicionado
        """
        if self.tabu_list is not None:
            self.tabu_list.popleft()  # Remove o mais antigo
            self.tabu_list.append(element)  # Adiciona o novo
    
    def set_verbose(self, verbose: bool):
        """
        Define se deve imprimir informações durante execução.
        
        Args:
            verbose (bool): True para ativar modo verboso
        """
        self.VERBOSE = verbose
