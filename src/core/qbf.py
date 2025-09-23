#!/usr/bin/env python3
"""
qbf.py

Implementação da função objetivo para o problema Quadratic Binary Function (QBF).
"""

from typing import List
from core.evaluator import Evaluator
from core.solution import Solution


class QBF(Evaluator):
    """
    Classe para o problema Quadratic Binary Function.
    Implementa f(x) = x^T * A * x onde x é um vetor binário.
    """
    
    def __init__(self, filename: str):
        """
        Inicializa a QBF lendo dados de um arquivo.
        
        Args:
            filename (str): Nome do arquivo contendo a matriz A
        """
        self.A = None
        self.size = self._read_input(filename)
        self.variables = [1.0] * self.size
    
    def _read_input(self, filename: str) -> int:
        """
        Lê o arquivo de entrada e inicializa a matriz A.
        
        Args:
            filename (str): Nome do arquivo
            
        Returns:
            int: Dimensão da matriz (número de variáveis)
        """
        try:
            print(f"Lendo arquivo: {filename}")
            
            with open(filename, 'r') as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]
            
            print(f"Arquivo lido: {len(lines)} linhas")
            
            if not lines:
                raise ValueError("Arquivo vazio")
            
            # Primeira linha é o tamanho
            n = int(lines[0])
            print(f"Dimensão da matriz: {n}")
            
            # SEMPRE inicializa a matriz
            self.A = [[0.0] * n for _ in range(n)]
            print("Matriz inicializada com zeros")
            
            # Verifica se temos linhas suficientes
            if len(lines) < n + 1:
                print(f"AVISO: Arquivo tem apenas {len(lines)} linhas, esperado pelo menos {n+1}")
                return n
            
            # Lê a matriz triangular superior
            line_idx = 1
            for i in range(n):
                if line_idx >= len(lines):
                    print(f"AVISO: Linha {line_idx} não encontrada, usando zeros para linha {i}")
                    break
                
                try:
                    values = list(map(float, lines[line_idx].split()))
                    expected_elements = n - i
                    
                    if i < 5:  # Debug apenas primeiras linhas
                        print(f"Linha {i}: {len(values)} elementos (esperado {expected_elements})")
                    
                    # Preenche a matriz triangular superior
                    for j, val in enumerate(values):
                        col_idx = i + j
                        if col_idx < n:
                            self.A[i][col_idx] = val
                            # Parte inferior fica zero (não simétrica)
                            if col_idx != i:
                                self.A[col_idx][i] = 0.0
                
                except ValueError as e:
                    print(f"Erro ao converter linha {i}: {e}")
                
                line_idx += 1
            
            print("Matriz carregada com sucesso")
            return n
            
        except FileNotFoundError:
            print(f"ERRO: Arquivo '{filename}' não encontrado!")
            self.A = [[0.0]]
            return 1
        except Exception as e:
            print(f"ERRO ao ler arquivo {filename}: {e}")
            self.A = [[0.0]]
            return 1
    
    def reset_variables(self):
        """Reset das variáveis para um."""
        self.variables = [1.0] * self.size
    
    def set_variables(self, solution: Solution):
        """
        Define as variáveis baseado na solução. Um elemento estar contido em solution significa que a variável deve ser definida como 0.
        Isso pode parecer contra-intuitiva, mas a ideia é que uma solução vazia representa uma solução em que todos os conjuntos são selecionados (variáveis = 1).
        O contrário (todos as variáveis = 0) seria uma solução inválida para QBF-SC.
        
        Args:
            solution (Solution): Solução atual
        """
        self.reset_variables()
        if solution:
            for elem in solution:
                if 0 <= elem < self.size:
                    self.variables[elem] = 0.0
    
    def get_domain_size(self) -> int:
        """
        Retorna o tamanho do domínio.
        
        Returns:
            int: Número de variáveis
        """
        return self.size
    
    def evaluate(self, solution: Solution) -> float:
        """
        Avalia uma solução completa.
        
        Args:
            solution (Solution): Solução a ser avaliada
            
        Returns:
            float: Valor da função objetivo
        """
        self.set_variables(solution)
        solution.cost = self._evaluate_qbf()
        return solution.cost
    
    def _evaluate_qbf(self) -> float:
        """
        Calcula f(x) = x^T * A * x.
        
        Returns:
            float: Valor da função QBF
        """
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
        """
        Avalia o custo de inserir um elemento na solução (o que significa definir a variável como 0).
        
        Args:
            elem (int): Elemento a ser inserido
            solution (Solution): Solução atual
            
        Returns:
            float: Custo de inserção
        """
        self.set_variables(solution)
        return self._evaluate_removal_qbf(elem)
    
    def _evaluate_insertion_qbf(self, i: int) -> float:
        """
        Calcula o custo de inserção incremental.
        
        Args:
            i (int): Índice do elemento
            
        Returns:
            float: Custo de inserção
        """
        if self.variables[i] == 1:
            return 0.0
        return self._evaluate_contribution_qbf(i)
    
    def evaluate_removal_cost(self, elem: int, solution: Solution) -> float:
        """
        Avalia o custo de remover um elemento (o que significa definir a variável como 1).
        
        Args:
            elem (int): Elemento a ser removido
            solution (Solution): Solução atual
            
        Returns:
            float: Custo de remoção
        """
        self.set_variables(solution)
        return self._evaluate_insertion_qbf(elem)
    
    def _evaluate_removal_qbf(self, i: int) -> float:
        """
        Calcula o custo de remoção incremental.
        
        Args:
            i (int): Índice do elemento
            
        Returns:
            float: Custo de remoção
        """
        if self.variables[i] == 0:
            return 0.0
        return -self._evaluate_contribution_qbf(i)
    
    def evaluate_exchange_cost(self, elem_in: int, elem_out: int, solution: Solution) -> float:
        """
        Avalia o custo de trocar dois elementos. O elemento a entrar é definido como 0 e o elemento a sair como 1.
        
        Args:
            elem_in (int): Elemento a entrar
            elem_out (int): Elemento a sair
            solution (Solution): Solução atual
            
        Returns:
            float: Custo de troca
        """
        self.set_variables(solution)
        return self._evaluate_exchange_qbf(elem_out, elem_in)
    
    def _evaluate_exchange_qbf(self, elem_in: int, elem_out: int) -> float:
        """
        Calcula o custo de troca incremental.
        
        Args:
            elem_in (int): Elemento a entrar
            elem_out (int): Elemento a sair
            
        Returns:
            float: Custo de troca
        """
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
        """
        Calcula a contribuição de um elemento para a função objetivo.
        
        Args:
            i (int): Índice do elemento
            
        Returns:
            float: Contribuição do elemento
        """
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
    
    def print_matrix_info(self):
        """Imprime informações sobre a matriz para debug."""
        print(f"=== Informações da Matriz QBF ===")
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
        
        # Verifica elementos não-zero
        non_zero_count = 0
        total_elements = self.size * self.size
        for i in range(self.size):
            for j in range(self.size):
                if self.A[i][j] != 0.0:
                    non_zero_count += 1
        
        print(f"Elementos não-zero: {non_zero_count}/{total_elements}")
        print("=" * 35)


class QBFInverse(QBF):
    """
    Versão inversa da QBF para uso em algoritmos de minimização.
    Multiplica todos os valores por -1.
    """
    
    def _evaluate_qbf(self) -> float:
        """
        Avalia a QBF inversa.
        
        Returns:
            float: Valor negativo da QBF original
        """
        return -super()._evaluate_qbf()
    
    def _evaluate_insertion_qbf(self, i: int) -> float:
        """
        Avalia inserção na QBF inversa.
        
        Args:
            i (int): Índice do elemento
            
        Returns:
            float: Custo de inserção invertido
        """
        return -super()._evaluate_insertion_qbf(i)
    
    def _evaluate_removal_qbf(self, i: int) -> float:
        """
        Avalia remoção na QBF inversa.
        
        Args:
            i (int): Índice do elemento
            
        Returns:
            float: Custo de remoção invertido
        """
        return -super()._evaluate_removal_qbf(i)
    
    def _evaluate_exchange_qbf(self, elem_in: int, elem_out: int) -> float:
        """
        Avalia troca na QBF inversa.
        
        Args:
            elem_in (int): Elemento a entrar
            elem_out (int): Elemento a sair
            
        Returns:
            float: Custo de troca invertido
        """
        return -super()._evaluate_exchange_qbf(elem_in, elem_out)
