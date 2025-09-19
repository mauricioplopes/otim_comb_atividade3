#!/usr/bin/env python3
"""
ts_qbf.py

Implementação especializada do Tabu Search para o problema QBF.
"""

from collections import deque
from typing import List, Optional
import random

from core.abstract_ts import AbstractTabuSearch
from core.solution import Solution
from core.qbf import QBFInverse


class TabuSearchQBF(AbstractTabuSearch):
    """
    Implementação do Tabu Search especializada para o problema QBF.
    Usa QBFInverse pois o TS está configurado para minimização.
    """
    
    def __init__(self, tenure: int, iterations: int, filename: str, random_seed: int = 0):
        """
        Inicializa o Tabu Search para QBF.
        
        Args:
            tenure (int): Tamanho da lista tabu
            iterations (int): Número de iterações
            filename (str): Arquivo com a instância QBF
            random_seed (int): Seed para números aleatórios
        """
        # Cria função objetivo QBF inversa
        qbf_inverse = QBFInverse(filename)
        
        # Inicializa classe pai
        super().__init__(qbf_inverse, tenure, iterations, random_seed)
        
        # Referência tipada para facilitar acesso
        self.qbf: QBFInverse = qbf_inverse
    
    def _get_fake_element(self) -> int:
        """
        Retorna elemento fake para lista tabu.
        
        Returns:
            int: Valor -1 usado como elemento fake
        """
        return -1
    
    def make_candidate_list(self) -> List[int]:
        """
        Cria lista de candidatos com todos os índices das variáveis.
        
        Returns:
            List[int]: Lista com índices de 0 a n-1
        """
        return list(range(self.obj_function.get_domain_size()))
    
    def make_restricted_candidate_list(self) -> List[int]:
        """
        Cria lista restrita de candidatos vazia.
        
        Returns:
            List[int]: Lista vazia que será preenchida durante execução
        """
        return []
    
    def make_tabu_list(self) -> deque:
        """
        Cria e inicializa lista tabu com elementos fake.
        
        Returns:
            deque: Lista tabu com capacidade 2*tenure preenchida com fake elements
        """
        tabu_list = deque(maxlen=2 * self.tenure)
        for _ in range(2 * self.tenure):
            tabu_list.append(self.fake_element)
        return tabu_list
    
    def update_candidate_list(self):
        """
        Atualiza lista de candidatos.
        Para QBF, não há necessidade de atualização.
        """
        pass
    
    def create_empty_solution(self) -> Solution:
        """
        Cria solução vazia para QBF.
        
        Returns:
            Solution: Solução vazia com custo 0.0
        """
        solution = Solution()
        solution.cost = 0.0
        return solution
    
    def neighborhood_move(self) -> Optional[Solution]:
        """
        Executa movimento de vizinhança explorando inserção, remoção e troca.
        
        Returns:
            Optional[Solution]: None (modifica solução atual in-place)
        """
        min_delta_cost = float('inf')
        best_cand_in = None
        best_cand_out = None
        best_move_type = None
        
        self.update_candidate_list()
        
        # 1. AVALIA INSERÇÕES
        for cand_in in self.candidate_list:
            if not self.current_sol.contains_element(cand_in):
                delta_cost = self.obj_function.evaluate_insertion_cost(cand_in, self.current_sol)
                
                # Verifica se movimento é permitido (não-tabu ou satisfaz aspiração)
                if (not self.is_tabu(cand_in) or 
                    self.aspiration_criteria(cand_in, delta_cost)):
                    
                    if delta_cost < min_delta_cost:
                        min_delta_cost = delta_cost
                        best_cand_in = cand_in
                        best_cand_out = None
                        best_move_type = "insertion"
        
        # 2. AVALIA REMOÇÕES
        for cand_out in list(self.current_sol):  # Cria cópia para evitar problemas de iteração
            delta_cost = self.obj_function.evaluate_removal_cost(cand_out, self.current_sol)
            
            # Verifica se movimento é permitido
            if (not self.is_tabu(cand_out) or 
                self.aspiration_criteria(cand_out, delta_cost)):
                
                if delta_cost < min_delta_cost:
                    min_delta_cost = delta_cost
                    best_cand_in = None
                    best_cand_out = cand_out
                    best_move_type = "removal"
        
        # 3. AVALIA TROCAS (2-EXCHANGE)
        for cand_in in self.candidate_list:
            if not self.current_sol.contains_element(cand_in):
                for cand_out in list(self.current_sol):
                    delta_cost = self.obj_function.evaluate_exchange_cost(cand_in, cand_out, self.current_sol)
                    
                    # Para troca, ambos elementos devem ser não-tabu ou satisfazer aspiração
                    tabu_in = self.is_tabu(cand_in)
                    tabu_out = self.is_tabu(cand_out)
                    aspiration = self.aspiration_criteria(cand_in, delta_cost)
                    
                    if (not tabu_in and not tabu_out) or aspiration:
                        if delta_cost < min_delta_cost:
                            min_delta_cost = delta_cost
                            best_cand_in = cand_in
                            best_cand_out = cand_out
                            best_move_type = "exchange"
        
        # 4. IMPLEMENTA O MELHOR MOVIMENTO
        if best_move_type is None:
            # Nenhum movimento válido encontrado - isso não deveria acontecer
            print("AVISO: Nenhum movimento válido encontrado!")
            return None
        
        # Atualiza lista tabu e executa movimento
        if best_move_type == "insertion":
            # Apenas inserção
            self.add_to_tabu_list(self.fake_element)  # Nada removido
            self.add_to_tabu_list(best_cand_in)       # Elemento inserido vira tabu
            self.current_sol.add_element(best_cand_in)
            
        elif best_move_type == "removal":
            # Apenas remoção  
            self.add_to_tabu_list(best_cand_out)      # Elemento removido vira tabu
            self.add_to_tabu_list(self.fake_element)  # Nada inserido
            self.current_sol.remove_element(best_cand_out)
            
        elif best_move_type == "exchange":
            # Troca: remove um e insere outro
            self.add_to_tabu_list(best_cand_out)      # Elemento removido vira tabu
            self.add_to_tabu_list(best_cand_in)       # Elemento inserido vira tabu
            self.current_sol.remove_element(best_cand_out)
            self.current_sol.add_element(best_cand_in)
        
        # Reavalia solução atual
        self.obj_function.evaluate(self.current_sol)
        
        return None
    
    def print_debug_info(self):
        """Imprime informações de debug sobre o estado atual."""
        print("\n=== DEBUG INFO - Tabu Search QBF ===")
        print(f"Domain size: {self.obj_function.get_domain_size()}")
        print(f"Tenure: {self.tenure}")
        print(f"Iterations: {self.iterations}")
        
        if self.current_sol:
            print(f"Current solution size: {len(self.current_sol)}")
            print(f"Current cost: {self.current_sol.cost}")
        
        if self.best_sol:
            print(f"Best solution size: {len(self.best_sol)}")
            print(f"Best cost: {self.best_sol.cost}")
        
        if self.tabu_list:
            non_fake_elements = [x for x in self.tabu_list if x != self.fake_element]
            print(f"Tabu list size: {len(self.tabu_list)}")
            print(f"Non-fake elements in tabu: {len(non_fake_elements)}")
            if non_fake_elements:
                print(f"Tabu elements: {non_fake_elements[:10]}...")  # Mostra apenas os primeiros 10
        
        # Informações da matriz
        self.qbf.print_matrix_info()
        print("=" * 40)
    
    def get_solution_quality_info(self) -> dict:
        """
        Retorna informações sobre a qualidade das soluções.
        
        Returns:
            dict: Dicionário com informações das soluções
        """
        info = {
            'best_cost': self.best_sol.cost if self.best_sol else None,
            'best_size': len(self.best_sol) if self.best_sol else 0,
            'current_cost': self.current_sol.cost if self.current_sol else None,
            'current_size': len(self.current_sol) if self.current_sol else 0,
            'domain_size': self.obj_function.get_domain_size(),
            'iterations': self.iterations,
            'tenure': self.tenure
        }
        
        # Calcula valor real (não invertido) para QBF
        if info['best_cost'] is not None:
            info['best_real_value'] = -info['best_cost']  # Inverte pois usamos QBFInverse
        
        return info
