# QBF Tabu Search Framework - Estrutura Modular

Framework Python para resolução de problemas de maximização de Função Binária Quadrática (QBF) usando metaheurísticas de Busca Tabu, desenvolvido para a disciplina MO824/MC859 - Atividade 3.

## 📁 Estrutura do Projeto

```
qbf_tabu_search/
├── __init__.py                 # Pacote principal
├── main.py                     # Interface de linha de comando
├── requirements.txt            # Dependências Python
├── README.md                   # Este arquivo
│
├── core/                       # Módulos fundamentais
│   ├── __init__.py
│   ├── solution.py            # Classe Solution
│   ├── evaluator.py           # Interface Evaluator
│   └── abstract_ts.py         # Classe abstrata AbstractTS
│
├── problems/                   # Implementações de problemas
│   ├── __init__.py
│   └── qbf/                   # Módulo QBF específico
│       ├── __init__.py
│       ├── qbf.py            # Classe QBF base
│       ├── qbf_inverse.py    # Variações da QBF
│       └── ts_qbf.py         # Busca Tabu para QBF
│
├── utils/                      # Utilitários
│   ├── __init__.py
│   ├── file_io.py            # Leitura/escrita de arquivos
│   ├── validation.py         # Validação de instâncias
│   └── analysis.py           # Análise de instâncias
│
├── examples/                   # Exemplos de uso
│   ├── __init__.py
│   ├── basic_usage.py        # Uso básico
│   └── parameter_study.py    # Estudo paramétrico
│
├── tests/                      # Testes unitários
│   ├── __init__.py
│   ├── test_core.py          # Testes dos módulos core
│   ├── test_qbf.py           # Testes das classes QBF
│   └── test_utils.py         # Testes dos utilitários
│
└── instances/                  # Instâncias QBF
    ├── qbf060                 # Instância pequena (60 variáveis)
    ├── qbf200                 # Instância maior (200 variáveis)
    └── ...                    # Outras instâncias
```

## 🚀 Instalação e Configuração

### Pré-requisitos

```bash
python >= 3.7
numpy >= 1.19.0
```

### Instalação

1. **Clone/baixe o projeto:**
```bash
git clone <repository-url>
cd qbf_tabu_search
```

2. **Instale dependências:**
```bash
pip install -r requirements.txt
```

3. **Verifique a instalação:**
```bash
python -c "import qbf_tabu_search; print('Framework instalado com sucesso!')"
```

## 📖 Uso Básico

### Interface de Linha de Comando

```bash
# Execução básica
python main.py --instance instances/qbf060 --tenure 20 --iterations 1000

# Busca Tabu avançada
python main.py --instance instances/qbf200 --enhanced --best-improvement --diversification

# Processamento em lote
python main.py --batch instances/ --output results/batch_results.csv

# Análise de instância
python main.py --analyze --instance instances/qbf060
```

### Uso Programático

```python
# Importação básica
from qbf_tabu_search import TS_QBF, TabuSearchConfig

# Configuração simples
ts = TS_QBF(tenure=20, iterations=1000, filename="instances/qbf060")
best_solution = ts.solve()
print(f"Melhor solução: {best_solution}")

# Configuração avançada
from qbf_tabu_search.problems.qbf.ts_qbf import TS_QBF_Enhanced
from qbf_tabu_search.core.abstract_ts import TabuSearchConfig

config = TabuSearchConfig(
    tenure=25,
    iterations=2000,
    seed=42,
    verbose=True,
    diversification_enabled=True,
    intensification_enabled=True
)

ts_enhanced = TS_QBF_Enhanced(config, "instances/qbf200")
ts_enhanced.set_search_strategy(best_improvement=True)
best_solution = ts_enhanced.solve()
```

## 🧩 Módulos Principais

### Core (`core/`)

**`solution.py`** - Classe Solution
```python
from qbf_tabu_search.core.solution import Solution

sol = Solution()
sol.add(5)
sol.add(10)
print(f"Solução tem {sol.size()} elementos: {sol.get_elements()}")
```

**`evaluator.py`** - Interface para avaliadores
```python
from qbf_tabu_search.core.evaluator import Evaluator

# Implementar avaliador customizado
class MyEvaluator(Evaluator):
    def evaluate(self, solution):
        # Implementar lógica de avaliação
        pass
```

**`abstract_ts.py`** - Framework de Busca Tabu
```python
from qbf_tabu_search.core.abstract_ts import AbstractTS

# Implementar Busca Tabu customizada
class MyTabuSearch(AbstractTS):
    def neighborhood_move(self):
        # Implementar movimento de vizinhança
        pass
```

### Problems (`problems/qbf/`)

**`qbf.py`** - Avaliador QBF base
```python
from qbf_tabu_search.problems.qbf.qbf import QBF

qbf = QBF("instances/qbf060")
print(f"Tamanho do domínio: {qbf.get_domain_size()}")

# Avaliar solução
solution = Solution()
solution.add(0)
solution.add(5)
cost = qbf.evaluate(solution)
```

**`qbf_inverse.py`** - Variações da QBF
```python
from qbf_tabu_search.problems.qbf.qbf_inverse import QBF_Inverse, QBF_Scaled

# QBF invertida (para minimização)
qbf_inv = QBF_Inverse("instances/qbf060")

# QBF com escala
qbf_scaled = QBF_Scaled("instances/qbf060", scale_factor=2.0)
```

**`ts_qbf.py`** - Busca Tabu para QBF
```python
from qbf_tabu_search.problems.qbf.ts_qbf import TS_QBF, TS_QBF_Enhanced

# Busca Tabu básica
ts_basic = TS_QBF(tenure=20, iterations=1000, filename="instances/qbf060")

# Busca Tabu avançada
ts_advanced = TS_QBF_Enhanced(config, "instances/qbf060")
ts_advanced.set_search_strategy(best_improvement=True)
```

### Utils (`utils/`)

**`file_io.py`** - Entrada/saída de arquivos
```python
from qbf_tabu_search.utils.file_io import QBFFileReader, SolutionFileHandler

# Ler instância QBF
size, matrix = QBFFileReader.read_qbf_instance("instances/qbf060")

# Salvar solução
SolutionFileHandler.write_solution_json("solution.json", solution)
```

**`validation.py`** - Validação
```python
from qbf_tabu_search.utils.validation import QBFValidator

validator = QBFValidator()
if validator.validate_file("instances/qbf060"):
    print("Instância válida!")
```

**`analysis.py`** - Análise de instâncias
```python
from qbf_tabu_search.utils.analysis import QBFAnalyzer

analyzer = QBFAnalyzer("instances/qbf060")
analysis = analyzer.get_comprehensive_analysis()
print(f"Estatísticas: {analysis['basic_stats']}")
```

## 🔧 Opções de Configuração

### Parâmetros da Busca Tabu

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `tenure` | int | 20 | Tamanho da lista tabu |
| `iterations` | int | 1000 | Número máximo de iterações |
| `seed` | int | 0 | Semente aleatória |
| `verbose` | bool | True | Saída detalhada |

### Estratégias Avançadas

| Estratégia | Descrição |
|------------|-----------|
| `best_improvement` | Usa melhor movimento vs. primeiro movimento |
| `diversification` | Reinicialização para diversificação |
| `intensification` | Foco na região da melhor solução |
| `aspiration` | Critério de aspiração ativo |

## 📊 Exemplos de Análise

### Análise de Instância
```python
from qbf_tabu_search.utils.analysis import QBFAnalyzer

analyzer = QBFAnalyzer("instances/qbf200")

# Estatísticas básicas
stats = analyzer.get_basic_statistics()
print(f"Tamanho: {stats['size']}, Esparsidade: {stats['sparsity']:.1f}%")

# Análise de paisagem
landscape = analyzer.get_landscape_analysis()
print(f"Rugosidade estimada: {landscape['ruggedness_estimate']:.3f}")
```

### Análise de Performance
```python
from qbf_tabu_search.utils.analysis import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()

# Adicionar resultados de múltiplas execuções
for result in experimental_results:
    analyzer.add_result(result)

# Analisar sensibilidade a parâmetros
sensitivity = analyzer.analyze_parameter_sensitivity(results, 'tenure')
print(f"Melhor tenure: {sensitivity['trends']['best_parameter_value']}")
```

## 🧪 Testes

```bash
# Executar todos os testes
python -m pytest tests/

# Testes específicos
python -m pytest tests/test_core.py
python -m pytest tests/test_qbf.py -v

# Cobertura de testes
python -m pytest tests/ --cov=qbf_tabu_search
```

## 📈 Experimentos

### Exemplo Completo de Experimento
```python
#!/usr/bin/env python3
"""
Exemplo de experimento comparativo
"""

from qbf_tabu_search.core.abstract_ts import TabuSearchConfig
from qbf_tabu_search.problems.qbf.ts_qbf import TS_QBF, TS_QBF_Enhanced
from qbf_tabu_search.utils.file_io import ResultsFileHandler
import time

def run_experiment():
    instances = ["instances/qbf060", "instances/qbf200"]
    tenures = [10, 20, 30]
    algorithms = ['basic', 'enhanced']
    
    results = []
    
    for instance in instances:
        for tenure in tenures:
            for algorithm in algorithms:
                for run in range(5):  # 5 execuções independentes
                    
                    config = TabuSearchConfig(
                        tenure=tenure,
                        iterations=1000,
                        seed=run,
                        verbose=False
                    )
                    
                    start_time = time.time()
                    
                    if algorithm == 'basic':
                        ts = TS_QBF(tenure, 1000, instance, run)
                    else:
                        ts = TS_QBF_Enhanced(config, instance)
                    
                    solution = ts.solve()
                    
                    results.append({
                        'instance': instance,
                        'algorithm': algorithm,
                        'tenure': tenure,
                        'run': run,
                        'best_cost': solution.cost,
                        'solution_size': solution.size(),
                        'execution_time': time.time() - start_time
                    })
                    
                    print(f"Completed: {instance} - {algorithm} - tenure={tenure} - run={run}")
    
    # Salvar resultados
    ResultsFileHandler.write_results_csv("experiment_results.csv", results)
    print(f"Experimento concluído! {len(results)} execuções salvas.")

if __name__ == "__main__":
    run_experiment()
```

## 🎯 Implementação das Estratégias Requeridas

O framework está preparado para implementar as estratégias tabu alternativas da Atividade 3:

### 1. Probabilistic TS
```python
class ProbabilisticTS(TS_QBF_Enhanced):
    def neighborhood_move(self):
        # Implementar seleção probabilística baseada em custos
        # ao invés de seleção determinística do melhor movimento
        pass
```

### 2. Intensification by Restart
```python
class IntensificationRestartTS(TS_QBF_Enhanced):
    def solve(self):
        # Implementar reinicialização periódica da melhor solução
        # para intensificação da busca
        pass
```

### 3. Intensification by Neighborhood
```python
class IntensificationNeighborhoodTS(TS_QBF_Enhanced):
    def neighborhood_move(self):
        # Implementar expansão da vizinhança em regiões promissoras
        pass
```

### 4. Diversification by Restart
```python
class DiversificationRestartTS(TS_QBF_Enhanced):
    def solve(self):
        # Implementar reinicialização aleatória para diversificação
        # quando detectar estagnação
        pass
```

### 5. Strategic Oscillation
```python
class StrategicOscillationTS(TS_QBF_Enhanced):
    def solve(self):
        # Implementar oscilação entre diferentes estratégias
        # (ex: alternar entre intensificação e diversificação)
        pass
```

### 6. Surrogate Objective
```python
class SurrogateObjectiveTS(TS_QBF_Enhanced):
    def __init__(self, config, filename):
        super().__init__(config, filename)
        # Implementar função objetivo substituta
        self.surrogate_evaluator = self._create_surrogate()
```

## 📋 Checklist da Atividade 3

### ✅ Requisitos Implementados

- [x] **Framework Base**: Conversão completa Java → Python
- [x] **Estrutura Modular**: Organização em módulos especializados
- [x] **Busca Tabu Padrão**: Implementação TS_QBF funcional
- [x] **Configuração Flexível**: TabuSearchConfig para parametrização
- [x] **Interface CLI**: Script main.py com opções avançadas
- [x] **Utilitários**: Validação, análise, I/O de arquivos
- [x] **Documentação**: README completo e docstrings

### 🔲 Requisitos a Implementar

- [ ] **Estratégia Alternativa 1**: (escolher entre as 6 opções)
- [ ] **Estratégia Alternativa 2**: (escolher entre as 6 opções)
- [ ] **Experimentos**: Configurações de teste conforme especificado
- [ ] **Relatório**: Documento de ~5 páginas com resultados

### 📝 Configurações de Teste Sugeridas

Conforme a atividade, implementar:

1. **PADRÃO**: TS com first-improving, tenure=T1, estratégia padrão
2. **PADRÃO+BEST**: TS PADRÃO com best-improving
3. **PADRÃO+TENURE**: TS PADRÃO com tenure=T2
4. **PADRÃO+METHOD1**: TS PADRÃO com estratégia alternativa 1
5. **PADRÃO+METHOD2**: TS PADRÃO com estratégia alternativa 2

## 🔍 Troubleshooting

### Problemas Comuns

**ImportError: No module named 'qbf_tabu_search'**
```bash
# Certifique-se de estar no diretório correto
cd qbf_tabu_search
python -c "import sys; print(sys.path)"

# Ou adicione ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**FileNotFoundError: Instância não encontrada**
```bash
# Verifique se as instâncias estão no lugar correto
ls instances/
# Ou use caminho absoluto
python main.py --instance /path/to/qbf060
```

**Erro de permissão ao salvar resultados**
```bash
# Crie diretórios necessários
mkdir -p results solutions logs
chmod 755 results solutions logs
```

### Validação da Instalação
```python
from qbf_tabu_search.utils.validation import validate_framework_installation

validation_result = validate_framework_installation()
if validation_result['valid']:
    print("✅ Framework instalado corretamente!")
else:
    print("❌ Problemas na instalação:")
    for error in validation_result['errors']:
        print(f"  - {error}")
```

## 🤝 Contribuição

### Estrutura para Novas Funcionalidades

1. **Novo Problema**: Adicionar em `problems/new_problem/`
2. **Nova Metaheurística**: Estender `core/abstract_ts.py`
3. **Novos Utilitários**: Adicionar em `utils/`
4. **Novos Testes**: Adicionar em `tests/`

### Padrões de Código

- **Docstrings**: Usar formato Google/NumPy
- **Type Hints**: Usar tipagem quando possível
- **Imports**: Seguir PEP 8 (stdlib, terceiros, locais)
- **Nomenclatura**: snake_case para variáveis, PascalCase para classes

## 📚 Referências

1. **Tabu Search**: Gendreau, M. & Potvin, J.-Y. (eds.), Handbook of Metaheuristics
2. **QBF**: Kochenberger, et al. The unconstrained binary quadratic programming problem: a survey. J Comb Optim (2014)
3. **Framework Original**: Implementação Java dos professores ccavellucci e fusberti

## 📄 Licença

Este código é uma adaptação para fins educacionais da disciplina MO824/MC859 - Tópicos em Otimização Combinatória, UNICAMP.

**Autores originais (Java)**: ccavellucci, fusberti  
**Conversão Python**: Para atividade acadêmica  
**Versão**: 1.0.0

---

**Nota**: Esta estrutura modular facilita a implementação das estratégias alternativas requeridas na Atividade 3. Cada estratégia pode ser implementada como uma subclasse de `TS_QBF_Enhanced`, mantendo o código organizado e reutilizável.