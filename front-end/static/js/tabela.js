// ORDENAR TABELA
function ordenarTabela(colunaElemento, indiceColuna, tipoDado) {
    const tbody = document.querySelector(".tabela table tbody");
    const todasLinhas = Array.from(tbody.querySelectorAll('tr'));
    // Separar linha do total
    const linhaTotal = todasLinhas.find(
        linha => linha.classList.contains("linha-total")
    );
    // Apenas linhas que podem ser ordenadas
    const linhas = todasLinhas.filter(
        linha => !linha.classList.contains("linha-total")
    );
    // Verificar se a tabela está vazia
    if (linhas.length === 0 || (linhas.length === 1 && linhas[0].cells.length === 1)) {
        return;
    }
    // Descobre direção atual
    const direcaoAtual = colunaElemento.dataset.ordem === 'asc' ? 'desc' : 'asc';
    // Remove setas dos outros cabeçalhos
    document.querySelectorAll(".tabela_cabecalho").forEach(th => {
        if (th !== colunaElemento) {
            th.classList.remove("ordem-asc", "ordem-desc");
            delete th.dataset.ordem;
        }
    });
    linhas.sort((a, b) => {
        let valorA = a.cells[indiceColuna].textContent.trim();
        let valorB = b.cells[indiceColuna].textContent.trim();
        // Ordenação numérica
        if (tipoDado === 'numero') {
            valorA = parseFloat(
                valorA
                    .replace(/[^0-9,-]/g, '')
                    .replace(/\./g, '')
                    .replace(',', '.')
            ) || 0;
            valorB = parseFloat(
                valorB
                    .replace(/[^0-9,-]/g, '')
                    .replace(/\./g, '')
                    .replace(',', '.')
            ) || 0;
            return direcaoAtual === 'asc'
                ? valorA - valorB
                : valorB - valorA;
        }
        // Ordenação de parcela
        if (tipoDado === 'parcela') {
            const itemA = a.cells[2].textContent.trim();
            const itemB = b.cells[2].textContent.trim();
            const comparacaoItem = itemA.localeCompare(itemB);
            if (comparacaoItem !== 0) {
                return direcaoAtual === 'asc'
                    ? comparacaoItem
                    : -comparacaoItem;
            }
            const numeroA = parseInt(valorA.split('/')[0], 10);
            const numeroB = parseInt(valorB.split('/')[0], 10);
            return direcaoAtual === 'asc'
                ? numeroA - numeroB
                : numeroB - numeroA;
        }
        // Ordenação por data
        if (tipoDado === 'data') {
            const [diaA, mesA, anoA] = valorA.split('/');
            const [diaB, mesB, anoB] = valorB.split('/');
            const dateA = new Date(anoA, mesA - 1, diaA);
            const dateB = new Date(anoB, mesB - 1, diaB);
            return direcaoAtual === 'asc'
                ? dateA - dateB
                : dateB - dateA;
        }
        // Ordenação texto
        const comparacao = valorA.localeCompare(valorB);
        return direcaoAtual === 'asc'
            ? comparacao
            : -comparacao;
    });
    // Recria tabela
    tbody.innerHTML = '';
    linhas.forEach(linha => {
        tbody.appendChild(linha);
    });
    // Coloca total sempre no final
    if (linhaTotal) {
        tbody.appendChild(linhaTotal);
    }
    // Atualiza estado da seta
    colunaElemento.dataset.ordem = direcaoAtual;
    colunaElemento.classList.remove(
        "ordem-asc",
        "ordem-desc"
    );
    colunaElemento.classList.add(
        direcaoAtual === "asc"
            ? "ordem-asc"
            : "ordem-desc"
    );
}
