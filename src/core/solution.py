"""
solution.py

Classe Solution para representar soluções no Tabu Search.
Herda de list para compatibilidade com operações de lista.
"""

class Solution(list):
    """
    Classe que representa uma solução para problemas de otimização.
    Herda de list para permitir operações como append, remove, etc.
    """
    
    def __init__(self, solution=None):
        """
        Inicializa uma nova solução.
        
        Args:
            solution: Solução existente para copiar (opcional)
        """
        super().__init__()
        self.cost = float('inf')
        
        if solution is not None:
            self.extend(solution)
            self.cost = solution.cost if hasattr(solution, 'cost') else float('inf')
    
    def copy(self):
        """
        Cria uma cópia da solução atual.
        
        Returns:
            Solution: Nova instância com os mesmos elementos e custo
        """
        return Solution(self)
    
    def is_empty(self):
        """
        Verifica se a solução está vazia.
        
        Returns:
            bool: True se a solução não contém elementos
        """
        return len(self) == 0
    
    def get_cost(self):
        """
        Retorna o custo da solução.
        
        Returns:
            float: Custo atual da solução
        """
        return self.cost
    
    def set_cost(self, cost):
        """
        Define o custo da solução.
        
        Args:
            cost (float): Novo custo da solução
        """
        self.cost = cost
    
    def get_size(self):
        """
        Retorna o tamanho da solução.
        
        Returns:
            int: Número de elementos na solução
        """
        return len(self)
    
    def contains_element(self, element):
        """
        Verifica se um elemento está na solução.
        
        Args:
            element: Elemento a ser verificado
            
        Returns:
            bool: True se o elemento está presente
        """
        return element in self
    
    def add_element(self, element):
        """
        Adiciona um elemento à solução.
        
        Args:
            element: Elemento a ser adicionado
        """
        if element not in self:
            self.append(element)
    
    def remove_element(self, element):
        """
        Remove um elemento da solução.
        
        Args:
            element: Elemento a ser removido
            
        Returns:
            bool: True se o elemento foi removido, False se não estava presente
        """
        if element in self:
            self.remove(element)
            return True
        return False
    
    def get_elements(self):
        """
        Retorna uma cópia da lista de elementos.
        
        Returns:
            list: Lista com todos os elementos da solução
        """
        return list(self)
    
    def __str__(self):
        """
        Representação em string da solução.
        
        Returns:
            str: String formatada com custo, tamanho e elementos
        """
        elements_str = list.__str__(self)  # Usa diretamente o __str__ da lista
        return f"Solution: cost=[{self.cost}], size=[{len(self)}], elements={elements_str}"
    
    def __repr__(self):
        """
        Representação para debug.
        
        Returns:
            str: Representação detalhada da solução
        """
        elements_repr = list.__repr__(self)  # Usa diretamente o __repr__ da lista
        return f"Solution(cost={self.cost}, elements={elements_repr})"
