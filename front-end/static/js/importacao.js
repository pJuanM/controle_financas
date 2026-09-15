const form = document.getElementById("formImportacao");
const botao = document.getElementById("botaoImportarOfx");
const arquivoInput = document.getElementById("arquivoOFX");
const labelArquivo = document.getElementById("labelArquivo");

arquivoInput.addEventListener("change", function () {
    if (this.files.length > 0) {
        labelArquivo.innerText = this.files[0].name;
    } else {
        labelArquivo.innerText = "Arquivo OFX."
    }
});

form.addEventListener("submit", async function(event) {
    event.preventDefault();
    if (!arquivoInput.files.length) {
        alert("Nenhum arquivo selecionado.");
        return;
    }
    botao.disabled = true;
    botao.innerText = "LENDO ARQUIVO...";
    try {
        // =====================================================
        // PRIMEIRA REQUISIÇÃO
        // =====================================================
        const formData = new FormData(form);
        const resposta = await fetch(
            form.action,
            {
                method: "POST",
                body: formData
            }
        );
        const dados = await resposta.json();
        // =====================================================
        // FASTAPI DISSE QUE PRECISA CRIAR O NUBANK
        // =====================================================
        if (dados.precisa_criar_forma_pagamento) {
            const desejaCriar = confirm(
                "Deseja criar a forma de pagamento:\n\n" +
                dados.forma_pagamento + "?"
            );
            // Usuário respondeu NÃO
            if (!desejaCriar) {
                botao.disabled = false;
                botao.innerText = "LER ARQUIVO";
                return;
            }
            // =================================================
            // PERGUNTA VENCIMENTO
            // =================================================
            const vencimento = prompt(
                "Qual a data de vencimento?\n\n" +
                "Informe apenas o dia.\n" +
                "Exemplo: 8"
            );
            if (!vencimento) {
                botao.disabled = false;
                botao.innerText = "LER ARQUIVO";
                return;
            }
            // =================================================
            // PERGUNTA FECHAMENTO
            // =================================================
            const fechamento = prompt(
                "Qual a data de fechamento?\n\n" +
                "Informe apenas o dia.\n" +
                "Exemplo: 1"
            );
            if (!fechamento) {
                botao.disabled = false;
                botao.innerText = "LER ARQUIVO";
                return;
            }
            // =================================================
            // SEGUNDA REQUISIÇÃO
            // =================================================
            const novoFormData = new FormData();
            novoFormData.append(
                "arquivo",
                arquivoInput.files[0]
            );
            novoFormData.append(
                "confirmar_nubank",
                "true"
            );
            novoFormData.append(
                "data_vencimento",
                vencimento
            );
            novoFormData.append(
                "data_fechamento",
                fechamento
            );
            botao.innerText = "IMPORTANDO...";
            const segundaResposta = await fetch(
                form.action,
                {
                    method: "POST",
                    body: novoFormData
                }
            );
            const resultado = await segundaResposta.json();
            if (!segundaResposta.ok) {
                alert(
                    resultado.detail ||
                    "Erro ao importar o arquivo."
                );
                return;
            }
            if (resultado.sucesso) {
                alert(resultado.mensagem);
                window.location.href = "/lancamentos/";
            }
            return;
        }
        // =====================================================
        // NÃO PRECISOU CRIAR FORMA DE PAGAMENTO
        // =====================================================
        if (dados.sucesso) {
            alert(dados.mensagem);
            window.location.href = "/lancamentos/";
            return;
        }
        // =====================================================
        // ERRO
        // =====================================================
        if (dados.detail) {
            alert(dados.detail);
        } else {
            alert("Ocorreu um erro ao importar o arquivo.");
        }
    } catch (erro) {
        console.error(erro);
        alert(
            "Erro ao comunicar com o servidor."
        );
    } finally {
        botao.disabled = false;
        botao.innerText = "LER ARQUIVO";
    }
});