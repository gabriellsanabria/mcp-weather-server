# Guia de Boas Práticas: Git e Segurança

Este documento descreve os procedimentos padrão para controle de versão e gerenciamento de segredos para este projeto.

## Configuração do Repositório

### Arquivos Monitorados
Os seguintes arquivos devem ser incluídos no controle de versão:
- Implementação core (`server.py`)
- Suites de teste (`test_server.py`)
- Especificações de dependência (`requirements.txt`)
- Templates de ambiente (`.env.example`)
- Documentação do projeto (Arquivos Markdown)
- Templates de implantação (`claude_desktop_config.json`)

### Arquivos Ignorados
Os seguintes padrões são excluídos através do `.gitignore`:
- Configurações locais (`.env`)
- Ambientes virtuais (`venv/`, `env/`)
- Artefatos de build e caches (`__pycache__/`, `*.pyc`)
- Metadados específicos do sistema (`.DS_Store`, `Thumbs.db`)

## Segurança: Variáveis de Ambiente

### Gerenciamento de Segredos
Chaves de API e configurações sensíveis **nunca** devem ser incluídas no repositório. O projeto utiliza `python-dotenv` para o gerenciamento local.

1. Garanta que o arquivo `.env` esteja listado no `.gitignore`.
2. Utilize o `.env.example` como um template não sensível para colaboração.
3. Caso um segredo seja exposto no histórico do Git:
   - Revogue a chave imediatamente.
   - Utilize ferramentas como `git filter-branch` ou `BFG Repo-Cleaner` para limpar o histórico.

## Workflow de Desenvolvimento

### Ramificações de Funcionalidade
Recomendamos o uso de Git Flow simplificado:
- `main`: Código pronto para produção.
- `feature/*`: Novas implementações ou adições de ferramentas.
- `fix/*`: Correções de bugs.

### Commits Convencionais
Utilize o seguinte formato para mensagens de commit:
- `feat`: Adição de nova ferramenta ou funcionalidade.
- `fix`: Resolução de bug.
- `docs`: Atualizações em documentação.
- `refactor`: Mudanças na estrutura do código sem alteração de funcionalidade.
- `test`: Adição de casos de teste.

Exemplo:
```bash
git commit -m "feat: implementacao de ferramenta de analise com fallback de provedor"
```

## Inicialização do Repositório

1. Inicialize o repositório local:
   ```bash
   git init
   ```
2. Verifique a lista de exclusão:
   ```bash
   git status
   ```
   *Confirme que o arquivo .env não consta na lista de arquivos não monitorados.*

3. Commit inicial:
   ```bash
   git add .
   git commit -m "feat: commit inicial - MCP Weather & Files AI Server"
   ```

4. Conexão com repositório remoto:
   ```bash
   git remote add origin https://github.com/gabriellsanabria/mcp-weather-server.git
   git branch -M main
   git push -u origin main
   ```

## Checklist Pré-submissão
- [ ] Nenhum segredo presente no código ou histórico de commits.
- [ ] requirements.txt atualizado com novas dependências.
- [ ] Testes executados com sucesso (`python test_server.py`).
- [ ] Documentação reflete o estado atual das funcionalidades.
