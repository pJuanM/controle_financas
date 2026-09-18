// ======================================================
// SELECIONAR PARCELAS
// ======================================================

document.querySelectorAll(".btn-liquidar").forEach(checkbox => {
    checkbox.addEventListener("click", function (e) {
        // Impede que o clique no checkbox abra o menu de edição da linha
        e.stopPropagation();
    });
});

// ======================================================
// BOTÃO LIQUIDAR
// ======================================================

const btnLiquidar = document.getElementById("btn-liquidar");
if (btnLiquidar) {
    btnLiquidar.addEventListener("click", async function () {
        // Pega somente os checkboxes marcados
        const selecionados = document.querySelectorAll(
            ".btn-liquidar:checked"
        );
        // ==================================================
        // NENHUM ITEM SELECIONADO
        // ==================================================
        if (selecionados.length === 0) {
            alert("Selecione pelo menos uma parcela.");
            return;
        }
        // ==================================================
        // CONFIRMAÇÃO
        // ==================================================
        const confirmar = confirm(
            "DESEJA LIQUIDAR LANÇAMENTOS?"
        );
        // Se clicar em "Cancelar",
        // não fazemos absolutamente nada.
        //
        // Os checkboxes continuam marcados.
        if (!confirmar) {
            return;
        }
        // ==================================================
        // PEGAR IDS DAS PARCELAS
        // ==================================================
        const ids = [];
        selecionados.forEach(checkbox => {
            const linha = checkbox.closest("tr");
            if (linha) {
                const id = linha.dataset.id;
                ids.push(id);
            }
        });
        console.log("Parcelas selecionadas:", ids);
        // ==================================================
        // LIQUIDAR PARCELAS
        // ==================================================
        try {
            for (const id of ids) {
                const dados = new FormData();
                dados.append("id_parcela", id);
                dados.append("status_parcela", "PAGO");
                const resposta = await fetch(
                    "/parcelas/editar",
                    {
                        method: "POST",
                        body: dados
                    }
                );
                const resultado = await resposta.json();
                // Se o backend retornar erro
                if (!resposta.ok) {
                    throw new Error(
                        resultado.detail ||
                        "Erro ao liquidar parcela."
                    );
                }
                console.log(
                    `Parcela ${id} liquidada com sucesso.`
                );
            }
            // ==================================================
            // REMOVER AS LINHAS DA TABELA
            // ==================================================
            selecionados.forEach(checkbox => {
                const linha = checkbox.closest("tr");
                if (linha) {
                    linha.remove();
                }
            });
            console.log(
                "Todos os lançamentos foram liquidados."
            );
        } catch (erro) {
            console.error(
                "Erro ao liquidar lançamentos:",
                erro
            );
            alert(
                "Ocorreu um erro ao liquidar os lançamentos."
            );
        }
    });

}

const selecionarTudo = document.querySelector(".selecionar_tudo");

selecionarTudo.addEventListener("click", function () {
    const botoesLiquidar = document.querySelectorAll(".btn-liquidar");
    const bolinhaAlternavel = document.querySelector("#selecionarTodasParcelas");

    if (botoesLiquidar.length === 0){ 
        return;
    }

    bolinhaAlternavel.classList.toggle("ativo")
    const selecionado = bolinhaAlternavel.classList.contains("ativo");
    console.log(selecionado)
    for (const botao of botoesLiquidar) {
        botao.checked = selecionado;
    }
});


