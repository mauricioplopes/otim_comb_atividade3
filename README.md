# Tabu Search para Função Binária Quadrática (QBF)

Este repositório contém uma implementação em Python do algoritmo **Tabu Search** para resolver o problema de maximização de uma **Função Binária Quadrática (QBF)**. O código foi convertido de uma implementação original em Java, mantendo todas as funcionalidades e estruturas do algoritmo original.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Problema QBF](#problema-qbf)
- [Características da Implementação](#características-da-implementação)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Formato das Instâncias](#formato-das-instâncias)
- [Exemplos](#exemplos)
- [Parâmetros](#parâmetros)
- [Estrutura do Código](#estrutura-do-código)
- [Resultados Esperados](#resultados-esperados)
- [Troubleshooting](#troubleshooting)
- [Contribuição](#contribuição)

## 🎯 Sobre o Projeto

Este projeto implementa o algoritmo **Tabu Search** para resolver o problema MAX-QBF (Maximização de Função Binária Quadrática). O Tabu Search é uma metaheurística que utiliza uma lista de movimentos proibidos (tabu) para evitar ciclagem e explorar eficientemente o espaço de soluções.

### Características Principais:
- ✅ Implementação fiel ao código Java original
- ✅ Heurística construtiva com lista restrita de candidatos (RCL)
- ✅ Movimentos de vizinhança: inserção, remoção e troca
- ✅ Lista tabu com critério de aspiração
- ✅ Avaliação incremental da função objetivo
- ✅ Modo debug para análise detalhada
- ✅ Tratamento robusto de erros

## 📊 Problema QBF

Uma **Função Binária Quadrática (QBF)** é definida como:


$$f(x) = x^T · A · x = Σᵢ Σⱼ aᵢⱼ · xᵢ · xⱼ$$


Onde:
- `x ∈ {0,1}ⁿ` é um vetor binário
- `A` é uma matriz n×n de coeficientes reais
- O objetivo é maximizar f(x)

O problema MAX-QBF é **NP-difícil**, tornando as metaheurísticas uma abordagem apropriada para instâncias de grande porte.

## 🔧 Características da Implementação

### Algoritmo Tabu Search
- **Heurística Construtiva**: Constrói solução inicial usando estratégia gulosa com RCL
- **Movimentos de Vizinhança**: 
  - Inserção de elementos
  - Remoção de elementos  
  - Troca de elementos (2-exchange)
- **Lista Tabu**: Evita movimentos recentes com tenure configurável
- **Critério de Aspiração**: Permite movimentos tabu se melhoram a melhor solução conhecida
- **Avaliação Incremental**: Cálculo eficiente do impacto dos movimentos

### Estrutura de Classes
- `Solution`: Representa uma solução (herda de list)
- `QBF`: Implementa a função objetivo e operações de avaliação
- `QBFInverse`: Versão inversa para uso com algoritmo de minimização
- `TabuSearch`: Implementação principal do algoritmo

## 💻 Instalação

### Pré-requisitos
- Python 3.7 ou superior
- Não requer bibliotecas externas (usa apenas bibliotecas padrão)

### Clone o repositório
```bash
git clone https://github.com/seu-usuario/tabu-search-qbf.git
cd tabu-search-qbf
```

## 🚀 Como Usar

### Uso Básico
```bash
python tabu_search.py <tenure> <iterations> <arquivo_instancia>
```

### Modo Debug (Recomendado para primeira execução)
```bash
python tabu_search.py <tenure> <iterations> <arquivo_instancia> debug
```

### Exemplos de Comando
```bash
# Execução padrão
python tabu_search.py 20 1000 instances/qbf200

# Modo debug
python tabu_search.py 20 1000 instances/qbf200 debug

# Instância menor para testes
python tabu_search.py 10 500 instances/qbf060 debug
```

## 📄 Formato das Instâncias

O arquivo de instância deve seguir o formato de **matriz triangular superior**:

```
n
a₁₁ a₁₂ a₁₃ ... a₁ₙ
a₂₂ a₂₃ ... a₂ₙ
a₃₃ ... a₃ₙ
...
aₙₙ
```

**Exemplo** (n=5):
```
5
9 0 -7 -1 -10
7 -8 2 -4
3 -9 9
10 -5
8
```

### Características do Formato:
- Primeira linha: dimensão da matriz (n)
- Próximas n linhas: elementos da matriz triangular superior
- Linha i contém (n-i+1) elementos: aᵢᵢ, aᵢ₍ᵢ₊₁₎, ..., aᵢₙ
- Elementos abaixo da diagonal são assumidos como zero

## 📝 Exemplos

### Exemplo 1: Execução Básica
```bash
$ python tabu_search.py 20 1000 instances/qbf060

(Iter. 15) BestSol = Solution: cost=[-245.0], size=[18], elements=[0, 1, 2, ...]
(Iter. 23) BestSol = Solution: cost=[-198.0], size=[15], elements=[1, 3, 5, ...]
maxVal = Solution: cost=[-156.0], size=[12], elements=[2, 4, 6, 8, 10, 12]
Time = 2.341 seg
```

### Exemplo 2: Modo Debug
```bash
$ python tabu_search.py 20 1000 instances/qbf060 debug

=== MODO DEBUG ===
Arquivo: instances/qbf060
Tenure: 20
Iterations: 1000
Tentando ler arquivo: instances/qbf060
Arquivo lido: 61 linhas
Dimensão da matriz: 60
Matriz inicializada com zeros
Linha 0: 60 elementos (esperado 60)
...
Matriz carregada com sucesso
Arquivo lido com sucesso!
=== Informações da Matriz ===
Size: 60
Matrix A is None: False
Matriz 60x60 inicializada
...
maxVal = Solution: cost=[-156.0], size=[12], elements=[2, 4, 6, 8, 10, 12]
Time = 2.341 seg
```

## ⚙️ Parâmetros

| Parâmetro | Descrição | Valores Sugeridos |
|-----------|-----------|-------------------|
| `tenure` | Tamanho da lista tabu | 10-50 (tipicamente 20) |
| `iterations` | Número de iterações | 500-5000 (tipicamente 1000) |
| `filename` | Arquivo da instância | Caminho para arquivo QBF |
| `debug` | Modo debug (opcional) | Adicione "debug" para informações detalhadas |

### Diretrizes para Parâmetros:
- **Tenure pequeno** (5-15): Mais diversificação, pode escapar de ótimos locais
- **Tenure grande** (30-50): Mais intensificação, busca mais refinada
- **Iterations**: Depende do tamanho da instância e tempo disponível

## 🏗️ Estrutura do Código

```
tabu_search.py
├── Solution              # Classe para representar soluções
├── QBF                   # Classe base para função objetivo
│   ├── _read_input()     # Leitura do arquivo de instância
│   ├── evaluate()        # Avaliação completa da solução
│   ├── evaluate_*_cost() # Avaliações incrementais
│   └── print_matrix_info() # Debug da matriz
├── QBFInverse           # Versão inversa para minimização
├── TabuSearch           # Algoritmo principal
│   ├── constructive_heuristic() # Construção de solução inicial
│   ├── neighborhood_move()      # Movimentos de vizinhança
│   └── solve()                  # Loop principal
└── main()               # Função principal
```

## 📈 Resultados Esperados

### Saída Típica:
- **cost**: Valor da função objetivo (negativo devido à inversão)
- **size**: Número de variáveis selecionadas (xᵢ = 1)
- **elements**: Índices das variáveis selecionadas
- **Time**: Tempo de execução em segundos

### Interpretação:
- Custos aparecem **negativos** devido ao uso de QBFInverse
- Para obter o valor real da maximização: `valor_real = -cost`
- Soluções maiores não necessariamente são melhores

## 🔍 Troubleshooting

### Problema: "Arquivo não encontrado"
**Solução**: Verifique o caminho do arquivo
```bash
# Windows
python tabu_search.py 20 1000 instances\qbf200
# Linux/Mac
python tabu_search.py 20 1000 instances/qbf200
```

### Problema: "Matriz não inicializada"
**Solução**: Use modo debug para diagnóstico
```bash
python tabu_search.py 20 1000 arquivo debug
```

### Problema: Arquivo com formato incorreto
**Solução**: Verifique se:
- Primeira linha contém apenas o número n
- Cada linha i tem (n-i+1) elementos
- Todos os valores são números

### Problema: Performance lenta
**Soluções**:
- Reduza o número de iterações
- Use instâncias menores para teste
- Verifique se não está em modo debug

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Áreas para Contribuição:
- Implementação de estratégias tabu alternativas
- Otimizações de performance
- Melhorias na interface
- Documentação adicional
- Testes unitários

## 📚 Referências

1. **Gendreau, M., & Potvin, J. Y.** (2010). *Handbook of metaheuristics* (Vol. 2). Springer.
2. **Kochenberger, G., et al.** (2014). The unconstrained binary quadratic programming problem: a survey. *Journal of Combinatorial Optimization*, 28(1), 58-81.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 📞 Contato

Para dúvidas ou sugestões, abra uma [issue](https://github.com/seu-usuario/tabu-search-qbf/issues) no repositório.

**Desenvolvido como parte do curso MO824/MC859 - Tópicos em Otimização Combinatória**