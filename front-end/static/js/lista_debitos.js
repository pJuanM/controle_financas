function ordenarTabela(colunaElemento, indiceColuna, tipoDado) {
    const tbody = document.querySelector(".tabela table tbody");
    const linhas = Array.from(tbody.querySelectorAll('tr'));

    // Verifica se a tabela está vazia (mensagem de "Nenhuma forma encontrada")
    if (linhas.length === 0 || (linhas.length === 1 && linhas[0].cells.length === 1)) return;

    // Descobre a direção atual guardada na própria tag HTML (padrão: crescente)
    const direcaoAtual = colunaElemento.dataset.ordem === 'asc' ? 'desc' : 'asc';
    
    // Remove setas visuais de todos os outros cabeçalhos antes de ordenar o atual
    document.querySelectorAll(".tabela-cabecalho").forEach(th => {
        if (th !== colunaElemento) {
            th.textContent = th.textContent.replace(/▲|▼/g, '');
            delete th.dataset.ordem;
        }
    });

    // Ordenação customizada por tipo de dado
    linhas.sort((a, b) => {
        let valorA = a.cells[indiceColuna].textContent.trim();
        let valorB = b.cells[indiceColuna].textContent.trim();

        if (tipoDado === 'numero') {
            // Remove "R$", pontos de milhar e troca vírgula por ponto para virar número real
            valorA = parseFloat(valorA.replace(/[^0-8,-]/g, '').replace('.', '').replace(',', '.')) || 0;
            valorB = parseFloat(valorB.replace(/[^0-8,-]/g, '').replace('.', '').replace(',', '.')) || 0;
            return direcaoAtual === 'asc' ? valorA - valorB : valorB - valorA;
        } 
        
        if (tipoDado === 'data') {
            // Transforma o formato DD/MM/AAAA em um objeto Date comparável
            const [diaA, mesA, anoA] = valorA.split('/');
            const [diaB, mesB, anoB] = valorB.split('/');
            const dateA = new Date(anoA, mesA - 1, diaA);
            const dateB = new Date(anoB, mesB - 1, diaB);
            return direcaoAtual === 'asc' ? dateA - dateB : dateB - dateA;
        }

        // Padrão: Texto (Alfabetico)
        const comparacao = valorA.localeCompare(valorB);
        return direcaoAtual === 'asc' ? comparacao : -1 * comparacao;
    });

    // Limpa e reinsere os dados na nova ordem
    tbody.innerHTML = '';
    linhas.forEach(linha => tbody.appendChild(linha));

    // Atualiza o estado da direção na tag HTML
    colunaElemento.dataset.ordem = direcaoAtual;

    // Atualiza o indicador visual de seta (▲ ou ▼) sem apagar o texto original do cabeçalho
    colunaElemento.textContent = colunaElemento.textContent.replace(/ ▲| ▼/g, '') + (direcaoAtual === 'asc' ? ' ▲' : ' ▼');
}