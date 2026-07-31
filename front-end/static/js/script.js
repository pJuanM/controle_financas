// // PEGAR ELEMENTOS #MENU E .TOGGLE
// const menu = document.querySelector("#menu");
// const toggle = document.querySelector(".toggle")
// // DEFINIR TOGGLE COM EVENTO DE CLIQUE, PASSANDO O MENU PARA RECEBER A CLASSE ACTIVE
// toggle.addEventListener("click", function() {
//     menu.classList.toggle("active")
//     console.log("clicado")
// })


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
// PEGAR ELEMENTOS .MENU_EDITAR E .OVERLAY 
const menu_editar = document.querySelector(".menu_editar");
const overlay = document.querySelector(".overlay")

// DECLARAR FUNCAO FECHAR MENU() QUE REMOVE A CLASSE ATIVO DO MENU EDITAR E DO OVERLAY
function fecharMenu(){
    menu_editar.classList.toggle("ativo");
    overlay.classList.toggle("ativo");
}
// ADICIONAR EVENTO DE CLICK NO OVERLAY PARA ELE FECHAR O MENU
overlay.addEventListener("click", function() {
    fecharMenu()
})
// ADICIONAR EVENTO DE FECHAR O MENU QUANDO PRESSIONAR O BOTAO ESCAPE BASEADO NO EVENTO REALIZADO
addEventListener("keydown", function(e) {
    if (e.key === "Escape" && menu_editar.classList.contains("ativo")) {
        fecharMenu() ;
    }   
})

// EDITAR VIA FETCH
const formEditar = document.getElementById("formulario_editar");
let linhaSelecionada = null;
if (formEditar) {
    formEditar.addEventListener("submit", async (e) => {
        e.preventDefault();

        const botao = e.submitter;
        const url = botao.formAction;

        const dados = new FormData(formEditar);

        const tipoDados = formEditar.dataset.tipo;

        const resposta = await fetch(url, {
            method: "POST",
            body: dados
        });

        const resultado = await resposta.json();
        
        if (resultado.sucesso) {
            // Pega o valor setado nos inputs de edição
            function pegarValor(id){
                const elemento = document.getElementById(id);
                return elemento ? elemento.value : '';
            }
            // LANÇAENTOS
            const novaDtCompra = pegarValor("editar_data_compra");
            const novoItem = pegarValor("editar_item_comprado");
            const novoValor = pegarValor("editar_valor_lancamento");
            const novoPagamentoLancamento = pegarValor("editar_id_forma_pagamento");
            const novaCategoriaLancamento = pegarValor("editar_id_categoria");
            const novaParcelas = pegarValor("editar_qnt_parcelas");
            const novoPagador = pegarValor("editar_pagador_responsavel");

            // PARCELAS  
            const novoStatusParcela = pegarValor("editar_status_parcela");
            
            // FORMAS DE PAGAMENTO
            const novaFormaPagamento = pegarValor("editar_forma_pagamento");
            const novaDtVencimento = pegarValor("editar_data_vencimento");
            const novaDtFechamento = pegarValor("editar_data_fechamento");
            const novoStatusFormaPagamento = pegarValor("editar_status_forma_pagamento");
            

            // CATEGORIAS
            const novaCategoria = pegarValor("editar_categoria");
            const novaDescricao = pegarValor("editar_descricao");
            const novoStatusCategoria = pegarValor("editar_status_categoria");
            // AJUSTAR DATA DE COMPRA (TIPO DATE)
            let dataCompraFormatada = "";
            if (novaDtCompra) {
                dataCompraFormatada = novaDtCompra.split("-").reverse().join("/");
            }

            // Atualiza os dados usados pelo editarItem()

            // LANÇAMENTOS
            linhaSelecionada.dataset.dataCompra = novaDtCompra;
            linhaSelecionada.dataset.itemComprado = novoItem;
            linhaSelecionada.dataset.valorLancamento = novoValor;
            linhaSelecionada.dataset.idFormaPagamento = novoPagamentoLancamento;
            linhaSelecionada.dataset.idCategoria = novaCategoriaLancamento;
            linhaSelecionada.dataset.qntParcelas = novaParcelas;
            linhaSelecionada.dataset.pagadorResponsavel = novoPagador;

            // PARCELAS
            linhaSelecionada.dataset.statusParcela = novoStatusParcela;

            // FORMAS DE PAGAMENTO
            linhaSelecionada.dataset.dataVencimento = novaDtVencimento;
            linhaSelecionada.dataset.formaPagamento = novaFormaPagamento;
            linhaSelecionada.dataset.dataFechamento = novaDtFechamento;
            linhaSelecionada.dataset.statusFormaPagamento = novoStatusFormaPagamento;

            // CATEGORIAS
            linhaSelecionada.dataset.categoria = novaCategoria;
            linhaSelecionada.dataset.descricao = novaDescricao;
            linhaSelecionada.dataset.statusCategoria = novoStatusCategoria;

            // Atualiza visual da tabela
            // FORMAS DE PAGAMENTO
            
            if (tipoDados === "formasPagamento") {
                linhaSelecionada.cells[0].textContent = resultado.formaPagamento;
                linhaSelecionada.cells[1].textContent = resultado.responsavel;
                linhaSelecionada.cells[2].textContent = resultado.data_vencimento;
                linhaSelecionada.cells[3].textContent = resultado.status;
            }
            // CATEGORIAS
            if (tipoDados === "categorias") {
                linhaSelecionada.cells[0].textContent = resultado.categoria;
                linhaSelecionada.cells[1].textContent = resultado.descricao;
                linhaSelecionada.cells[2].textContent = resultado.status_categoria;
            }
            // LANÇAMENTOS
            if (tipoDados === "lancamentos") {
                linhaSelecionada.cells[0].textContent = dataCompraFormatada;
                linhaSelecionada.cells[1].textContent = resultado.item_comprado;
                linhaSelecionada.cells[2].textContent = resultado.valor_lancamento;
            }

            fecharMenu();
            alert("Lançamento atualizado com sucesso!");
        }
    });
}

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
    const inputValorLancamento = document.getElementById("editar_valor_lancamento");
    const inputValorParcela = document.getElementById("editar_valor_parcela");

    if (inputValorLancamento) {
        inputValorLancamento.value = linha.dataset.valorLancamento;
        formatarMoeda(inputValorLancamento);
    };
    if (inputValorParcela) {
        inputValorParcela.value = linha.dataset.valorParcela;
        formatarMoeda(inputValorParcela);
    }


    const selectCategoria = document.getElementById("editar_id_categoria");
    if (selectCategoria != null) {
        selectCategoria.value = linha.dataset.idCategoria;
        console.log(
            "Opções:",
            [...selectCategoria.options].map(op => ({
                valor: op.value,
                texto: op.text
            }))
        );
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


// ADICIONAR COMPORTAMENTO DE MENU DROPDOWN NO DETAILS DE SELECIONAR PAGADOR RESPONSAVEL
document.addEventListener("click", function(event) {
    const filtros = document.querySelectorAll(".filtroDetails");

    filtros.forEach(function(filtro) {
        if (!filtro.contains(event.target)) {
            filtro.open = false;
        }
    });
});