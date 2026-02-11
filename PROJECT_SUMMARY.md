# Resumo do Projeto: MCP Weather & Files AI Server

## Arquitetura Técnica

O servidor implementa o Model Context Protocol (MCP) para integrar Modelos de Linguagem de Grande Escala (LLMs) com APIs externas e o sistema de arquivos local.

### Visão Geral do Sistema
```text
[ Cliente: Claude Desktop / Gemini ]
             |
             | (Protocolo MCP / JSON-RPC)
             |
[ Servidor: Implementação MCP em Python ]
             |
  +----------+----------+----------+
  |          |          |          |
[ OpenWeatherMap ] [ RestCountries ] [ Sistema de Arquivos Local ]
  |          |          |          |
  +----------+----------+----------+
             |
[ Provedores de IA: OpenAI (Primário) / Anthropic (Fallback) ]
```

## Detalhes de Implementação

### Infraestrutura Core
- **Servidor Core**: Desenvolvido utilizando o SDK oficial da Anthropic para Python.
- **I/O Assíncrono**: Gerenciamento de alta performance para clientes HTTP com `httpx` e `asyncio`.
- **Configuração**: Carregamento dinâmico de variáveis de ambiente via `python-dotenv`.

### Ferramentas Integradas

1. **Integração Meteorológica**: Interface com OpenWeatherMap.org para recuperação de parâmetros meteorológicos ao vivo.
2. **Serviço de Dados Geográficos**: Consome a API RestCountries para obter metadados demográficos e regionais.
3. **Ponte de Sistema de Arquivos**: Interface segura para navegação em diretórios e leitura de arquivos.
4. **Camada de Raciocínio de IA**: Interface multi-provedor que implementa estratégia de failover:
   - Primário: OpenAI (GPT-4o-mini).
   - Fallback: Anthropic (Claude 3.5 Sonnet).

## Requisitos Técnicos
- Python 3.10 ou superior
- `mcp>=0.9.0`
- `httpx>=0.27.0`
- `pydantic>=2.0.0`
- `openai>=1.54.0`
- `anthropic>=0.39.0`

## Padrões de Projeto e Boas Práticas

### 1. Padrão de Provedor (IA)
O servidor utiliza uma camada de abstração para operações de IA, permitindo a alternância transparente entre os serviços da OpenAI e Anthropic sem comprometer a resposta ao cliente.

### 2. Operações Seguras de Sistema de Arquivos
- Resolução e normalização de caminhos através de `pathlib.Path.resolve()`.
- Verificação explícita de existência e permissões de leitura dos arquivos.
- Limite de buffer para leitura de arquivos extensos.

### 3. Tratamento de Erros Assíncrono
Implementação de blocos try-except em todas as ferramentas para garantir a estabilidade do servidor. Logging detalhado para diagnóstico de exceções de rede ou permissões de sistema.

## Roadmap do Projeto

### Fase 1: Integração de Banco de Dados
- Suporte para conectores SQLite/PostgreSQL.
- Camada de cache local para respostas de API.

### Fase 2: Autenticação Avançada
- Fluxo OAuth2 para serviços de armazenamento em nuvem.
- Gerenciamento de sessões por usuário.

### Fase 3: Streams em Tempo Real
- Suporte para atualizações de ferramentas via WebSocket.
- Leitura incremental para grandes volumes de dados.

## Status de Desenvolvimento
O projeto está pronto para integração com clientes MCP padrão. Todas as ferramentas core (clima, fatos geográficos, arquivos, IA) estão operacionais e validadas pela suite de testes interna.
