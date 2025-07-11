# 📊 App de Controle e Automação de Carteira de Investimentos

## 🎯 Visão Geral

Aplicação desktop desenvolvida em Python para controle e automação de carteira de investimentos. Permite cadastro de ativos, acompanhamento de cotações em tempo real, geração de relatórios, análise de risco e projeções financeiras.

## ✨ Funcionalidades Principais

### 📈 Gestão de Ativos

- **Cadastro de Ativos**: Adicione ações, FIIs, ETFs e outros ativos
- **Transações**: Registre compras e vendas com histórico completo
- **Preços em Tempo Real**: Integração com Yahoo Finance
- **Cálculo Automático**: Preço médio, rentabilidade e valor atual

### 📊 Análise e Relatórios

- **Relatórios Excel/PDF**: Relatórios detalhados da carteira
- **Análise de Risco**: Volatilidade e Beta dos ativos
- **Comparação com Benchmark**: Compare performance com Ibovespa
- **Projeções**: Simulações de Monte Carlo e projeções lineares

### 🔔 Alertas e Automação

- **Alertas de Preço**: Configure alertas para preços específicos
- **Alertas de Variação**: Monitore variações percentuais
- **Atualização Automática**: Cotações atualizadas em background
- **Calendário de Eventos**: Gerencie dividendos e vencimentos

### 💾 Backup e Exportação

- **Backup Automático**: Cópias de segurança do banco de dados
- **Exportação CSV/JSON**: Dados portáveis
- **Importação de Dados**: Restaure dados de arquivos externos

## 🏗️ Arquitetura

### Princípios Aplicados

- **SOLID**: Single Responsibility, Open/Closed, Dependency Inversion
- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **Clean Code**: Código limpo e legível

### Estrutura Modular

```
src/
├── main.py                 # Aplicação principal
├── config.py              # Configurações centralizadas
├── database_manager.py    # Gerenciamento de banco de dados
├── asset_registration.py  # Cadastro de ativos
├── yfinance_integration.py # Integração com Yahoo Finance
├── report_generator.py    # Geração de relatórios
├── plot_manager.py        # Gráficos e visualizações
├── risk_analysis.py       # Análise de risco
├── projection_simulation.py # Projeções e simulações
├── alert_manager.py       # Sistema de alertas
├── event_calendar.py      # Calendário de eventos
├── logger.py              # Sistema de logging
└── test_main.py          # Testes unitários
```

### Classes Principais

- **`InvestmentCarteiraApp`**: Orquestração geral da aplicação
- **`CarteiraDataManager`**: Gestão de dados da carteira
- **`UIManager`**: Interface do usuário
- **`ThemeManager`**: Gerenciamento de temas
- **`BackgroundTaskManager`**: Tarefas em segundo plano
- **`DateFormatter`**: Utilitário de formatação de datas

## 🚀 Instalação e Uso

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. **Clone o repositório**

```bash
git clone https://github.com/seu-usuario/investment_app.git
cd investment_app
```

2. **Instale as dependências**

```bash
pip install -r requirements.txt
```

3. **Execute a aplicação**

```bash
python src/main.py
```

### Configuração Inicial

1. **Primeiro Uso**: A aplicação criará automaticamente o banco de dados
2. **Cadastro de Ativos**: Use "Cadastrar Ativo" para adicionar seus investimentos
3. **Atualização de Cotações**: Clique em "Atualizar Cotações" para buscar preços atuais
4. **Geração de Relatórios**: Use "Gerar Relatório" para criar relatórios Excel/PDF

## 📊 Tipos de Ativos Suportados

### ✅ Ativos com Cotação Automática

O app integra com Yahoo Finance para atualização automática de preços:

#### **Ações**

- **Brasileiras**: PETR4, VALE3, ITUB4, BBDC4
- **Estrangeiras**: AAPL, MSFT, GOOGL, TSLA
- **Funcionalidades**: Cotação automática, análise de risco, comparação com benchmark

#### **FIIs (Fundos Imobiliários)**

- **Exemplos**: MXRF11, HGLG11, XPML11, VISC11
- **Funcionalidades**: Cotação automática, controle de dividendos, análise de rentabilidade

#### **ETFs (Fundos de Índice)**

- **Exemplos**: BOVA11, SMAL11, IVVB11, HASH11
- **Funcionalidades**: Cotação automática, comparação com índices, análise de volatilidade

### ⚠️ Ativos com Cadastro Manual

#### **Tesouro Direto**

- **Exemplos**: SELIC, IPCA, IGPM, Prefixado
- **Funcionalidades**: Controle de posições, cálculo de rentabilidade
- **Limitação**: Sem cotação automática (inserir preços manualmente)

#### **Outros Ativos**

- **Exemplos**: CDBs, LCIs, LCAs, ações estrangeiras
- **Funcionalidades**: Controle de posições, cálculo de rentabilidade
- **Flexibilidade**: Qualquer tipo de ativo pode ser cadastrado

### 📈 Funcionalidades por Tipo

| Tipo de Ativo  | Cotação Automática | Análise de Risco | Gráficos | Alertas |
| -------------- | ------------------ | ---------------- | -------- | ------- |
| Ações          | ✅                 | ✅               | ✅       | ✅      |
| FIIs           | ✅                 | ✅               | ✅       | ✅      |
| ETFs           | ✅                 | ✅               | ✅       | ✅      |
| Tesouro Direto | ❌                 | ⚠️               | ⚠️       | ✅      |
| Outros         | ❌                 | ⚠️               | ⚠️       | ✅      |

### 💡 Dicas de Uso

#### **Para Tesouro Direto:**

- Use o valor de face como preço (ex: R$ 1,00 para SELIC)
- Atualize preços manualmente quando houver atualizações
- Configure alertas para acompanhar rentabilidade

#### **Para Ações/FIIs/ETFs:**

- Use tickers corretos (ex: PETR4, não PETR4.SA)
- A cotação é atualizada automaticamente
- Análise de risco completa disponível

## 📋 Funcionalidades Detalhadas

### Cadastro de Ativos

- **Ticker**: Código do ativo (ex: PETR4, VALE3)
- **Tipo**: Ação, FII, ETF, Tesouro, Outro
- **Quantidade**: Número de cotas/ações
- **Preço**: Valor da transação
- **Data**: Data da compra/venda

### Análise de Risco

- **Volatilidade**: Medida de variação do preço
- **Beta**: Correlação com o mercado (Ibovespa)
- **Período**: Último ano por padrão

### Projeções e Simulações

- **Monte Carlo**: Simulação estatística com múltiplos cenários
- **Projeção Linear**: Crescimento constante baseado em taxa de retorno
- **Configurável**: Número de simulações e período

### Sistema de Alertas

- **Preço Alvo**: Alerta quando ativo atinge preço específico
- **Variação Percentual**: Alerta para variações significativas
- **Notificações**: Pop-ups e logs automáticos

## 🎨 Interface

### Temas Disponíveis

- **Tema Claro**: Fundo branco, texto escuro
- **Tema Escuro**: Fundo escuro, texto claro

### Layout Responsivo

- **Botões Adaptativos**: Reorganizam conforme tamanho da janela
- **Tabela Interativa**: Clique duplo para ver gráficos
- **Pesquisa**: Filtre ativos por nome ou tipo

## 🔧 Configuração

### Arquivo de Configuração

O arquivo `src/config.py` centraliza todas as configurações:

```python
# Exemplo de configuração
APP_CONFIG = {
    "title": "App de Controle e Automação de Carteira de Investimentos",
    "version": "2.0.0",
    "update_interval_minutes": 5,
    "default_theme": "light"
}
```

### Personalização

- **Intervalo de Atualização**: Configure em `APP_CONFIG`
- **Temas**: Adicione novos temas em `THEME_CONFIG`
- **Validações**: Ajuste regras em `VALIDATION_CONFIG`
- **Mensagens**: Personalize textos em `MESSAGES`

## 🧪 Testes

### Executar Testes

```bash
python src/test_main.py
```

### Cobertura de Testes

- **Testes Unitários**: Cada classe tem seus próprios testes
- **Testes de Integração**: Verificação de fluxos completos
- **Testes de Validação**: Verificação de dados de entrada
- **Testes de Erro**: Tratamento de exceções

### Tipos de Teste

- **DateFormatter**: Formatação de datas
- **ThemeManager**: Gerenciamento de temas
- **CarteiraDataManager**: Cálculos de carteira
- **UIManager**: Interface do usuário
- **Config**: Funções de configuração
- **Validação**: Regras de negócio

## 📊 Métricas de Qualidade

### Antes da Refatoração

- **850 linhas** em arquivo único
- **1 classe** monolítica
- **Código duplicado** em várias partes
- **Difícil manutenção**

### Depois da Refatoração

- **915 linhas** organizadas em **6 classes**
- **Separação clara** de responsabilidades
- **Reutilização** de código
- **Fácil manutenção** e extensão
- **Type hints** e documentação completa

## 🔄 Melhorias Implementadas

### Arquitetura

- ✅ **Modularização**: Código dividido em módulos lógicos
- ✅ **SOLID**: Princípios aplicados corretamente
- ✅ **DRY**: Eliminação de código duplicado
- ✅ **KISS**: Simplificação da lógica

### Performance

- ✅ **Threading**: Tarefas em segundo plano otimizadas
- ✅ **Memória**: Melhor gestão de recursos
- ✅ **Interface**: Layout responsivo e eficiente

### Manutenibilidade

- ✅ **Configuração**: Centralizada e flexível
- ✅ **Testes**: Cobertura completa
- ✅ **Documentação**: Docstrings e comentários
- ✅ **Type Hints**: Tipagem estática

## 🚀 Roadmap

### Próximas Versões

- [ ] **API REST**: Interface web
- [ ] **Mobile**: Aplicativo móvel
- [ ] **Cloud**: Sincronização na nuvem
- [ ] **IA**: Análise preditiva
- [ ] **Social**: Compartilhamento de estratégias

### Melhorias Técnicas

- [ ] **Docker**: Containerização
- [ ] **CI/CD**: Pipeline automatizado
- [ ] **Monitoramento**: Métricas em tempo real
- [ ] **Cache**: Otimização de performance

## 🤝 Contribuição

### Como Contribuir

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

### Padrões de Código

- **PEP 8**: Estilo de código Python
- **Type Hints**: Tipagem estática
- **Docstrings**: Documentação de funções
- **Testes**: Cobertura mínima de 80%

## 👨‍💻 Autor

**Sonekas** - [GitHub](https://github.com/Sonekas)

---
