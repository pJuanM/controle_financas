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

