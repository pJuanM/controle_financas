function mostrarCampoDataVencimento() {
    const select = document.getElementById("vencimento");
    const dataVencimento = document.getElementById("data_vencimento");

    if (select.value === "true") {
        dataVencimento.style.display = "block";      
        dataVencimento.required = true;
    } else {
        dataVencimento.required = false;

        dataVencimento.style.display = "none";
    }
}