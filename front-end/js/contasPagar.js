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