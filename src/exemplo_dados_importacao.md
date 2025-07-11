# 📋 Exemplos de Dados para Importação

## 🎯 Funcionalidade Automática

Após importar os dados, o app **automaticamente adiciona os ativos à sua carteira** baseado nas transações importadas. Isso significa que:

- ✅ Ativos com transações de compra/venda são adicionados automaticamente
- ✅ Quantidades e preços médios são calculados automaticamente
- ✅ Não precisa cadastrar manualmente cada ativo
- ✅ A carteira é atualizada imediatamente após a importação

## 📄 Formato CSV

### 1. assets.csv - Ativos
```csv
id,name,type
1,PETR4,Ação
2,MXRF11,FII
3,VALE3,Ação
4,HGLG11,FII
5,ITUB4,Ação
```

### 2. transactions.csv - Transações
```csv
id,asset_id,transaction_type,quantity,price,transaction_date
1,1,compra,100,25.00,2023-01-15
2,1,venda,50,26.50,2023-02-20
3,2,compra,200,10.00,2022-11-20
4,3,compra,150,65.30,2023-03-10
5,4,compra,100,120.50,2023-01-05
6,5,compra,80,32.15,2023-02-28
```

### 3. price_history.csv - Histórico de Preços
```csv
id,asset_id,price,record_date
1,1,25.50,2023-01-15
2,1,26.00,2023-01-16
3,1,25.80,2023-01-17
4,2,10.10,2022-11-20
5,2,10.20,2022-11-21
6,3,65.30,2023-03-10
7,3,66.15,2023-03-11
8,4,120.50,2023-01-05
9,4,121.20,2023-01-06
10,5,32.15,2023-02-28
11,5,32.80,2023-03-01
```

### 4. dividends.csv - Dividendos
```csv
id,asset_id,dividend_value,payment_date
1,1,0.50,2023-02-01
2,1,0.45,2023-05-01
3,2,0.10,2023-01-10
4,2,0.12,2023-02-10
5,3,1.20,2023-04-15
6,4,0.85,2023-01-20
7,5,0.30,2023-03-15
```

## 📋 Formato JSON

### arquivo_completo.json
```json
{
  "assets": [
    {"id": 1, "name": "PETR4", "type": "Ação"},
    {"id": 2, "name": "MXRF11", "type": "FII"},
    {"id": 3, "name": "VALE3", "type": "Ação"},
    {"id": 4, "name": "HGLG11", "type": "FII"},
    {"id": 5, "name": "ITUB4", "type": "Ação"}
  ],
  "transactions": [
    {"id": 1, "asset_id": 1, "transaction_type": "compra", "quantity": 100, "price": 25.00, "transaction_date": "2023-01-15"},
    {"id": 2, "asset_id": 1, "transaction_type": "venda", "quantity": 50, "price": 26.50, "transaction_date": "2023-02-20"},
    {"id": 3, "asset_id": 2, "transaction_type": "compra", "quantity": 200, "price": 10.00, "transaction_date": "2022-11-20"},
    {"id": 4, "asset_id": 3, "transaction_type": "compra", "quantity": 150, "price": 65.30, "transaction_date": "2023-03-10"},
    {"id": 5, "asset_id": 4, "transaction_type": "compra", "quantity": 100, "price": 120.50, "transaction_date": "2023-01-05"},
    {"id": 6, "asset_id": 5, "transaction_type": "compra", "quantity": 80, "price": 32.15, "transaction_date": "2023-02-28"}
  ],
  "price_history": [
    {"id": 1, "asset_id": 1, "price": 25.50, "record_date": "2023-01-15"},
    {"id": 2, "asset_id": 1, "price": 26.00, "record_date": "2023-01-16"},
    {"id": 3, "asset_id": 1, "price": 25.80, "record_date": "2023-01-17"},
    {"id": 4, "asset_id": 2, "price": 10.10, "record_date": "2022-11-20"},
    {"id": 5, "asset_id": 2, "price": 10.20, "record_date": "2022-11-21"},
    {"id": 6, "asset_id": 3, "price": 65.30, "record_date": "2023-03-10"},
    {"id": 7, "asset_id": 3, "price": 66.15, "record_date": "2023-03-11"},
    {"id": 8, "asset_id": 4, "price": 120.50, "record_date": "2023-01-05"},
    {"id": 9, "asset_id": 4, "price": 121.20, "record_date": "2023-01-06"},
    {"id": 10, "asset_id": 5, "price": 32.15, "record_date": "2023-02-28"},
    {"id": 11, "asset_id": 5, "price": 32.80, "record_date": "2023-03-01"}
  ],
  "dividends": [
    {"id": 1, "asset_id": 1, "dividend_value": 0.50, "payment_date": "2023-02-01"},
    {"id": 2, "asset_id": 1, "dividend_value": 0.45, "payment_date": "2023-05-01"},
    {"id": 3, "asset_id": 2, "dividend_value": 0.10, "payment_date": "2023-01-10"},
    {"id": 4, "asset_id": 2, "dividend_value": 0.12, "payment_date": "2023-02-10"},
    {"id": 5, "asset_id": 3, "dividend_value": 1.20, "payment_date": "2023-04-15"},
    {"id": 6, "asset_id": 4, "dividend_value": 0.85, "payment_date": "2023-01-20"},
    {"id": 7, "asset_id": 5, "dividend_value": 0.30, "payment_date": "2023-03-15"}
  ],
  "alerts": [
    {"id": 1, "asset_id": 1, "alert_type": "price_target", "target_value": 27.00, "percentage_change": null, "is_active": 1},
    {"id": 2, "asset_id": 2, "alert_type": "percentage_change", "target_value": null, "percentage_change": 5.0, "is_active": 1},
    {"id": 3, "asset_id": 3, "alert_type": "price_target", "target_value": 70.00, "percentage_change": null, "is_active": 1}
  ],
  "events": [
    {"id": 1, "event_date": "2023-02-10", "event_type": "dividendo", "description": "Pagamento de dividendos PETR4", "asset_id": 1},
    {"id": 2, "event_date": "2023-01-15", "event_type": "vencimento", "description": "Vencimento de opções MXRF11", "asset_id": 2},
    {"id": 3, "event_date": "2023-04-20", "event_type": "assembléia", "description": "Assembleia Geral VALE3", "asset_id": 3}
  ]
}
```

## 📋 Formato da Carteira de Investimentos

### 🎯 Estrutura Básica
A carteira deve conter **transações de compra e venda** que definem sua posição atual:

```
Exemplo de carteira:
- PETR4: 100 ações compradas a R$ 25,00
- MXRF11: 200 cotas compradas a R$ 10,00
- VALE3: 150 ações compradas a R$ 65,30
```

### 📊 Como o App Calcula sua Carteira

#### 🧮 Cálculo de Preço Médio:
```
Fórmula: Preço Médio = Valor Total Investido ÷ Quantidade Total

Exemplo:
- Compra 1: 100 ações a R$ 25,00 = R$ 2.500
- Compra 2: 50 ações a R$ 26,00 = R$ 1.300
- Venda: 30 ações a R$ 27,50 = -R$ 825

Valor Total Investido: 2.500 + 1.300 - 825 = R$ 2.975
Quantidade Total: 100 + 50 - 30 = 120 ações
Preço Médio: 2.975 ÷ 120 = R$ 24,79
```

#### 📈 Processo de Cálculo:
1. **Soma Compras**: Adiciona todas as compras (quantidade × preço)
2. **Subtrai Vendas**: Remove vendas do valor total (quantidade × preço)
3. **Calcula Quantidade**: Soma compras e subtrai vendas
4. **Preço Médio**: Valor total ÷ quantidade total
5. **Adição Automática**: Ativos com posição > 0 são adicionados à carteira

### 📝 Regras Importantes

#### ✅ Formato de Datas
- **Sempre use**: YYYY-MM-DD
- **Exemplos corretos**: 2023-01-15, 2023-12-31
- **Exemplos incorretos**: 15/01/2023, 2023-1-5

#### ✅ Formato de Números
- **Decimais**: Use ponto (.) como separador
- **Exemplos corretos**: 25.50, 100.00, 0.50
- **Exemplos incorretos**: 25,50, 100,00

#### ✅ Tipos de Transação
- **Valores válidos**: "compra", "venda"
- **Case sensitive**: Use exatamente essas palavras

#### ✅ Tipos de Ativo
- **Valores válidos**: "Ação", "FII", "ETF", "Tesouro", "CDB"
- **Case sensitive**: Use exatamente essas palavras

#### ✅ Quantidades e Preços
- **Quantidades**: Números positivos (ex: 100, 50.5)
- **Preços**: Use ponto como separador decimal (ex: 25.50)
- **Valores monetários**: Sem símbolo de moeda (ex: 25.50, não R$ 25.50)

#### ✅ Relacionamentos
- **asset_id**: Deve corresponder ao id do ativo na tabela assets
- **Integridade**: Todos os asset_id devem existir na tabela assets

### 🎯 Exemplos Detalhados de Carteira

#### 📊 Exemplo 1: Carteira Simples (Apenas Compras)
```
DADOS DE ENTRADA:
assets.csv:
id,name,type
1,PETR4,Ação
2,MXRF11,FII
3,VALE3,Ação

transactions.csv:
id,asset_id,transaction_type,quantity,price,transaction_date
1,1,compra,100,25.00,2023-01-15
2,2,compra,200,10.00,2022-11-20
3,3,compra,150,65.30,2023-03-10

RESULTADO APÓS IMPORTAÇÃO:
✅ PETR4: 100 ações, preço médio R$ 25,00
✅ MXRF11: 200 cotas, preço médio R$ 10,00
✅ VALE3: 150 ações, preço médio R$ 65,30
```

#### 📊 Exemplo 2: Carteira com Compras e Vendas
```
DADOS DE ENTRADA:
assets.csv:
id,name,type
1,PETR4,Ação
2,MXRF11,FII

transactions.csv:
id,asset_id,transaction_type,quantity,price,transaction_date
1,1,compra,100,25.00,2023-01-15
2,1,compra,50,26.00,2023-02-10
3,1,venda,30,27.50,2023-03-15
4,2,compra,200,10.00,2022-11-20
5,2,compra,100,10.50,2023-01-05

CÁLCULO:
PETR4: (100 × 25.00) + (50 × 26.00) - (30 × 27.50) = 2.500 + 1.300 - 825 = 2.975
Quantidade: 100 + 50 - 30 = 120 ações
Preço médio: 2.975 ÷ 120 = R$ 24,79

RESULTADO APÓS IMPORTAÇÃO:
✅ PETR4: 120 ações, preço médio R$ 24,79
✅ MXRF11: 300 cotas, preço médio R$ 10,17
```

#### 📊 Exemplo 3: Carteira com Múltiplas Operações
```
DADOS DE ENTRADA:
assets.csv:
id,name,type
1,PETR4,Ação
2,MXRF11,FII
3,VALE3,Ação

transactions.csv:
id,asset_id,transaction_type,quantity,price,transaction_date
1,1,compra,100,25.00,2023-01-15
2,1,compra,50,26.00,2023-02-10
3,1,venda,30,27.50,2023-03-15
4,1,compra,25,24.50,2023-04-20
5,2,compra,200,10.00,2022-11-20
6,2,venda,50,11.00,2023-02-15
7,3,compra,150,65.30,2023-03-10
8,3,compra,75,66.00,2023-04-05

RESULTADO APÓS IMPORTAÇÃO:
✅ PETR4: 145 ações (100+50-30+25), preço médio R$ 25,14
✅ MXRF11: 150 cotas (200-50), preço médio R$ 10,00
✅ VALE3: 225 ações (150+75), preço médio R$ 65,53
```

## ⚠️ Dicas para Evitar Erros

1. **Verifique os IDs**: Certifique-se de que os `asset_id` nas transações, preços e dividendos correspondem aos IDs dos ativos
2. **Datas válidas**: Use apenas datas válidas no formato YYYY-MM-DD
3. **Encoding**: Salve os arquivos em UTF-8
4. **Headers**: Inclua sempre a linha de cabeçalho nos arquivos CSV
5. **Valores nulos**: Use `null` no JSON ou deixe vazio no CSV para valores nulos

## 📋 Formato JSON Simplificado (Carteira)

Para importação rápida da carteira atual, o app também aceita um formato JSON simplificado:

### 🎯 Estrutura do Formato Simplificado

```json
[
  {
    "asset_id": "PETR4",
    "current_quantity": 100,
    "average_price": 25.50
  },
  {
    "asset_id": "MXRF11", 
    "current_quantity": 200,
    "average_price": 10.00
  },
  {
    "asset_id": "KNCR11",
    "current_quantity": 6,
    "average_price": 104.12
  }
]
```

### ✅ Vantagens do Formato Simplificado

- **Mais fácil de criar**: Apenas os dados essenciais da carteira
- **Migração rápida**: Ideal para importar de outros sistemas
- **Criação automática**: O app cria automaticamente os ativos e transações
- **Menos complexidade**: Não precisa definir IDs ou relacionamentos

### 📝 Regras do Formato Simplificado

#### ✅ Campos Obrigatórios
- **asset_id**: Nome/ticker do ativo (ex: "PETR4", "MXRF11")
- **current_quantity**: Quantidade atual na carteira (número positivo)
- **average_price**: Preço médio de compra (use ponto como separador decimal)

#### ✅ Exemplo de Uso
```json
[
  {
    "asset_id": "PETR4",
    "current_quantity": 100,
    "average_price": 25.50
  },
  {
    "asset_id": "RECT11",
    "current_quantity": 17,
    "average_price": 38.39
  },
  {
    "asset_id": "KNCR11", 
    "current_quantity": 6,
    "average_price": 104.12
  }
]
```

#### 🔄 O que o App Faz Automaticamente

1. **Cria o ativo**: Se não existir, cria o ativo com tipo "Ação" por padrão
2. **Adiciona transação**: Cria uma transação de compra com a quantidade e preço médio
3. **Adiciona ao histórico**: Registra o preço atual no histórico de preços
4. **Adiciona à carteira**: Inclui automaticamente na carteira atual

#### 📊 Resultado da Importação

Após importar o exemplo acima, você terá:
- ✅ PETR4: 100 ações, preço médio R$ 25,50
- ✅ RECT11: 17 cotas, preço médio R$ 38,39  
- ✅ KNCR11: 6 cotas, preço médio R$ 104,12

### 🎯 Quando Usar Cada Formato

#### 📋 Formato Completo (Recomendado para)
- ✅ Backup completo do sistema
- ✅ Migração entre instalações do app
- ✅ Dados históricos detalhados
- ✅ Transações individuais

#### 📋 Formato Simplificado (Recomendado para)
- ✅ Importação rápida da carteira atual
- ✅ Migração de outros sistemas
- ✅ Dados apenas da posição atual
- ✅ Criação manual simples 