// MENU
const menu = document.getElementById('menu');
const toggle = document.querySelector('.toggle');

toggle.onclick = () => {
    menu.classList.toggle('active');
}

// ORDENAR TABELA
function ordenarTabela(colunaElemento, indiceColuna, tipoDado) {
    const tbody = document.querySelector(".tabela table tbody");
    const linhas = Array.from(tbody.querySelectorAll('tr'));

    // Verificar se a tabela está vazia (aparece a mensagem de "Nenhuma forma encontrada")
    if (linhas.length === 0 || (linhas.length === 1 && linhas[0].cells.length === 1)) return;

    // Descobre a direção atual guardada na própria tag HTML
    const direcaoAtual = colunaElemento.dataset.ordem === 'asc' ? 'desc' : 'asc';   
    
    // Remove setas visuais de todos os outros cabeçalhos antes de ordenar o atual
    document.querySelectorAll(".tabela_cabecalho").forEach(th => {
        if (th !== colunaElemento) {
            th.classList.remove("ordem-asc", "ordem-desc");
            delete th.dataset.ordem;
        }
    });

    // Ordenação customizada por tipo de dado
    linhas.sort((a, b) => {
        let valorA = a.cells[indiceColuna].textContent.trim();
        let valorB = b.cells[indiceColuna].textContent.trim();

        if (tipoDado === 'numero') {
            // Remove "R$", pontos de milhar e troca vírgula por ponto para virar número real
            valorA = parseFloat(valorA.replace(/[^0-9,-]/g, '').replace('.', '').replace(',', '.')) || 0;
            valorB = parseFloat(valorB.replace(/[^0-9,.-]/g, '').replace(/\./g, '').replace(',', '.')) || 0

            return direcaoAtual === 'asc' ? valorA - valorB : valorB - valorA;
        } 
        if (tipoDado === 'parcela') {
            const itemA = a.cells[2].textContent.trim();
            const itemB = b.cells[2].textContent.trim();

            // Primeiro compara o nome do débito
            const comparacaoItem = itemA.localeCompare(itemB);

            if (comparacaoItem !== 0) {
                return direcaoAtual === 'asc'
                    ? comparacaoItem
                    : -comparacaoItem;
            }

            // Se for o mesmo débito, compara o número da parcela
            const numeroA = parseInt(valorA.split('/')[0], 10);
            const numeroB = parseInt(valorB.split('/')[0], 10);

            return direcaoAtual === 'asc'
                ? numeroA - numeroB
                : numeroB - numeroA;
        }
        
        if (tipoDado === 'data') {
            // Transforma o formato DD/MM/AAAA em um objeto Date comparável
            const [diaA, mesA] = valorA.split('/');
            const [diaB, mesB] = valorB.split('/');
            const dateA = new Date(mesA - 1, diaA);
            const dateB = new Date(mesB - 1, diaB);
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
    colunaElemento.classList.remove("ordem-asc", "ordem-desc");
    colunaElemento.classList.add(
        direcaoAtual === "asc" ? "ordem-asc" : "ordem-desc"
    );
}



// ABRIR OVERLAY
const menu_editar = document.querySelector('.menu_editar');
const overlay = document.querySelector('.overlay');
overlay.addEventListener("click", function() {
    menu_editar.classList.remove("ativo");
    overlay.classList.remove("ativo");
});

// EDITAR ITEM
function editarItem(linha) {

    menu_editar.classList.add("ativo");
    overlay.classList.add("ativo");
    

    for (const campo in linha.dataset) {

        const id = "editar_" + campo.replace(/[A-Z]/g, letra => "_" + letra.toLowerCase());

        const input = document.getElementById(id);

        if (input) {
            input.value = linha.dataset[campo];
        }
    }
    document.querySelector("[data-id-principal]").value = linha.dataset.id;
    const inputValor = document.getElementById("editar_valor_lancamento");


    if (inputValor) {
        inputValor.value = linha.dataset.valorLancamento;
        formatarMoeda(inputValor);
    }
}
// ESCONDER BOTOES QUANDO SELECIONAR INPUT OU SELECT
const campos = document.querySelectorAll('.menu_editar input, .menu_editar select');
const botoes = document.querySelector(".botoes_formulario");


campos.forEach(campo => {
    if (campo.type === 'hidden') return;

    campo.addEventListener('focus', () => {
        botoes.style.display = 'none';
    });

    campo.addEventListener('blur', () => {
        setTimeout(() => {
            const campoComFoco = [...campos].some(c => c === document.activeElement);
            botoes.style.display = campoComFoco ? 'none' : '';
        }, 0);
    });
});