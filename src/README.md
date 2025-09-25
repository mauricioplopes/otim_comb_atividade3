# Sistema Tabu Search - MAX-SC-QBF

O sistema implementa diferentes estratégias de Tabu Search conforme solicitado na Atividade 3.

## Implementações Disponíveis

### 1. PADRÃO
- **Método**: First-improving
- **Tenure**: T1
- **Estratégia**: Tabu padrão

### 2. PADRÃO+BEST 
- **Método**: Best-improving
- **Tenure**: T1 
- **Estratégia**: Tabu padrão

### 3. PADRÃO+TENURE
- **Método**: First-improving
- **Tenure**: T2
- **Estratégia**: Tabu padrão

### 4. PADRÃO+PROBABILISTIC TS 
- **Método**: Best-improving
- **Tenure**: T1 
- **Estratégia**: Probabilistic TS

### 5. PADRÃO+INTENSIFICATION BT NEIGHBORHOOD
- **Método**: First-improving (mesmo do padrão)
- **Tenure**: T1
- **Estratégia**: Intensification by Neighborhood

## Sintaxe

```bash
python main.py <tenure> <iterations> <filename> [options]
```

## Parâmetros

- **tenure**: Tamanho da lista tabu (T1 para padrão, T2 para item 3)
- **iterations**: Número de iterações
- **filename**: Arquivo da instância MAX-SC-QBF

## Opções

- `method=X`: Escolhe o método/estratégia
  - `best-improving`: Item 2 - Best-improving padrão
  - `first-improving`: Items 1,3 - First-improving padrão  
  - `probabilistic`: Item 4 - Probabilistic TS (METHOD1)
  - `intensification`: Item 5 - Intensification by Neighborhood (METHOD2)
- `alpha=X`: Parâmetro alpha para Probabilistic TS (padrão: 2.0)
- `elite=X`: Tamanho da elite list para Intensification (padrão: 5)
- `period=X`: Período de intensificação em iterações (padrão: 50)
- `debug`: Informações detalhadas de debug
- `quiet`: Saída mínima
- `seed=N`: Seed aleatória

## Exemplos de Uso por Item

### Item 1: PADRÃO (First-Improving + T1)
```bash
python main.py 20 1000 instances/qbf_sc/instance-01.txt method=first-improving
```

### Item 2: PADRÃO+BEST (Best-Improving + T1)
```bash
python main.py 20 1000 instances/qbf_sc/instance-01.txt method=best-improving
```

### Item 3: PADRÃO+TENURE (First-Improving + T2)
```bash
python main.py 50 1000 instances/qbf_sc/instance-01.txt method=first-improving
```

### Item 4: PADRÃO+METHOD1 (Probabilistic TS + T1)
```bash
python main.py 20 1000 instances/qbf_sc/instance-01.txt method=probabilistic

# Com alpha customizado
python main.py 20 1000 instances/qbf_sc/instance-01.txt method=probabilistic alpha=1.5
```

### Item 5: PADRÃO+METHOD2 (Intensification by Neighborhood + T1)
```bash
python main.py 20 1000 instances/qbf_sc/instance-01.txt method=intensification

# Com parâmetros customizados
python main.py 20 1000 instances/qbf_sc/instance-01.txt method=intensification elite=8 period=30
```


## Resumo dos 5 Items Implementados

| Item | Nome | Método Busca | Tenure | Estratégia Tabu | Comando |
|------|------|-------------|--------|----------------|---------|
| **1** | PADRÃO | First-improving | T1 | Padrão | `method=first-improving` |
| **2** | PADRÃO+BEST | Best-improving | T1 | Padrão | `method=best-improving` |
| **3** | PADRÃO+TENURE | First-improving | T2 | Padrão | T2 diferente de T1 |
| **4** | PADRÃO+METHOD1 | First-improving | T1 | **Probabilistic** | `method=probabilistic` |
| **5** | PADRÃO+METHOD2 | First-improving | T1 | **Intensification** | `method=intensification` |
