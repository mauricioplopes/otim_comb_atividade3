from qbf import QBFInverse

class QBFSCInverse(QBFInverse):
    def __init__(self, filename: str):
        self.sets = []
        super().__init__(filename)

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

            # Inicializa lista de conjuntos para as restrições de set-cover
            self.sets = []
            
            # Verifica se temos linhas suficientes
            if len(lines) <  2 * (n + 1):
                print(f"AVISO: Arquivo tem apenas {len(lines)} linhas, esperado pelo menos {2*(n+1)}")
                return n
            
            # Lê as restrições de set-cover
            line_idx = 2 # Podemos pular a segunda linha, que tem os tamanhos dos conjuntos
            for i in range(n):
                if line_idx >= len(lines):
                    print(f"AVISO: Linha {line_idx} não encontrada, conjuntos podem estar incompletos")
                    break
                
                try:
                    self.sets.append(set(map(int, lines[line_idx].split())))
                except ValueError as e:
                    raise ValueError(f"Erro ao processar linha {line_idx}: {e}") from e
                
                line_idx += 1

            print(f"{len(self.sets)} conjuntos lidos")
            
            # Lê a matriz triangular superior
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
                    raise ValueError(f"Erro ao processar linha {line_idx}: {e}") from e
                
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