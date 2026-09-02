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
try {
    const overlay = document.querySelector(".overlay");
    if (overlay) {
        overlay.addEventListener("click", function() {
            fecharMenu();
        });
    }
} catch (error) {
    console.error("Erro ao configurar o overlay:", error);
}
// ADICIONAR EVENTO DE FECHAR O MENU QUANDO PRESSIONAR O BOTAO ESCAPE BASEADO NO EVENTO REALIZADO
addEventListener("keydown", function(e) {
    if (e.key === "Escape" && menu_editar.classList.contains("ativo")) {
        fecharMenu() ;
    }   
})



function atualizarLinhaEditar(resultado) {
    if (!linhaSelecionada) {
        return;
    }
    // DADOS
    const tipoDados = formEditar.dataset.tipo;
    // Atualiza visual da tabela
    // FORMAS DE PAGAMENTO
    if (tipoDados === "formasPagamento") {
        // FORMAS DE PAGAMENTO                
        const novaFormaPagamento = document.getElementById("editar_forma_pagamento")?.value || ""; 
        const novoResponsavelPagamento = document.getElementById("editar_responsavel")?.value || ""; 
        const novaDtVencimento = document.getElementById("editar_data_vencimento")?.value || ""; 
        const novaDtFechamento = document.getElementById("editar_data_fechamento")?.value || ""; 
        const novoStatusFormaPagamento = document.getElementById("editar_status_forma_pagamento")?.value || "";

        linhaSelecionada.cells[0].textContent = resultado.formaPagamento;
        linhaSelecionada.cells[1].textContent = resultado.responsavel;
        linhaSelecionada.cells[2].textContent = resultado.data_vencimento;

        // FORMAS DE PAGAMENTO
        linhaSelecionada.dataset.dataVencimento = novaDtVencimento;
        linhaSelecionada.dataset.formaPagamento = novaFormaPagamento;
        linhaSelecionada.dataset.responsavel = novoResponsavelPagamento;
        linhaSelecionada.dataset.dataFechamento = novaDtFechamento;
        linhaSelecionada.dataset.statusFormaPagamento = novoStatusFormaPagamento;
    }
    // CATEGORIAS
    else if (tipoDados === "categorias") {
        // CATEGORIAS
        const novaCategoria = document.getElementById("editar_categoria")?.value || ""; 
        const novaDescricao = document.getElementById("editar_descricao")?.value || ""; 
        const novoStatusCategoria = document.getElementById("editar_status_categoria")?.value || "";

        linhaSelecionada.cells[0].textContent = resultado.categoria;
        linhaSelecionada.cells[1].textContent = resultado.descricao;
        linhaSelecionada.cells[2].textContent = resultado.status_categoria;

        // CATEGORIAS
        linhaSelecionada.dataset.categoria = novaCategoria;
        linhaSelecionada.dataset.descricao = novaDescricao;
        linhaSelecionada.dataset.statusCategoria = novoStatusCategoria;
    }
    // LANÇAMENTOS
    else if (tipoDados === "lancamentos") {
        // LANÇAMENTOS
        const novaDtCompra = document.getElementById("editar_data_compra")?.value || "";
        const novoItem = document.getElementById("editar_item_comprado")?.value || ""; 
        const novoValor = document.getElementById("editar_valor_lancamento")?.value || ""; 
        const novoPagamentoLancamento = document.getElementById("editar_id_forma_pagamento")?.value || ""; 
        const novaCategoriaLancamento = document.getElementById("editar_id_categoria")?.value || ""; 
        const novaParcelas = document.getElementById("editar_qnt_parcelas")?.value || ""; 
        const novoPagador = document.getElementById("editar_pagador_responsavel")?.value || ""; 
        

        let dataCompraFormatada = "";
        if (novaDtCompra) {
            dataCompraFormatada = novaDtCompra.split("-").reverse().join("/");
        } 

        linhaSelecionada.cells[0].textContent = dataCompraFormatada;
        linhaSelecionada.cells[1].textContent = resultado.item_comprado;
        linhaSelecionada.cells[2].textContent = resultado.valor_lancamento;

        // LANÇAMENTOS
        linhaSelecionada.dataset.dataCompra = novaDtCompra;
        linhaSelecionada.dataset.itemComprado = novoItem;
        linhaSelecionada.dataset.valorLancamento = novoValor;
        linhaSelecionada.dataset.idFormaPagamento = novoPagamentoLancamento;
        linhaSelecionada.dataset.idCategoria = novaCategoriaLancamento;
        linhaSelecionada.dataset.qntParcelas = novaParcelas;
        linhaSelecionada.dataset.pagadorResponsavel = novoPagador;
    }
    // PARCELAS
    else if (tipoDados === "parcelas") {
        const novoStatusParcela = document.getElementById("editar_status_parcela")?.value || "";
        linhaSelecionada.dataset.statusParcela = novoStatusParcela;
    }
    // USUARIOS
    else if (tipoDados === "usuario") {
        const usuario = document.getElementById("usuario");
        const nome = document.getElementById("nome");
        const email = document.getElementById("email");
        const novoUsuario = document.getElementById("editar_usuario")?.value || "";
        const novoNome = document.getElementById("editar_nome")?.value || "";
        const novoEmail = document.getElementById("editar_email")?.value || "";

        if (usuario) {
            usuario.value = novoUsuario;
        }
        if (nome) {
            nome.value = novoNome;
        }
        if (email) {
            email.value = novoEmail;
        }
        return;
    }
}


// EDITAR VIA FETCH
const formEditar = document.getElementById("formulario_editar");
let linhaSelecionada = null;
if (formEditar) {
    formEditar.addEventListener("submit", async (e) => {
        e.preventDefault();

        const botaoClicado = e.submitter;

        if (!botaoClicado) {
            console.error("Não foi possível identificar botão clicado!");
            return;
        }

        const url = botaoClicado.dataset.url;
        const acao = botaoClicado.dataset.acao;

        if (!url) {
            console.error("O botão não possui uma rota definida.")
            return;
        }
        const dados = new FormData(formEditar);
        // EXCLUIR
        if (acao === "excluir") {
            const confirmar = confirm("Deseja realmente excluir?");
            if (!confirmar) {
                return;
            }
            try {
                const resposta = await fetch(
                    url,
                    {
                        method: "POST",
                        body:dados
                    }
                );
                const resultado = await resposta.json();

                if (!resposta.ok) {
                    throw new Error(
                        resultado.detail || "Erro ao excluir."
                    );
                };
                if (linhaSelecionada) {
                    linhaSelecionada.remove();
                };
                fecharMenu();
                alert(
                    resultado.mensagem || "Excluído com sucesso."
                );

            } catch (erro) {
                console.error(
                    "Erro ao excluir: ",
                    erro
                );
                alert(
                    erro.message || "Ocorreu um erro ao excluir!"
                );
            };

            return;
        }

        // EDITAR
        if (acao === "editar") {
            try {
                const resposta = await fetch(url, {
                    method: "POST",
                    body: dados
                });
                const resultado = await resposta.json();
                if (!resposta.ok) { 
                    throw new Error( resultado.detail || "Erro ao editar." ); 
                }
                if (!resultado.sucesso) { 
                    throw new Error( resultado.mensagem || "Não foi possível editar." ); 
                }
                atualizarLinhaEditar(resultado);
                alert(
                    resultado.mensagem ||
                    "Editado com sucesso!"
                );
                fecharMenu();
            } catch (erro) {
                console.error("Erro ao editar:", erro);
                alert(erro.message || "Ocorreu um erro ao editar!");
            }
            return;
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
