// VALIDAR SE A SENHA + CONFIRMAR SENHA SÃO IGUAIS
function senhaIgual() {
    const senha = document.querySelector("[data-senha]");
    const confirmeSenha = document.querySelector("[data-confirme-senha]");
    const erro = document.getElementById("erroSenha");

    if (!senha || !confirmeSenha || !erro) {
        return;
    }

    function validarSenha() {
        const iguais = senha.value === confirmeSenha.value;
        erro.textContent = iguais
            ? ""
            : "As senhas não coincidem.";
        return iguais;
    }

    senha.addEventListener("input", validarSenha);
    confirmeSenha.addEventListener("input", validarSenha);

    const formulario = senha.closest("form");
    formulario.addEventListener("submit", function(event) {
        if (!validarSenha()) {
            event.preventDefault();
        }
    });
}
senhaIgual();

// FUNÇÃO PARA CADASTRAR USUÁRIO
async function cadastrarUsuario(event){

    event.preventDefault();

    const formulario = document.getElementById("formulario");
    const mensagemCadastro = document.getElementById("mensagemCadastro");
    const botao = document.getElementById("enviar_formulario");

    const dadosFormulario = new FormData(formulario);

    if (!formulario.checkValidity()) {
        formulario.reportValidity();
        return; 
    }

    botao.disabled = true;
    botao.innerHTML = `
        <span class="spinner"></span>
        Cadastrando...
    `;

    mensagemCadastro.textContent = "";
    mensagemCadastro.classList.remove("mensagemSucesso", "mensagemErro");
    try {
        const resposta = await fetch(formulario.action, {
            method: "POST",
            body: dadosFormulario
        });

        const dados = await resposta.json();
        if (dados.sucesso) {

            botao.innerHTML = "Cadastro realizado!";
            mensagemCadastro.textContent = dados.mensagem;
            mensagemCadastro.classList.add("mensagemSucesso");

            setTimeout(() => {
                window.location.href = "/usuario/login";
            }, 3000);
        } else {
            botao.disabled = false;
            botao.innerHTML = "Enviar Cadastro";
            mensagemCadastro.textContent = dados.mensagem;
            mensagemCadastro.classList.add("mensagemErro");

        }
    } catch (erro) {
        console.error(erro)
        botao.disabled = false;
        botao.innerHTML = "Enviar Cadastro";
        mensagemCadastro.textContent = "Erro ao tentar comunicar com o servidor.";
        mensagemCadastro.classList.add("mensagemErro");

    }
}

