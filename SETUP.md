# Guia de Configuração e Instalação

Este documento detalha o procedimento para instalação, configuração e validação do servidor MCP Weather & Files AI.

## 1. Pré-requisitos

### Instalação do Python
Certifique-se de que o Python 3.10 ou superior esteja disponível no sistema.
```bash
python --version
```
Download disponível em: https://www.python.org/downloads/

## 2. Instalação

### Configuração do Ambiente Virtual
1. Acesse o diretório raiz do projeto:
   ```bash
   cd mcp-weather-server
   ```
2. Crie e ative o ambiente virtual:
   ```bash
   python -m venv venv
   # Ativação Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # Ativação Linux/macOS:
   source venv/bin/activate
   ```

### Gerenciamento de Dependências
Instale os pacotes necessários via pip:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configuração de APIs

### 3.1 OpenWeatherMap
1. Registre-se em [OpenWeatherMap.org](https://openweathermap.org/api).
2. Obtenha sua chave de API através do painel de controle.

### 3.2 Provedores de IA (Opcional)
- **OpenAI**: Configure suas chaves em [OpenAI Platform](https://platform.openai.com/api-keys).
- **Anthropic**: Configure suas chaves em [Anthropic Console](https://console.anthropic.com/).

### 3.3 Variáveis de Ambiente
Configure o arquivo `.env` utilizando o template fornecido:
```bash
cp .env.example .env
# Edite o arquivo .env com suas chaves de API
```

## 4. Validação

### 4.1 Testes Automatizados
Execute a suite de testes para validar a lógica interna e a conectividade com as APIs:
```bash
python test_server.py
```

### 4.2 Verificação Manual
Inicie o servidor diretamente no terminal para confirmar a inicialização correta:
```bash
python server.py
```
Uma inicialização bem-sucedida registrará o log: `INFO - Iniciando MCP Weather & Files AI Server...`

## 5. Integração com Claude Desktop

### Localização do Arquivo de Configuração
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Exemplo de Configuração JSON
```json
{
  "mcpServers": {
    "weather-files-ai": {
      "command": "python",
      "args": ["C:/caminho/para/server.py"],
      "env": {
        "WEATHER_API_KEY": "...",
        "OPENAI_API_KEY": "...",
        "ANTHROPIC_API_KEY": "..."
      }
    }
  }
}
```
*Nota: Utilize caminhos absolutos e verifique se o executável do Python está no PATH do sistema.*

## Solução de Problemas

### 'ModuleNotFoundError'
Verifique se o ambiente virtual está ativado corretamente e se as dependências foram instaladas via `pip install -r requirements.txt`.

### Erros de Integração
Consulte os logs do Claude Desktop para mensagens específicas de erro de inicialização:
- **Windows**: `%APPDATA%\Claude\logs\`

### Falhas de Conexão
Certifique-se de que as chaves de API estão configuradas corretamente no arquivo de configuração e que o servidor possui acesso à internet.
