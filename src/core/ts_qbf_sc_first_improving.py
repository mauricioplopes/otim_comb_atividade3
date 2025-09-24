#!/usr/bin/env python3
"""
ts_qbf_sc_first_improving.py

Implementação do Tabu Search para o problema MAX-SC-QBF usando estratégia FIRST-IMPROVING.
Esta é a implementação do item 1: PADRÃO - Busca Tabu com método de busca first-improving,
"tabu tenure" igual a T1, estratégia tabu padrão.
"""

from typing import Optional
from core.ts_qbf_sc import TabuSearchQBFSc


class TabuSearchQBFScFirstImproving(TabuSearchQBFSc):
    """
    Implementação do Tabu Search para MAX-SC-QBF com busca first-improving.
    
    A diferença principal é que este método para assim que encontra o primeiro 
    movimento que melhora a solução atual, ao invés de explorar toda a vizinhança 
    para encontrar o melhor movimento.
    """
    
    def __init__(self, tenure: int, iterations: int, filename: str, random_seed: int = 0):
        """
        Inicializa o Tabu Search First-Improving para MAX-SC-QBF.
        
        Args:
            tenure (int): Tamanho da lista tabu (T1)
            iterations (int): Número de iterações
            filename (str): Arquivo com a instância QBF
            random_seed (int): Seed para números aleatórios
        """
        super().__init__(tenure, iterations, filename, random_seed)
    
    def neighborhood_move(self) -> Optional[None]:
        """
        Executa movimento de vizinhança usando estratégia FIRST-IMPROVING.
        
        Ao contrário do best-improving que explora toda a vizinhança,
        o first-improving para assim que encontra o primeiro movimento
        que melhora a solução atual.
        
        Returns:
            Optional[None]: None (modifica solução atual in-place)
        """
        self.update_candidate_list()
        
        # 1. AVALIA INSERÇÕES - FIRST-IMPROVING
        for cand_in in self.candidate_list:
            if not self.current_sol.contains_element(cand_in):
                delta_cost = self.obj_function.evaluate_insertion_cost(cand_in, self.current_sol)
                
                # Verifica se movimento é permitido (não-tabu ou satisfaz aspiração)
                if (not self.is_tabu(cand_in) or 
                    self.aspiration_criteria(cand_in, delta_cost)):
                    
                    # FIRST-IMPROVING: aceita primeiro movimento que melhora
                    if delta_cost < 0:  # Melhoria (custo negativo = melhoria na QBF inversa)
                        # Executa movimento de inserção
                        self.add_to_tabu_list(self.fake_element)  # Nada removido
                        self.add_to_tabu_list(cand_in)           # Elemento inserido vira tabu
                        self.current_sol.add_element(cand_in)
                        self.obj_function.evaluate(self.current_sol)
                        return None
        
        # 2. AVALIA REMOÇÕES - FIRST-IMPROVING
        for cand_out in list(self.current_sol):  # Cria cópia para evitar problemas
            delta_cost = self.obj_function.evaluate_removal_cost(cand_out, self.current_sol)
            
            # Verifica se movimento é permitido
            if (not self.is_tabu(cand_out) or 
                self.aspiration_criteria(cand_out, delta_cost)):
                
                # FIRST-IMPROVING: aceita primeiro movimento que melhora
                if delta_cost < 0:  # Melhoria
                    # Executa movimento de remoção
                    self.add_to_tabu_list(cand_out)           # Elemento removido vira tabu
                    self.add_to_tabu_list(self.fake_element)  # Nada inserido
                    self.current_sol.remove_element(cand_out)
                    self.obj_function.evaluate(self.current_sol)
                    return None
        
        # 3. AVALIA TROCAS (2-EXCHANGE) - FIRST-IMPROVING
        for cand_in in self.candidate_list:
            if not self.current_sol.contains_element(cand_in):
                for cand_out in list(self.current_sol):
                    delta_cost = self.obj_function.evaluate_exchange_cost(cand_in, cand_out, self.current_sol)
                    
                    # Para troca, ambos elementos devem ser não-tabu ou satisfazer aspiração
                    tabu_in = self.is_tabu(cand_in)
                    tabu_out = self.is_tabu(cand_out)
                    aspiration = self.aspiration_criteria(cand_in, delta_cost)
                    
                    if (not tabu_in and not tabu_out) or aspiration:
                        # FIRST-IMPROVING: aceita primeiro movimento que melhora
                        if delta_cost < 0:  # Melhoria
                            # Executa movimento de troca
                            self.add_to_tabu_list(cand_out)  # Elemento removido vira tabu
                            self.add_to_tabu_list(cand_in)   # Elemento inserido vira tabu
                            self.current_sol.remove_element(cand_out)
                            self.current_sol.add_element(cand_in)
                            self.obj_function.evaluate(self.current_sol)
                            return None
        
        # 4. SE NENHUM MOVIMENTO MELHORADOR ENCONTRADO, USA BEST-IMPROVING
        # (fallback para garantir que sempre há movimento)
        min_delta_cost = float('inf')
        best_cand_in = None
        best_cand_out = None
        best_move_type = None
        
        # Reavalia inserções para encontrar o melhor movimento não-melhorador
        for cand_in in self.candidate_list:
            if not self.current_sol.contains_element(cand_in):
                delta_cost = self.obj_function.evaluate_insertion_cost(cand_in, self.current_sol)
                
                if (not self.is_tabu(cand_in) or 
                    self.aspiration_criteria(cand_in, delta_cost)):
                    
                    if delta_cost < min_delta_cost:
                        min_delta_cost = delta_cost
                        best_cand_in = cand_in
                        best_cand_out = None
                        best_move_type = "insertion"
        
        # Reavalia remoções
        for cand_out in list(self.current_sol):
            delta_cost = self.obj_function.evaluate_removal_cost(cand_out, self.current_sol)
            
            if (not self.is_tabu(cand_out) or 
                self.aspiration_criteria(cand_out, delta_cost)):
                
                if delta_cost < min_delta_cost:
                    min_delta_cost = delta_cost
                    best_cand_in = None
                    best_cand_out = cand_out
                    best_move_type = "removal"
        
        # Reavalia trocas
        for cand_in in self.candidate_list:
            if not self.current_sol.contains_element(cand_in):
                for cand_out in list(self.current_sol):
                    delta_cost = self.obj_function.evaluate_exchange_cost(cand_in, cand_out, self.current_sol)
                    
                    tabu_in = self.is_tabu(cand_in)
                    tabu_out = self.is_tabu(cand_out)
                    aspiration = self.aspiration_criteria(cand_in, delta_cost)
                    
                    if (not tabu_in and not tabu_out) or aspiration:
                        if delta_cost < min_delta_cost:
                            min_delta_cost = delta_cost
                            best_cand_in = cand_in
                            best_cand_out = cand_out
                            best_move_type = "exchange"
        
        # 5. IMPLEMENTA O MELHOR MOVIMENTO (mesmo que não seja melhorador)
        if best_move_type is None:
            print("AVISO: Nenhum movimento válido encontrado!")
            return None
        
        # Executa o movimento escolhido
        if best_move_type == "insertion":
            self.add_to_tabu_list(self.fake_element)
            self.add_to_tabu_list(best_cand_in)
            self.current_sol.add_element(best_cand_in)
            
        elif best_move_type == "removal":
            self.add_to_tabu_list(best_cand_out)
            self.add_to_tabu_list(self.fake_element)
            self.current_sol.remove_element(best_cand_out)
            
        elif best_move_type == "exchange":
            self.add_to_tabu_list(best_cand_out)
            self.add_to_tabu_list(best_cand_in)
            self.current_sol.remove_element(best_cand_out)
            self.current_sol.add_element(best_cand_in)
        
        # Reavalia solução atual
        self.obj_function.evaluate(self.current_sol)
        
        return None


# Função de conveniência para criar o solver
def create_first_improving_solver(tenure: int, iterations: int, filename: str, random_seed: int = 0) -> TabuSearchQBFScFirstImproving:
    """
    Factory function para criar um solver First-Improving.
    
    Args:
        tenure (int): Tamanho da lista tabu (T1)
        iterations (int): Número de iterações
        filename (str): Arquivo da instância
        random_seed (int): Seed para números aleatórios
        
    Returns:
        TabuSearchQBFScFirstImproving: Solver configurado
    """
    return TabuSearchQBFScFirstImproving(tenure, iterations, filename, random_seed)