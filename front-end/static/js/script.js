// MENU
const menu = document.getElementById('menu');
const toggle = document.querySelector('.toggle');

toggle.onclick = () => {
    menu.classList.toggle('active');
}

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


// ABRIR OVERLAY
const menu_editar = document.querySelector('.menu_editar');
const overlay = document.querySelector('.overlay');

function fecharMenu() {
    menu_editar.classList.remove("ativo");
    overlay.classList.remove("ativo");
}

overlay.addEventListener("click", fecharMenu);
// Fecha ao pressionar Esc
document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
        fecharMenu();
    }
});


// EDITAR VIA FETCH
const form = document.querySelector(".menu_editar form");
let linhaSelecionada = null;
console.log(form);
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const dados = new FormData(form);

    const resposta = await fetch("/lancamentos/editar", {
        method: "POST",
        body: dados
    });

    const resultado = await resposta.json();
    

    if (resultado.sucesso) {

        const novoItem = document.getElementById("editar_item_comprado").value;
        const novoValor = document.getElementById("editar_valor_lancamento").value;
        const novaDtCompra = document.getElementById("editar_data_compra").value;

        const dataCompraFormatada = novaDtCompra.split("-").reverse().join("/");

        // Atualiza visual da tabela
        linhaSelecionada.cells[0].textContent = resultado.data_compra;
        linhaSelecionada.cells[1].textContent = resultado.item_comprado;
        linhaSelecionada.cells[2].textContent = resultado.valor_lancamento;

        // Atualiza os dados usados pelo editarItem()
        linhaSelecionada.dataset.dataCompra = novaDtCompra;
        linhaSelecionada.dataset.itemComprado = novoItem;
        linhaSelecionada.dataset.valorLancamento = novoValor;

        fecharMenu();
        alert("Lançamento atualizado com sucesso!");
    }
});


// EDITAR ITEM
function editarItem(linha) {
    linhaSelecionada = linha;

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


    const selectCategoria = document.getElementById("editar_id_categoria");

    console.log("Categoria recebida:", linha.dataset.idCategoria);

    console.log(
        "Opções:",
        [...selectCategoria.options].map(op => ({
            valor: op.value,
            texto: op.text
        }))
    );

    selectCategoria.value = linha.dataset.idCategoria;

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


// ADICIONAR COMPORTAMENTO DE MENU DROPDOWN NO DETAILS DE SELECIONAR PAGADOR RESPONSAVEL
document.addEventListener("click", function(event) {
    const filtros = document.querySelectorAll(".filtroDetails");

    filtros.forEach(function(filtro) {
        if (!filtro.contains(event.target)) {
            filtro.open = false;
        }
    });
});