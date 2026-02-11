# Guia de Prompts e Scripts de Demonstração

Este documento fornece um conjunto de prompts para demonstrar a versatilidade do servidor MCP Weather & Files AI.

## 1. Workflows Multi-Ferramenta

### Planejamento de Viagem
Prompt:
```text
Estou planejando uma viagem para Tóquio. Por favor, forneça:
1. As condições climáticas atuais em Tóquio.
2. Fatos geográficos e demográficos sobre o Japão.
3. Liste o conteúdo da pasta 'Documents' para que eu possa revisar minhas notas de viagem anteriores.
```
*Demonstra: Execução sequencial de ferramentas (clima, geografia e sistema de arquivos).*

### Workflow de Desenvolvimento
Prompt:
```text
Liste os arquivos Python no diretório atual e leia o conteúdo de 'server.py'. Em seguida, verifique o clima em Nova York para entender as condições de trabalho da equipe remota.
```
*Demonstra: Coleta de contexto técnico integrada com dados externos em tempo real.*

## 2. Exemplos de Ferramentas Específicas

### Operações Meteorológicas
- "Condições atuais em Londres, Reino Unido"
- "Parâmetros meteorológicos para Florianópolis, BR"
- "Temperatura e umidade em Curitiba"

### Operações de Sistema de Arquivos
- "Listar todos os arquivos em C:\Users\Dev\Projects"
- "Ler o conteúdo de 'config.json' no diretório raiz"
- "Analisar a estrutura do projeto listando o diretório atual"

### Análise de IA e Recomendações
- "Com base no clima atual em Barcelona, sugira atividades ao ar livre"
- "Analise os arquivos do projeto e explique a estratégia de tratamento de erros do servidor"
- "Utilizando os dados geográficos do Japão, forneça um breve resumo econômico"

## 3. Testes de Casos Limite

### Tratamento de Erros
- "Obter clima para CidadeInexistente123"
- "Ler arquivo em /caminho/invalido/teste.txt"
- "Fornecer fatos para um país chamado 'Atlantis'"

### Grandes Conjuntos de Dados
- "Listar conteúdo de um diretório com mais de 100 arquivos"
- "Ler um arquivo que excede o limite do buffer interno (10KB)"

## 4. Scripts de Apresentação

### Visão Geral de Funcionalidades (90 Segundos)
1. **Clima**: Demonstrar recuperação de dados em tempo real.
2. **Geografia**: Exibir metadados de países.
3. **Sistema de Arquivos**: Listar e ler arquivos de configuração locais.
4. **Análise de IA**: Demonstrar o modelo avaliando entradas combinadas (ex: sugerir vestuário baseado no clima e destino).

## Destaques Técnicos
- **Simultaneidade**: Execução assíncrona de ferramentas.
- **Failover**: Alternância automática entre OpenAI e Anthropic para ferramentas de IA.
- **Segurança**: Normalização rigorosa de caminhos e acesso restrito a leitura.
- **Padronização**: Implementação baseada no protocolo Model Context Protocol.
