#!/usr/bin/env python3
"""
Implementação do Tabu Search para QBF em Python
Convertido do código Java fornecido
"""

import random
import sys
from collections import deque
from typing import List, Optional
import time


class Solution(list):
    """Classe que representa uma solução, herda de list"""
    
    def __init__(self, solution=None):
        super().__init__()
        self.cost = float('inf')
        
        if solution is not None:
            self.extend(solution)
            self.cost = solution.cost if hasattr(solution, 'cost') else float('inf')
    
    def __str__(self):
        return f"Solution: cost=[{self.cost}], size=[{len(self)}], elements={super().__str__()}"


class QBF:
    """Classe para o problema Quadratic Binary Function"""
    
    def __init__(self, filename: str):
        self.A = None  # Inicializa antes
        self.size = self._read_input(filename)
        self.variables = [0.0] * self.size
    
    def _read_input(self, filename: str) -> int:
        """Lê o arquivo de entrada e inicializa a matriz A"""
        try:
            print(f"Tentando ler arquivo: {filename}")
            
            with open(filename, 'r') as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]
            
            print(f"Arquivo lido: {len(lines)} linhas")
            
            if not lines:
                raise ValueError("Arquivo vazio")
            
            # Primeira linha é o tamanho
            n = int(lines[0])
            print(f"Dimensão da matriz: {n}")
            
            # SEMPRE inicializa a matriz, mesmo se houver erro depois
            self.A = [[0.0] * n for _ in range(n)]
            print("Matriz inicializada com zeros")
            
            # Verifica se temos linhas suficientes
            if len(lines) < n + 1:
                print(f"AVISO: Arquivo tem apenas {len(lines)} linhas, esperado pelo menos {n+1}")
                return n  # Retorna com matriz de zeros
            
            # Lê a matriz triangular superior
            line_idx = 1
            for i in range(n):
                if line_idx >= len(lines):
                    print(f"AVISO: Linha {line_idx} não encontrada, usando zeros para linha {i}")
                    break
                
                try:
                    values = list(map(float, lines[line_idx].split()))
                    expected_elements = n - i  # Número esperado de elementos na linha i
                    
                    if i < 5:  # Debug apenas primeiras linhas
                        print(f"Linha {i}: {len(values)} elementos (esperado {expected_elements})")
                    
                    # Preenche a matriz
                    for j, val in enumerate(values):
                        col_idx = i + j
                        if col_idx < n:
                            self.A[i][col_idx] = val
                            # A matriz é triangular superior, parte inferior fica zero
                            if col_idx != i:
                                self.A[col_idx][i] = 0.0
                    
                except ValueError as e:
                    print(f"Erro ao converter linha {i}: {e}")
                    # Continua com zeros para esta linha
                
                line_idx += 1
            
            print(f"Matriz carregada com sucesso")
            return n
            
        except FileNotFoundError:
            print(f"ERRO: Arquivo '{filename}' não encontrado!")
            # Inicializa matriz pequena para evitar crash
            self.A = [[0.0]]
            return 1
        except Exception as e:
            print(f"ERRO ao ler arquivo {filename}: {e}")
            # Inicializa matriz pequena para evitar crash
            self.A = [[0.0]]
            return 1
    
    def reset_variables(self):
        """Reset das variáveis para zero"""
        self.variables = [0.0] * self.size
    
    def set_variables(self, solution: Solution):
        """Define as variáveis baseado na solução"""
        self.reset_variables()
        if solution:
            for elem in solution:
                if 0 <= elem < self.size:
                    self.variables[elem] = 1.0
    
    def print_matrix_info(self):
        """Imprime informações sobre a matriz (para debug)"""
        print(f"=== Informações da Matriz ===")
        print(f"Size: {self.size}")
        print(f"Matrix A is None: {self.A is None}")
        
        if self.A is None:
            print("ERRO: Matriz não foi inicializada!")
            return
        
        print(f"Matriz {self.size}x{self.size} inicializada")
        print("Primeiros elementos da diagonal:")
        for i in range(min(5, self.size)):
            print(f"  A[{i}][{i}] = {self.A[i][i]}")
        
        print("Alguns elementos da primeira linha:")
        for j in range(min(10, self.size)):
            print(f"  A[0][{j}] = {self.A[0][j]}")
        
        # Verifica se temos valores não-zero
        non_zero_count = 0
        total_elements = self.size * self.size
        for i in range(self.size):
            for j in range(self.size):
                if self.A[i][j] != 0.0:
                    non_zero_count += 1
        
        print(f"Elementos não-zero: {non_zero_count}/{total_elements}")
        print("=" * 30)
    
    def get_domain_size(self) -> int:
        """Retorna o tamanho do domínio"""
        return self.size
    
    def evaluate(self, solution: Solution) -> float:
        """Avalia uma solução completa"""
        self.set_variables(solution)
        solution.cost = self._evaluate_qbf()
        return solution.cost
    
    def _evaluate_qbf(self) -> float:
        """Calcula f(x) = x'.A.x"""
        total = 0.0
        vec_aux = [0.0] * self.size
        
        for i in range(self.size):
            aux = 0.0
            for j in range(self.size):
                aux += self.variables[j] * self.A[i][j]
            vec_aux[i] = aux
            total += aux * self.variables[i]
        
        return total
    
    def evaluate_insertion_cost(self, elem: int, solution: Solution) -> float:
        """Avalia o custo de inserir um elemento"""
        self.set_variables(solution)
        return self._evaluate_insertion_qbf(elem)
    
    def _evaluate_insertion_qbf(self, i: int) -> float:
        """Calcula o custo de inserção incremental"""
        if self.variables[i] == 1:
            return 0.0
        return self._evaluate_contribution_qbf(i)
    
    def evaluate_removal_cost(self, elem: int, solution: Solution) -> float:
        """Avalia o custo de remover um elemento"""
        self.set_variables(solution)
        return self._evaluate_removal_qbf(elem)
    
    def _evaluate_removal_qbf(self, i: int) -> float:
        """Calcula o custo de remoção incremental"""
        if self.variables[i] == 0:
            return 0.0
        return -self._evaluate_contribution_qbf(i)
    
    def evaluate_exchange_cost(self, elem_in: int, elem_out: int, solution: Solution) -> float:
        """Avalia o custo de trocar dois elementos"""
        self.set_variables(solution)
        return self._evaluate_exchange_qbf(elem_in, elem_out)
    
    def _evaluate_exchange_qbf(self, elem_in: int, elem_out: int) -> float:
        """Calcula o custo de troca incremental"""
        if elem_in == elem_out:
            return 0.0
        if self.variables[elem_in] == 1:
            return self._evaluate_removal_qbf(elem_out)
        if self.variables[elem_out] == 0:
            return self._evaluate_insertion_qbf(elem_in)
        
        total = 0.0
        total += self._evaluate_contribution_qbf(elem_in)
        total -= self._evaluate_contribution_qbf(elem_out)
        total -= (self.A[elem_in][elem_out] + self.A[elem_out][elem_in])
        
        return total
    
    def _evaluate_contribution_qbf(self, i: int) -> float:
        """Calcula a contribuição de um elemento para a função objetivo"""
        if self.A is None:
            print("ERRO: Matriz A é None!")
            return 0.0
        
        if not (0 <= i < self.size):
            print(f"ERRO: Índice {i} fora do range [0, {self.size-1}]")
            return 0.0
        
        total = 0.0
        
        for j in range(self.size):
            if i != j:
                try:
                    total += self.variables[j] * (self.A[i][j] + self.A[j][i])
                except (IndexError, TypeError) as e:
                    print(f"ERRO ao acessar A[{i}][{j}] ou A[{j}][{i}]: {e}")
                    return 0.0
        
        try:
            total += self.A[i][i]
        except (IndexError, TypeError) as e:
            print(f"ERRO ao acessar A[{i}][{i}]: {e}")
            return 0.0
        
        return total


class QBFInverse(QBF):
    """Versão inversa da QBF para minimização"""
    
    def _evaluate_qbf(self) -> float:
        return -super()._evaluate_qbf()
    
    def _evaluate_insertion_qbf(self, i: int) -> float:
        return -super()._evaluate_insertion_qbf(i)
    
    def _evaluate_removal_qbf(self, i: int) -> float:
        return -super()._evaluate_removal_qbf(i)
    
    def _evaluate_exchange_qbf(self, elem_in: int, elem_out: int) -> float:
        return -super()._evaluate_exchange_qbf(elem_in, elem_out)


class TabuSearch:
    """Implementação do Tabu Search para QBF"""
    
    VERBOSE = True
    
    def __init__(self, obj_function: QBF, tenure: int, iterations: int):
        self.obj_function = obj_function
        self.tenure = tenure
        self.iterations = iterations
        self.best_cost = None
        self.cost = None
        self.best_sol = None
        self.sol = None
        self.CL = None  # Candidate List
        self.RCL = None  # Restricted Candidate List
        self.TL = None  # Tabu List
        self.fake = -1
        
        # Inicializa o gerador de números aleatórios
        random.seed(0)
    
    def make_cl(self) -> List[int]:
        """Cria a lista de candidatos"""
        return list(range(self.obj_function.get_domain_size()))
    
    def make_rcl(self) -> List[int]:
        """Cria a lista restrita de candidatos"""
        return []
    
    def make_tl(self) -> deque:
        """Cria a lista tabu"""
        tl = deque(maxlen=2 * self.tenure)
        for _ in range(2 * self.tenure):
            tl.append(self.fake)
        return tl
    
    def update_cl(self):
        """Atualiza a lista de candidatos (não faz nada nesta implementação)"""
        pass
    
    def create_empty_sol(self) -> Solution:
        """Cria uma solução vazia"""
        sol = Solution()
        sol.cost = 0.0
        return sol
    
    def constructive_heuristic(self) -> Solution:
        """Heurística construtiva"""
        self.CL = self.make_cl()
        self.RCL = self.make_rcl()
        self.sol = self.create_empty_sol()
        self.cost = float('inf')
        
        # Loop principal da heurística construtiva
        while not self._constructive_stop_criteria():
            max_cost = float('-inf')
            min_cost = float('inf')
            self.cost = self.sol.cost
            self.update_cl()
            
            # Explora todos os candidatos para encontrar max e min custo
            for c in self.CL:
                if c not in self.sol:
                    delta_cost = self.obj_function.evaluate_insertion_cost(c, self.sol)
                    if delta_cost < min_cost:
                        min_cost = delta_cost
                    if delta_cost > max_cost:
                        max_cost = delta_cost
            
            # Insere na RCL os candidatos com melhor performance
            self.RCL.clear()
            for c in self.CL:
                if c not in self.sol:
                    delta_cost = self.obj_function.evaluate_insertion_cost(c, self.sol)
                    if delta_cost <= min_cost:
                        self.RCL.append(c)
            
            if not self.RCL:
                break
            
            # Escolhe um candidato aleatório da RCL
            rnd_index = random.randint(0, len(self.RCL) - 1)
            in_cand = self.RCL[rnd_index]
            self.sol.append(in_cand)
            self.obj_function.evaluate(self.sol)
        
        return self.sol
    
    def _constructive_stop_criteria(self) -> bool:
        """Critério de parada da heurística construtiva"""
        return self.cost <= self.sol.cost
    
    def neighborhood_move(self) -> Optional[Solution]:
        """Executa um movimento de vizinhança"""
        min_delta_cost = float('inf')
        best_cand_in = None
        best_cand_out = None
        
        self.update_cl()
        
        # Avalia inserções
        for cand_in in self.CL:
            if cand_in not in self.sol:
                delta_cost = self.obj_function.evaluate_insertion_cost(cand_in, self.sol)
                aspiration = self.sol.cost + delta_cost < self.best_sol.cost
                
                if cand_in not in self.TL or aspiration:
                    if delta_cost < min_delta_cost:
                        min_delta_cost = delta_cost
                        best_cand_in = cand_in
                        best_cand_out = None
        
        # Avalia remoções
        for cand_out in self.sol:
            delta_cost = self.obj_function.evaluate_removal_cost(cand_out, self.sol)
            aspiration = self.sol.cost + delta_cost < self.best_sol.cost
            
            if cand_out not in self.TL or aspiration:
                if delta_cost < min_delta_cost:
                    min_delta_cost = delta_cost
                    best_cand_in = None
                    best_cand_out = cand_out
        
        # Avalia trocas
        for cand_in in self.CL:
            if cand_in not in self.sol:
                for cand_out in self.sol:
                    delta_cost = self.obj_function.evaluate_exchange_cost(cand_in, cand_out, self.sol)
                    aspiration = self.sol.cost + delta_cost < self.best_sol.cost
                    
                    if (cand_in not in self.TL and cand_out not in self.TL) or aspiration:
                        if delta_cost < min_delta_cost:
                            min_delta_cost = delta_cost
                            best_cand_in = cand_in
                            best_cand_out = cand_out
        
        # Implementa o melhor movimento não-tabu
        self.TL.popleft()
        if best_cand_out is not None:
            self.sol.remove(best_cand_out)
            self.TL.append(best_cand_out)
        else:
            self.TL.append(self.fake)
        
        self.TL.popleft()
        if best_cand_in is not None:
            self.sol.append(best_cand_in)
            self.TL.append(best_cand_in)
        else:
            self.TL.append(self.fake)
        
        self.obj_function.evaluate(self.sol)
        
        return None
    
    def solve(self) -> Solution:
        """Método principal do Tabu Search"""
        self.best_sol = self.create_empty_sol()
        self.constructive_heuristic()
        self.TL = self.make_tl()
        
        self.best_sol = Solution(self.sol)
        
        for i in range(self.iterations):
            self.neighborhood_move()
            if self.best_sol.cost > self.sol.cost:
                self.best_sol = Solution(self.sol)
                if self.VERBOSE:
                    print(f"(Iter. {i}) BestSol = {self.best_sol}")
        
        return self.best_sol


def main():
    """Função principal"""
    if len(sys.argv) not in [4, 5]:
        print("Uso: python tabu_search.py <tenure> <iterations> <filename> [debug]")
        print("Exemplo: python tabu_search.py 20 1000 qbf200")
        print("Debug: python tabu_search.py 20 1000 qbf200 debug")
        sys.exit(1)
    
    try:
        tenure = int(sys.argv[1])
        iterations = int(sys.argv[2])
        filename = sys.argv[3]
        debug_mode = len(sys.argv) == 5 and sys.argv[4].lower() == 'debug'
        
        if debug_mode:
            print(f"=== MODO DEBUG ===")
            print(f"Arquivo: {filename}")
            print(f"Tenure: {tenure}")
            print(f"Iterations: {iterations}")
        
        # Usa QBF_Inverse pois o TS é configurado para minimização
        qbf_inverse = QBFInverse(filename)
        
        if debug_mode:
            print("Arquivo lido com sucesso!")
            qbf_inverse.print_matrix_info()
            print("Iniciando Tabu Search...")
        
        start_time = time.time()
        
        tabu_search = TabuSearch(qbf_inverse, tenure, iterations)
        best_sol = tabu_search.solve()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"maxVal = {best_sol}")
        print(f"Time = {total_time:.3f} seg")
        
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filename}' não encontrado!")
        print("Certifique-se de que o caminho está correto.")
        sys.exit(1)
    except ValueError as e:
        print(f"Erro de valor: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()