# Tabu Search para QBF - Implementação Modular

Implementação em Python do algoritmo **Tabu Search** para resolver o problema de maximização de uma **Função Binária Quadrática (QBF)**.

## Estrutura do Projeto

```
src/
├── core
│	├── solution.py     # Classe Solution
│	├── evaluator.py    # Interface para funções objetivo
│	├── qbf.py          # Implementação QBF e QBFInverse
│	├── abstract_ts.py  # Framework genérico Tabu Search
│	└── ts_qbf.py       # Tabu Search especializado para QBF
├── instances			# Diretório das instâncias
│	└── qbf				# Repositório das instâncias QBF
├── main.py             # Interface de linha de comando
├── test_basic.py       # Testes unitários
└── quick_test.py       # Teste rápido de funcionamento
```

## Instalação

Requer apenas **Python 3.7+** (sem dependências externas):

```bash
git clone https://github.com/seu-usuario/tabu-search-qbf.git
cd tabu-search-qbf/src
```

## Como Usar

### Execução Básica
```bash
python main.py <tenure> <iterations> <arquivo_instancia>
```

### Exemplos
```bash
# Execução padrão
python main.py 20 1000 instances/qbf200

# Modo silencioso
python main.py 20 1000 instances/qbf200 quiet

# Com seed personalizada
python main.py 20 1000 instances/qbf200 seed=42
```

### Teste do Sistema
```bash
python quick_test.py     # Teste rápido
python test_basic.py     # Testes completos
```

## Formato das Instâncias

Arquivo texto com matriz triangular superior:

```
n
a11 a12 a13 ... a1n
a22 a23 ... a2n
a33 ... a3n
...
ann
```

**Exemplo:**
```
5
2 -1 3 0 1
1 0 -1 2
3 1 -1
0 2
1
```

## Parâmetros

| Parâmetro | Descrição | Valores Sugeridos |
|-----------|-----------|-------------------|
| `tenure` | Tamanho da lista tabu | 10-30 |
| `iterations` | Número de iterações | 100-1000 |
| `filename` | Arquivo da instância | Caminho válido |

## Arquitetura Modular

### Classes Principais
- **`Solution`**: Representa soluções do problema
- **`Evaluator`**: Interface para funções objetivo
- **`QBF/QBFInverse`**: Função objetivo quadrática binária
- **`AbstractTabuSearch`**: Framework genérico do algoritmo
- **`TabuSearchQBF`**: Implementação especializada para QBF

## Saída Esperada

```
=== TABU SEARCH PARA QBF ===
Arquivo: instances/qbf200
Tenure: 20
Iterations: 1000

(Iter. 15) Nova melhor solução: Solution: cost=[-245.0], size=[18]
(Iter. 23) Nova melhor solução: Solution: cost=[-198.0], size=[15]

==================================================
RESULTADOS FINAIS
==================================================
Melhor solução encontrada:
  Valor real QBF: 156.0
  Variáveis selecionadas: 12
  Tempo: 2.341 segundos
```


## Referências

- **Gendreau, M., & Potvin, J. Y.** (2010). Handbook of metaheuristics. Springer.
- **Kochenberger, G., et al.** (2014). The unconstrained binary quadratic programming problem: a survey. Journal of Combinatorial Optimization, 28(1), 58-81.
