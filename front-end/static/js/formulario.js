// ESCONDER LABEL DO CAMPO DE DATA
document.querySelectorAll(".campo_data input").forEach(input => {
    const campo = input.parentElement;
    const label = campo.querySelector("label");
    function atualizarCampo() {
        if (input.value) {
            input.classList.add("tem_valor");
            label.classList.add("escondida");
        } else {
            input.classList.remove("tem_valor");
            if (document.activeElement !== input) {
                label.classList.remove("escondida");
            }
        }
    }
    input.addEventListener("focus", () => {
        label.classList.add("escondida");
    });
    input.addEventListener("blur", () => {
        atualizarCampo();
    });
    input.addEventListener("change", atualizarCampo);
    input.addEventListener("input", atualizarCampo);
    atualizarCampo();
});

// MOSTRAR CAMPO DE QUANTIDADE DE PARCELAS
function mostrarQuantidadeParcelas() {
    const select = document.getElementById("parcelado");
    const qntParcelas = document.getElementById("qnt_parcelas");

    if (select.value === "true") {
        qntParcelas.style.display = "block";       
        qntParcelas.required = true;
    } else {
        qntParcelas.required = false;
        qntParcelas.style.display = "none";

    }
}

// FORMATAR CAMPO DE VALOR PARA R$##.##
function formatarMoeda(input) {
    let value = input.value.replace(/\D/g, "");
    let number = parseFloat(value) / 100;
    if (isNaN(number)) {
        input.value = "";
        return;
    }
    input.value = number.toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL"
    });
}


// CADASTRO CATEGORIA / FORMA PAGAMENTO / LANCAMENTO / USUARIO
async function envioFormularioCadastro(event) {

    event.preventDefault();

    const formulario = document.getElementById("formulario")
    const dados = new FormData(formulario)

    const statusMensagem = document.querySelector("#status_mensagem");

    const tipo = formulario.dataset.tipo;
    const url = formulario.dataset.url;
    
    statusMensagem.classList.remove("mensagemSucesso", "mensagemErro")
    statusMensagem.textContent = "";
    
    if (dados){
        try {
            const resposta = await fetch(url,{
                method: 'POST',
                body: dados
            })
            if (!resposta.ok) {
                throw new Error('Erro na requisição: ' + resposta.status);
            }
            const resultado = await resposta.json();
            if (resultado.sucesso) {
                statusMensagem.classList.add("mensagemSucesso");
                statusMensagem.textContent = resultado.mensagem;
                setTimeout(() => {
                    statusMensagem.textContent = "Recarregando a página....";
                    setTimeout(() => {
                        window.location.reload();                         
                    }, 2000);
                }, 2000);
                  
            } else {
                statusMensagem.classList.add("mensagemErro");
                statusMensagem.textContent = resultado.mensagem;
            }
        } catch (erro) {
            console.error(erro);
            statusMensagem.classList.add("mensagemErro");
            statusMensagem.textContent = "Ocorreu um erro.";
        }
    }
}