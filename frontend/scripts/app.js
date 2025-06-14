// scripts/app.js (Versão Corrigida e Mais Robusta)

lucide.createIcons();

// Referências aos elementos do DOM
const form = document.getElementById('analysis-form');
const submitButton = document.getElementById('submit-button');
const buttonText = document.getElementById('button-text');
const buttonSpinner = document.getElementById('button-spinner');
const resultsCard = document.getElementById('results-card');
const textArea = document.getElementById('texto_usuario');

// Função para mostrar os resultados de forma amigável e segura
function displayResults(data) {
    // CORREÇÃO: Verificamos se 'data.gatilhos_potenciais' existe antes de o usar.
    // Se não existir, usamos um objeto vazio {} como padrão.
    const gatilhos = data?.gatilhos_potenciais || {};
    
    const allTriggers = [
        ...(gatilhos.alimentacao || []),
        ...(gatilhos.ambiente || []),
        ...(gatilhos.rotina || [])
    ];

    let triggersHtml = '<p class="text-sm text-slate-500">Nenhum gatilho específico identificado.</p>';
    if (allTriggers.length > 0) {
        triggersHtml = allTriggers.map(trigger => 
            `<span class="inline-block bg-indigo-100 text-indigo-800 text-sm font-medium mr-2 mb-2 px-3 py-1 rounded-full">${trigger}</span>`
        ).join('');
    }
    
    // CORREÇÃO: Verificamos se 'data.sintomas' existe antes de usar .join()
    const sintomasTexto = (data?.sintomas || []).join(', ') || 'Nenhum';
    
    const content = `
        <h2 class="text-xl font-semibold mb-4 text-slate-800">Resultados da Análise</h2>
        <div class="mb-6">
            <h3 class="text-lg font-semibold text-slate-700 mb-2">Resumo da IA</h3>
            <p class="text-slate-600 italic">"${data.resumo_narrativo || 'Não foi possível gerar um resumo.'}"</p>
        </div>
        <div class="mb-6">
            <h3 class="text-lg font-semibold text-slate-700 mb-2">Sintomas Identificados</h3>
            <p class="text-slate-600">${sintomasTexto}</p>
        </div>
        <div class="mb-6">
            <h3 class="text-lg font-semibold text-slate-700 mb-2">Gatilhos Potenciais</h3>
            <div>${triggersHtml}</div>
        </div>
        <details class="mt-4">
            <summary class="cursor-pointer text-sm text-slate-500 hover:text-slate-900">Ver dados brutos (JSON)</summary>
            <pre class="bg-slate-100 p-4 rounded-md mt-2 text-xs overflow-x-auto"><code>${JSON.stringify(data, null, 2)}</code></pre>
        </details>
    `;
    
    resultsCard.innerHTML = content;
    resultsCard.classList.remove('hidden');
}

// Função para mostrar erros
function displayError(message) {
    const content = `
        <h2 class="text-xl font-semibold mb-4 text-red-700">Ocorreu um Erro</h2>
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md">
            <p>${message}</p>
        </div>
    `;
    resultsCard.innerHTML = content;
    resultsCard.classList.remove('hidden');
}

// Listener do formulário (sem alterações)
form.addEventListener('submit', async (event) => {
    event.preventDefault(); 

    const textoUsuario = textArea.value;
    if (!textoUsuario.trim()) {
        alert("Por favor, escreva uma anotação.");
        return;
    }

    submitButton.disabled = true;
    buttonText.classList.add('hidden');
    buttonSpinner.classList.remove('hidden');
    resultsCard.classList.add('hidden');

    try {
        const response = await fetch('https://aurora-api-q3la.onrender.com/analise_texto', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ texto: textoUsuario }),
        });

        if (response.ok) {
            const data = await response.json();
            displayResults(data);
        } else {
            const errorData = await response.text();
            displayError(`O servidor retornou um erro: ${response.status}. ${errorData}`);
        }
    } catch (error) {
        console.error('Erro de conexão:', error);
        displayError('Não foi possível conectar ao servidor Python. Verifique a consola do navegador para mais detalhes.');
    } finally {
        submitButton.disabled = false;
        buttonText.classList.remove('hidden');
        buttonSpinner.classList.add('hidden');
    }
});