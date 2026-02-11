document.addEventListener('DOMContentLoaded', () => {
    const toolList = document.getElementById('tool-list');
    const formFields = document.getElementById('form-fields');
    const toolForm = document.getElementById('tool-form');
    const activeToolName = document.getElementById('active-tool-name');
    const activeToolDesc = document.getElementById('active-tool-desc');
    const consoleOutput = document.getElementById('console-output');
    const runBtn = document.getElementById('run-btn');
    const clearConsoleBtn = document.getElementById('clear-console');
    const lastRunTime = document.getElementById('last-run-time');

    let currentTool = null;
    let toolsData = [];

    // Carregar ferramentas da API
    async function loadTools() {
        try {
            const response = await fetch('/api/tools');
            toolsData = await response.json();

            toolList.innerHTML = '';
            toolsData.forEach(tool => {
                const li = document.createElement('li');
                li.className = 'tool-item';
                li.innerHTML = `
                    <span class="tool-name">${tool.name}</span>
                    <span class="tool-summary">${tool.description}</span>
                `;
                li.addEventListener('click', () => selectTool(tool));
                toolList.appendChild(li);
            });
        } catch (error) {
            console.error('Erro ao carregar ferramentas:', error);
            toolList.innerHTML = '<li class="error-state">Erro ao conectar ao servidor.</li>';
        }
    }

    function selectTool(tool) {
        currentTool = tool;

        // Atualizar UI da sidebar
        document.querySelectorAll('.tool-item').forEach(item => {
            item.classList.remove('active');
            if (item.querySelector('.tool-name').textContent === tool.name) {
                item.classList.add('active');
            }
        });

        // Atualizar cabeçalho
        activeToolName.textContent = tool.name;
        activeToolDesc.textContent = tool.description;

        // Gerar campos do formulário
        generateForm(tool);
        runBtn.disabled = false;
    }

    function generateForm(tool) {
        formFields.innerHTML = '';

        tool.params.forEach(param => {
            const group = document.createElement('div');
            group.className = 'form-group';

            const label = document.createElement('label');
            label.textContent = param.charAt(0).toUpperCase() + param.slice(1).replace('_', ' ');

            let input;
            if (param === 'prompt' || param === 'context') {
                input = document.createElement('textarea');
                input.rows = 3;
            } else {
                input = document.createElement('input');
                input.type = 'text';
            }

            input.name = param;
            input.placeholder = `Digite o valor para ${param}...`;
            input.required = param !== 'country_code' && param !== 'context';

            group.appendChild(label);
            group.appendChild(input);
            formFields.appendChild(group);
        });
    }

    toolForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!currentTool) return;

        const formData = new FormData(toolForm);
        const args = {};
        formData.forEach((value, key) => {
            if (value) args[key] = value;
        });

        addToConsole(`Executando ${currentTool.name}...`, 'info');
        runBtn.disabled = true;
        runBtn.textContent = 'Executando...';

        try {
            const response = await fetch('/api/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tool_name: currentTool.name,
                    arguments: args
                })
            });

            const data = await response.json();

            if (response.ok) {
                addToConsole(data.result, 'success');
            } else {
                addToConsole(`Erro do Servidor: ${data.detail}`, 'error');
            }

            const now = new Date();
            lastRunTime.textContent = `Última execução: ${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;

        } catch (error) {
            addToConsole(`Erro de Rede: ${error.message}`, 'error');
        } finally {
            runBtn.disabled = false;
            runBtn.textContent = 'Executar Ferramenta';
        }
    });

    function addToConsole(text, type) {
        const welcome = consoleOutput.querySelector('.console-welcome');
        if (welcome) welcome.remove();

        const entry = document.createElement('div');
        entry.className = 'console-entry';

        const header = document.createElement('div');
        header.className = 'entry-header';
        header.textContent = `[${new Date().toLocaleTimeString()}] ${type.toUpperCase()}`;

        const content = document.createElement('div');
        content.textContent = text;

        entry.appendChild(header);
        entry.appendChild(content);

        consoleOutput.appendChild(entry);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }

    clearConsoleBtn.addEventListener('click', () => {
        consoleOutput.innerHTML = '<div class="console-welcome">Console limpo. Aguardando comando...</div>';
    });

    loadTools();
});
