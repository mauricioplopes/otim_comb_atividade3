#!/usr/bin/env python3
"""
ts_qbf_sc_intensification.py

Implementação do Tabu Search para o problema MAX-SC-QBF usando estratégia INTENSIFICATION BY NEIGHBORHOOD.
Esta é a implementação do item 5: PADRÃO+METHOD2 - Busca Tabu PADRÃO mas com estratégia tabu alternativa 2.

Estratégia Intensification by Neighborhood:
- Quando uma nova melhor solução é encontrada, intensifica a busca nessa região
- Modifica temporariamente a vizinhança para focar em elementos similares à melhor solução
- Usa uma "elite list" dos melhores elementos encontrados
- Após período de intensificação, retorna à vizinhança normal para diversificação
- Balanceia automaticamente entre intensificação e diversificação
"""

import random
from typing import Optional, List, Set
from core.ts_qbf_sc_first_improving import TabuSearchQBFScFirstImproving


class TabuSearchQBFScIntensification(TabuSearchQBFScFirstImproving):
    """
    Implementação do Tabu Search para MAX-SC-QBF com estratégia Intensification by Neighborhood.
    
    A estratégia funciona da seguinte forma:
    1. Mantém uma "elite list" dos elementos que aparecem nas melhores soluções
    2. Quando uma nova melhor solução é encontrada, entra em modo de intensificação
    3. Durante intensificação, prioriza movimentos envolvendo elementos da elite list
    4. Após um período sem melhorias, retorna ao modo normal (diversificação)
    """
    
    def __init__(self, tenure: int, iterations: int, filename: str, random_seed: int = 0, 
                 elite_size: int = 5, intensification_period: int = 50):
        """
        Inicializa o Tabu Search com Intensification by Neighborhood para MAX-SC-QBF.
        
        Args:
            tenure (int): Tamanho da lista tabu (T1)
            iterations (int): Número de iterações
            filename (str): Arquivo com a instância QBF
            random_seed (int): Seed para números aleatórios
            elite_size (int): Tamanho da elite list (padrão: 5)
            intensification_period (int): Período de intensificação após nova melhor solução (padrão: 50)
        """
        super().__init__(tenure, iterations, filename, random_seed)
        
        # Parâmetros da intensificação
        self.elite_size = elite_size
        self.intensification_period = intensification_period
        
        # Elite list: elementos que aparecem frequentemente nas melhores soluções
        self.elite_list: Set[int] = set()
        self.element_frequency: dict = {}  # Frequência dos elementos nas soluções de alta qualidade
        
        # Controle de intensificação
        self.intensification_mode = False
        self.iterations_since_improvement = 0
        self.last_best_cost = float('inf')
        self.intensification_counter = 0
        
        # Histórico para análise
        self.best_solutions_history = []
        self.intensification_phases = []
    
    def update_elite_list(self, solution):
        """
        Atualiza a elite list baseada na solução atual.
        
        Args:
            solution: Solução para analisar
        """
        # Atualiza frequência dos elementos
        for element in solution:
            self.element_frequency[element] = self.element_frequency.get(element, 0) + 1
        
        # Reconstrói elite list com elementos mais frequentes
        if self.element_frequency:
            sorted_elements = sorted(self.element_frequency.items(), 
                                   key=lambda x: x[1], reverse=True)
            self.elite_list = set([elem for elem, _ in sorted_elements[:self.elite_size]])
    
    def enter_intensification_mode(self, new_best_solution):
        """
        Entra em modo de intensificação após encontrar nova melhor solução.
        
        Args:
            new_best_solution: Nova melhor solução encontrada
        """
        if not self.intensification_mode:
            self.intensification_mode = True
            self.intensification_counter = 0
            
            # Atualiza elite list com a nova melhor solução
            self.update_elite_list(new_best_solution)
            
            # Registra início da fase de intensificação
            self.intensification_phases.append({
                'start_iteration': len(self.best_solutions_history),
                'trigger_cost': new_best_solution.cost,
                'elite_elements': list(self.elite_list)
            })
            
            if self.VERBOSE:
                print(f"  >> INTENSIFICATION MODE ATIVADO")
                print(f"  >> Elite list: {sorted(list(self.elite_list))}")
    
    def exit_intensification_mode(self):
        """
        Sai do modo de intensificação e retorna à busca normal.
        """
        if self.intensification_mode:
            self.intensification_mode = False
            
            # Finaliza registro da fase
            if self.intensification_phases:
                self.intensification_phases[-1]['end_iteration'] = len(self.best_solutions_history)
                self.intensification_phases[-1]['duration'] = self.intensification_counter
            
            if self.VERBOSE:
                print(f"  >> INTENSIFICATION MODE DESATIVADO (após {self.intensification_counter} iterações)")
    
    def get_intensified_candidates(self, all_candidates: List[int]) -> List[int]:
        """
        Retorna lista de candidatos priorizando elementos da elite list.
        
        Args:
            all_candidates: Lista completa de candidatos
            
        Returns:
            Lista de candidatos ordenada por prioridade (elite primeiro)
        """
        if not self.elite_list:
            return all_candidates
        
        # Separa candidatos em elite e não-elite
        elite_candidates = [c for c in all_candidates if c in self.elite_list]
        non_elite_candidates = [c for c in all_candidates if c not in self.elite_list]
        
        # Durante intensificação, prioriza elite candidates
        if self.intensification_mode:
            # 70% de chance de focar apenas na elite, 30% de incluir outros
            if random.random() < 0.7 and elite_candidates:
                return elite_candidates
            else:
                # Mistura priorizando elite
                random.shuffle(elite_candidates)
                random.shuffle(non_elite_candidates)
                return elite_candidates + non_elite_candidates[:len(elite_candidates)]
        else:
            # Modo normal: apenas reorganiza colocando elite primeiro
            random.shuffle(elite_candidates)
            random.shuffle(non_elite_candidates)
            return elite_candidates + non_elite_candidates
    
    def neighborhood_move(self) -> Optional[None]:
        """
        Executa movimento de vizinhança com estratégia de Intensification by Neighborhood.
        
        Modifica a ordem de exploração da vizinhança baseada na elite list e no modo atual.
        
        Returns:
            Optional[None]: None (modifica solução atual in-place)
        """
        self.update_candidate_list()
        
        # Atualiza contadores
        self.iterations_since_improvement += 1
        if self.intensification_mode:
            self.intensification_counter += 1
        
        # Verifica se deve sair do modo de intensificação
        if (self.intensification_mode and 
            self.intensification_counter >= self.intensification_period):
            self.exit_intensification_mode()
        
        # Obtém candidatos com priorização baseada na estratégia
        base_candidates = self.candidate_list.copy()
        prioritized_candidates = self.get_intensified_candidates(base_candidates)
        
        # 1. AVALIA INSERÇÕES COM PRIORIZAÇÃO
        for cand_in in prioritized_candidates:
            if not self.current_sol.contains_element(cand_in):
                delta_cost = self.obj_function.evaluate_insertion_cost(cand_in, self.current_sol)
                
                # Verifica se movimento é permitido
                if (not self.is_tabu(cand_in) or 
                    self.aspiration_criteria(cand_in, delta_cost)):
                    
                    # FIRST-IMPROVING: aceita primeiro movimento que melhora
                    if delta_cost < 0:  # Melhoria
                        # Executa movimento de inserção
                        self.add_to_tabu_list(self.fake_element)
                        self.add_to_tabu_list(cand_in)
                        self.current_sol.add_element(cand_in)
                        self.obj_function.evaluate(self.current_sol)
                        return None
        
        # 2. AVALIA REMOÇÕES COM PRIORIZAÇÃO
        # Para remoções, usamos ordem baseada na elite list
        current_elements = list(self.current_sol)
        if self.intensification_mode and self.elite_list:
            # Durante intensificação, evita remover elementos da elite
            non_elite_elements = [e for e in current_elements if e not in self.elite_list]
            elite_elements = [e for e in current_elements if e in self.elite_list]
            prioritized_removal = non_elite_elements + elite_elements
        else:
            prioritized_removal = current_elements
        
        for cand_out in prioritized_removal:
            delta_cost = self.obj_function.evaluate_removal_cost(cand_out, self.current_sol)
            
            # Verifica se movimento é permitido
            if (not self.is_tabu(cand_out) or 
                self.aspiration_criteria(cand_out, delta_cost)):
                
                # FIRST-IMPROVING: aceita primeiro movimento que melhora
                if delta_cost < 0:  # Melhoria
                    # Executa movimento de remoção
                    self.add_to_tabu_list(cand_out)
                    self.add_to_tabu_list(self.fake_element)
                    self.current_sol.remove_element(cand_out)
                    self.obj_function.evaluate(self.current_sol)
                    return None
        
        # 3. AVALIA TROCAS COM PRIORIZAÇÃO
        for cand_in in prioritized_candidates:
            if not self.current_sol.contains_element(cand_in):
                for cand_out in prioritized_removal:
                    delta_cost = self.obj_function.evaluate_exchange_cost(cand_in, cand_out, self.current_sol)
                    
                    # Para troca, ambos elementos devem ser permitidos
                    tabu_in_ok = not self.is_tabu(cand_in) or self.aspiration_criteria(cand_in, delta_cost)
                    tabu_out_ok = not self.is_tabu(cand_out) or self.aspiration_criteria(cand_out, delta_cost)
                    
                    if tabu_in_ok and tabu_out_ok:
                        # FIRST-IMPROVING: aceita primeiro movimento que melhora
                        if delta_cost < 0:  # Melhoria
                            # Executa movimento de troca
                            self.add_to_tabu_list(cand_out)
                            self.add_to_tabu_list(cand_in)
                            self.current_sol.remove_element(cand_out)
                            self.current_sol.add_element(cand_in)
                            self.obj_function.evaluate(self.current_sol)
                            return None
        
        # 4. SE NENHUM MOVIMENTO MELHORADOR ENCONTRADO, USA MELHOR MOVIMENTO DISPONÍVEL
        # (mantém a lógica original para garantir que sempre há movimento)
        min_delta_cost = float('inf')
        best_cand_in = None
        best_cand_out = None
        best_move_type = None
        
        # Reavalia inserções para encontrar o melhor movimento não-melhorador
        for cand_in in prioritized_candidates:
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
        for cand_out in prioritized_removal:
            delta_cost = self.obj_function.evaluate_removal_cost(cand_out, self.current_sol)
            
            if (not self.is_tabu(cand_out) or 
                self.aspiration_criteria(cand_out, delta_cost)):
                
                if delta_cost < min_delta_cost:
                    min_delta_cost = delta_cost
                    best_cand_in = None
                    best_cand_out = cand_out
                    best_move_type = "removal"
        
        # Reavalia trocas
        for cand_in in prioritized_candidates:
            if not self.current_sol.contains_element(cand_in):
                for cand_out in prioritized_removal:
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
    
    def solve(self):
        """
        Método principal do Tabu Search com Intensification by Neighborhood.
        Sobrescreve o método base para controlar as fases de intensificação.
        """
        # Inicializa melhor solução
        self.best_sol = self.create_empty_solution()
        
        # Constrói solução inicial
        self.constructive_heuristic()
        
        # Inicializa lista tabu
        self.tabu_list = self.make_tabu_list()
        
        # Define melhor solução como a inicial
        self.best_sol = self.current_sol.copy()
        self.last_best_cost = self.best_sol.cost
        
        if self.VERBOSE:
            print(f"Solução inicial: {self.current_sol}")
        
        # Loop principal do Tabu Search
        for iteration in range(self.iterations):
            # Executa movimento de vizinhança
            self.neighborhood_move()
            
            # Verifica se encontrou nova melhor solução
            if self.current_sol.cost < self.best_sol.cost:
                self.best_sol = self.current_sol.copy()
                self.best_solutions_history.append({
                    'iteration': iteration,
                    'cost': self.best_sol.cost,
                    'solution': list(self.best_sol)
                })
                
                # Reseta contador de iterações sem melhoria
                self.iterations_since_improvement = 0
                self.last_best_cost = self.best_sol.cost
                
                # Entra em modo de intensificação
                self.enter_intensification_mode(self.best_sol)
                
                if self.VERBOSE:
                    print(f"(Iter. {iteration}) Nova melhor solução: {self.best_sol}")
        
        # Finaliza intensificação se ainda ativa
        if self.intensification_mode:
            self.exit_intensification_mode()
        
        return self.best_sol
    
    def print_intensification_info(self):
        """Imprime informações específicas da estratégia de intensificação."""
        print(f"\nESTRATÉGIA INTENSIFICATION BY NEIGHBORHOOD:")
        print(f"  Elite size: {self.elite_size}")
        print(f"  Período de intensificação: {self.intensification_period}")
        print(f"  Modo atual: {'INTENSIFICAÇÃO' if self.intensification_mode else 'DIVERSIFICAÇÃO'}")
        print(f"  Iterações desde melhoria: {self.iterations_since_improvement}")
        
        if self.elite_list:
            print(f"  Elite list atual: {sorted(list(self.elite_list))}")
        
        if self.element_frequency:
            top_elements = sorted(self.element_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
            print(f"  Top 10 elementos mais frequentes:")
            for elem, freq in top_elements:
                print(f"    Elemento {elem}: {freq} aparições")
        
        print(f"  Fases de intensificação: {len(self.intensification_phases)}")
        for i, phase in enumerate(self.intensification_phases):
            duration = phase.get('duration', 'em andamento')
            print(f"    Fase {i+1}: iter {phase['start_iteration']}, duração {duration}")


# Função de conveniência para criar o solver
def create_intensification_solver(tenure: int, iterations: int, filename: str, 
                                random_seed: int = 0, elite_size: int = 5, 
                                intensification_period: int = 50) -> TabuSearchQBFScIntensification:
    """
    Factory function para criar um solver com Intensification by Neighborhood.
    
    Args:
        tenure (int): Tamanho da lista tabu (T1)
        iterations (int): Número de iterações
        filename (str): Arquivo da instância
        random_seed (int): Seed para números aleatórios
        elite_size (int): Tamanho da elite list
        intensification_period (int): Período de intensificação
        
    Returns:
        TabuSearchQBFScIntensification: Solver configurado
    """
    return TabuSearchQBFScIntensification(tenure, iterations, filename, random_seed, 
                                        elite_size, intensification_period)