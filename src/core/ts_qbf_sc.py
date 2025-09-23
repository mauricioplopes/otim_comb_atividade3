from core.ts_qbf import TabuSearchQBF
from core.qbf_sc import QBFSCInverse

class TabuSearchQBFSc(TabuSearchQBF):
    """
    Implementação do Tabu Search especializada para o problema QBF com restrição de set-cover
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
        super().__init__(tenure, iterations, filename, random_seed, qbf_inverse=QBFSCInverse(filename))

    def update_candidate_list(self):
        """
        Atualiza lista de candidatos.
        """
        qbf_sc_inverse: QBFSCInverse = self.qbf  # type: ignore
        self.candidate_list = qbf_sc_inverse.get_variables_that_can_be_set_to_zero()