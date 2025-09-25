#!/usr/bin/env python3
"""
ts_qbf_sc_probabilistic.py

Implementação do Tabu Search para o problema MAX-SC-QBF usando estratégia PROBABILISTIC TS.
Esta é a implementação do item 4: PADRÃO+METHOD1 - Busca Tabu PADRÃO mas com estratégia tabu alternativa 1.

Estratégia Probabilistic TS:
- Movimentos tabu podem ser aceitos com uma probabilidade baseada em quão recentemente 
  foram adicionados à lista tabu
- Elementos mais recentes na lista tabu têm menor probabilidade de serem aceitos
- Elementos mais antigos na lista tabu têm maior probabilidade de serem aceitos
- Isso permite mais diversificação que o critério de aspiração padrão
"""

import random
import math
from typing import Optional, Any
from collections import deque
from core.ts_qbf_sc_first_improving import TabuSearchQBFScFirstImproving


class TabuSearchQBFScProbabilistic(TabuSearchQBFScFirstImproving):
    """
    Implementação do Tabu Search para MAX-SC-QBF com estratégia Probabilistic TS.
    
    A diferença principal é que movimentos tabu podem ser aceitos com uma probabilidade
    que depende de há quanto tempo o elemento está na lista tabu:
    - Probabilidade = exp(-alpha * tabu_age / tenure)
    onde tabu_age é a posição do elemento na lista tabu (0 = mais recente)
    """
    
    def __init__(self, tenure: int, iterations: int, filename: str, random_seed: int = 0, alpha: float = 2.0):
        """
        Inicializa o Tabu Search Probabilistic para MAX-SC-QBF.
        
        Args:
            tenure (int): Tamanho da lista tabu (T1)
            iterations (int): Número de iterações  
            filename (str): Arquivo com a instância QBF
            random_seed (int): Seed para números aleatórios
            alpha (float): Parâmetro que controla a curva de probabilidade (padrão: 2.0)
        """
        super().__init__(tenure, iterations, filename, random_seed)
        
        # Parâmetro de controle da probabilidade
        self.alpha = alpha
        
        # Estrutura para rastrear posições na lista tabu
        # Mapeia elemento -> posição na lista (0 = mais recente)
        self.tabu_positions = {}
    
    def make_tabu_list(self) -> deque:
        """
        Cria e inicializa lista tabu com elementos fake.
        Sobrescreve para inicializar também o tracking de posições.
        
        Returns:
            deque: Lista tabu com capacidade 2*tenure preenchida com fake elements
        """
        tabu_list = deque(maxlen=2 * self.tenure)
        self.tabu_positions = {}
        
        for i in range(2 * self.tenure):
            tabu_list.append(self.fake_element)
            if self.fake_element not in self.tabu_positions:
                self.tabu_positions[self.fake_element] = []
            self.tabu_positions[self.fake_element].append(i)
        
        return tabu_list
    
    def add_to_tabu_list(self, element: Any):
        """
        Adiciona um elemento à lista tabu e atualiza posições.
        
        Args:
            element: Elemento a ser adicionado
        """
        if self.tabu_list is not None:
            # Remove o mais antigo e suas posições
            oldest = self.tabu_list.popleft()
            if oldest in self.tabu_positions:
                if self.tabu_positions[oldest]:
                    self.tabu_positions[oldest].pop(0)  # Remove posição mais antiga
                if not self.tabu_positions[oldest]:  # Se não há mais posições
                    del self.tabu_positions[oldest]
            
            # Adiciona o novo elemento
            self.tabu_list.append(element)
            
            # Atualiza posições - incrementa todas existentes
            for elem in self.tabu_positions:
                self.tabu_positions[elem] = [pos + 1 for pos in self.tabu_positions[elem]]
            
            # Adiciona nova posição para o elemento inserido
            if element not in self.tabu_positions:
                self.tabu_positions[element] = []
            self.tabu_positions[element].append(0)  # Posição 0 = mais recente
    
    def get_tabu_acceptance_probability(self, element: Any) -> float:
        """
        Calcula a probabilidade de aceitar um movimento tabu.
        
        Args:
            element: Elemento a ser verificado
            
        Returns:
            float: Probabilidade de aceitação (0.0 a 1.0)
        """
        if not self.is_tabu(element):
            return 1.0  # Não é tabu, sempre aceita
        
        if element not in self.tabu_positions:
            return 1.0  # Não encontrado nas posições, aceita
        
        # Usa a posição mais recente (menor valor)
        min_position = min(self.tabu_positions[element])
        
        # Calcula probabilidade baseada na posição
        # Quanto menor a posição (mais recente), menor a probabilidade
        # P = exp(-alpha * position / max_position)
        max_position = len(self.tabu_list) - 1
        if max_position <= 0:
            return 0.0
        
        normalized_age = min_position / max_position
        probability = math.exp(-self.alpha * normalized_age)
        
        return probability
    
    def probabilistic_tabu_check(self, element: Any) -> bool:
        """
        Verifica se um movimento tabu deve ser aceito probabilisticamente.
        
        Args:
            element: Elemento a ser verificado
            
        Returns:
            bool: True se o movimento deve ser aceito
        """
        if not self.is_tabu(element):
            return True  # Não é tabu, sempre aceita
        
        # Calcula probabilidade de aceitação
        probability = self.get_tabu_acceptance_probability(element)
        
        # Gera número aleatório e compara
        random_value = random.random()
        
        return random_value < probability
    
    def aspiration_criteria(self, element: Any, delta_cost: float) -> bool:
        """
        Critério de aspiração combinado: aspiração padrão OU probabilística.
        
        Args:
            element: Elemento do movimento
            delta_cost (float): Variação de custo do movimento
            
        Returns:
            bool: True se o movimento deve ser aceito
        """
        # Primeiro verifica aspiração padrão (melhoria sobre melhor solução conhecida)
        standard_aspiration = super().aspiration_criteria(element, delta_cost)
        
        if standard_aspiration:
            return True
        
        # Se não passou na aspiração padrão, usa critério probabilístico
        return self.probabilistic_tabu_check(element)
    
    def neighborhood_move(self) -> Optional[None]:
        """
        Executa movimento de vizinhança usando estratégia PROBABILISTIC TS.
        
        Igual ao first-improving, mas com critério de aceitação probabilístico
        para movimentos tabu ao invés de apenas aspiração determinística.
        
        Returns:
            Optional[None]: None (modifica solução atual in-place)
        """
        self.update_candidate_list()
        
        # 1. AVALIA INSERÇÕES - FIRST-IMPROVING COM PROBABILISTIC TS
        for cand_in in self.candidate_list:
            if not self.current_sol.contains_element(cand_in):
                delta_cost = self.obj_function.evaluate_insertion_cost(cand_in, self.current_sol)
                
                # Verifica se movimento é permitido (não-tabu ou aceito probabilisticamente)
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
        
        # 2. AVALIA REMOÇÕES - FIRST-IMPROVING COM PROBABILISTIC TS
        for cand_out in list(self.current_sol):
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
        
        # 3. AVALIA TROCAS (2-EXCHANGE) - FIRST-IMPROVING COM PROBABILISTIC TS
        for cand_in in self.candidate_list:
            if not self.current_sol.contains_element(cand_in):
                for cand_out in list(self.current_sol):
                    delta_cost = self.obj_function.evaluate_exchange_cost(cand_in, cand_out, self.current_sol)
                    
                    # Para troca, ambos elementos devem ser permitidos
                    tabu_in_ok = not self.is_tabu(cand_in) or self.aspiration_criteria(cand_in, delta_cost)
                    tabu_out_ok = not self.is_tabu(cand_out) or self.aspiration_criteria(cand_out, delta_cost)
                    
                    if tabu_in_ok and tabu_out_ok:
                        # FIRST-IMPROVING: aceita primeiro movimento que melhora
                        if delta_cost < 0:  # Melhoria
                            # Executa movimento de troca
                            self.add_to_tabu_list(cand_out)  # Elemento removido vira tabu
                            self.add_to_tabu_list(cand_in)   # Elemento inserido vira tabu
                            self.current_sol.remove_element(cand_out)
                            self.current_sol.add_element(cand_in)
                            self.obj_function.evaluate(self.current_sol)
                            return None
        
        # 4. SE NENHUM MOVIMENTO MELHORADOR ENCONTRADO, USA MELHOR MOVIMENTO DISPONÍVEL
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
                    
                    tabu_in_ok = not self.is_tabu(cand_in) or self.aspiration_criteria(cand_in, delta_cost)
                    tabu_out_ok = not self.is_tabu(cand_out) or self.aspiration_criteria(cand_out, delta_cost)
                    
                    if tabu_in_ok and tabu_out_ok:
                        if delta_cost < min_delta_cost:
                            min_delta_cost = delta_cost
                            best_cand_in = cand_in
                            best_cand_out = cand_out
                            best_move_type = "exchange"
        
        # 5. IMPLEMENTA O MELHOR MOVIMENTO
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
    
    def print_probabilistic_info(self):
        """Imprime informações específicas da estratégia probabilística."""
        print(f"\nESTRATÉGIA PROBABILISTIC TS:")
        print(f"  Alpha (parâmetro): {self.alpha}")
        print(f"  Elementos na lista tabu: {len([x for x in self.tabu_list if x != self.fake_element])}")
        
        if self.tabu_positions:
            print(f"  Elementos com posições:")
            for elem, positions in self.tabu_positions.items():
                if elem != self.fake_element and positions:
                    min_pos = min(positions)
                    prob = self.get_tabu_acceptance_probability(elem)
                    print(f"    Elemento {elem}: pos_min={min_pos}, prob={prob:.3f}")


# Função de conveniência para criar o solver
def create_probabilistic_solver(tenure: int, iterations: int, filename: str, 
                              random_seed: int = 0, alpha: float = 2.0) -> TabuSearchQBFScProbabilistic:
    """
    Factory function para criar um solver Probabilistic TS.
    
    Args:
        tenure (int): Tamanho da lista tabu (T1)
        iterations (int): Número de iterações
        filename (str): Arquivo da instância
        random_seed (int): Seed para números aleatórios
        alpha (float): Parâmetro de controle da probabilidade
        
    Returns:
        TabuSearchQBFScProbabilistic: Solver configurado
    """
    return TabuSearchQBFScProbabilistic(tenure, iterations, filename, random_seed, alpha)