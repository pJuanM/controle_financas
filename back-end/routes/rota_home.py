import calendar
from datetime import datetime
from decimal import Decimal
from urllib.parse import quote

from dependencies import pegar_sessao, verificar_token
from fastapi import APIRouter, Depends, Form, Request
from main import templates
from models import Categorias, FormasPagamento, Lancamentos, Parcelas, Usuarios
from sqlalchemy import extract
from sqlalchemy.orm import Session

rota_home = APIRouter(prefix="/home", tags=["home"], dependencies=[Depends(verificar_token)])


@rota_home.get("/")
async def homepage(request: Request,
                   session: Session = Depends(pegar_sessao),
                   usuario: Usuarios = Depends(verificar_token)):
    """
    Essa é a rota padrão das formas de pagamentos.
    """
    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")

    return templates.TemplateResponse(
            request = request,
            name = "home.html",
            context = {
                "parcelas" : None,

                "valor_pago": 0,
                "valor_pendente": 0,
                "valor_total": 0,
                "valor_credito": 0,
                "valor_debito": 0,
                "saldo": 0,

                "label_gastos_dia": [],
                "data_gastos_dia": [],

                "labels_mes": list(range(1, 13)),
                "data_gastos_mes": [0] * 12,
                "data_creditos_mes": [0] * 12,

                "label_gastos_categoria": [],
                "data_gastos_categoria": [],

                "label_gastos_forma_pagamento": [],
                "data_gastos_forma_pagamento": [],
            }
        )


@rota_home.post("/")
async def homepage(request: Request,
                   session: Session = Depends(pegar_sessao),
                   mes: int | None = Form(None),
                   ano: int | None = Form(None),
                   usuario: Usuarios = Depends(verificar_token)):


    if usuario is None:
            return templates.TemplateResponse(request= request, name="sem_login.html")
    
    # ======= VARIÁVEIS PARA INICIALIZAR VALORES =======
    valor_pago = 0
    valor_pendente = 0
    valor_credito = 0
    valor_debito = 0
    gastosMes = {}
    creditosMes = {}
    formasPagamento = {}
    categorias = {}
    gastosDia = {}
    mesesParcelas = []

    # ======= ALTERAR PARA O MES JÁ SER SORT, E ELE RECEBER UMA LISTA =======
    parcelas = session.query(Parcelas).join(Parcelas.lancamento).filter(Parcelas.status_parcela != "CANCELADO", Lancamentos.id_usuario == usuario.id)

    if ano:
        parcelas = parcelas.filter(extract('year', Parcelas.data_vencimento) == ano)
        mesesParcelas = session.query(Parcelas).join(Parcelas.lancamento).filter(
            Lancamentos.id_usuario == usuario.id, 
            Parcelas.status_parcela != "CANCELADO", 
            extract('year', Parcelas.data_vencimento) == ano)
    else:
        parcelas = parcelas.filter(extract('year', Parcelas.data_vencimento) == datetime.now().year)
        mesesParcelas = session.query(Parcelas).join(Parcelas.lancamento).filter(
            Lancamentos.id_usuario == usuario.id, 
            Parcelas.status_parcela != "CANCELADO", 
            extract('year', Parcelas.data_vencimento) == datetime.today().year)

    if mes:
        parcelas = parcelas.filter(extract('month', Parcelas.data_vencimento) == mes)



    # ======= LOOPING PRINCIPAL PARA ITERAR SOBRE CADA PARCELA =======
    for parcela in parcelas:
        formaPagamento = parcela.lancamento.formaPagamento.forma_pagamento
        categoria = parcela.lancamento.categoria.categoria
        dia = parcela.lancamento.data_compra.day
        valorParcela = parcela.valor_parcela

        if parcela.lancamento.tipo_lancamento == "DEBITO":
            if  parcela.lancamento.pagador_responsavel != usuario.nome:
                continue
            # ======= DICIONÁRIO DE GASTOS POR CATEGORIA =======
            if categoria not in categorias:
                categorias[categoria] = 0
            categorias[categoria] += float(valorParcela)

            # ======= DICIONÁRIO DE GASTOS POR FORMA DE PAGAMENTO =======
            if formaPagamento not in formasPagamento:
                formasPagamento[formaPagamento] = 0
            formasPagamento[formaPagamento] += float(valorParcela)

            # ======= DICIONARIO DE GASTOS POR DIA =======
            if dia not in gastosDia:
                gastosDia[dia] = 0
            gastosDia[dia] += float(valorParcela)

        # ======= PARCELAS POR STATUS PAGO OU PENDENTE E SALDO =======
            if parcela.status_parcela == "PAGO":
                valor_pago += valorParcela
            elif parcela.status_parcela == "PENDENTE":
                valor_pendente += valorParcela


        # ======= PARCELAS POR TIPO LANCAMENTO - CREDITO OU DEBITO =======
            valor_debito += valorParcela
        else:
            valor_credito += valorParcela
    valor_total = valor_pago + valor_pendente

    # ======= LOOPING SECUNDÁRIO ITERAR PARA TODOS OS MESES =======
    for mesParcelas in mesesParcelas:
        valorParcela = mesParcelas.valor_parcela
        numeroMes = mesParcelas.data_vencimento.month
        if mesParcelas.lancamento.tipo_lancamento == "DEBITO":
            if mesParcelas.lancamento.pagador_responsavel != usuario.nome:
                continue
            if numeroMes not in gastosMes:
                gastosMes[numeroMes] = 0
            gastosMes[numeroMes] += float(valorParcela)
        else:
            if numeroMes not in creditosMes:
                creditosMes[numeroMes] = 0
            creditosMes[numeroMes] += float(valorParcela)


    # ======= LISTA DE GASTOS POR CATEGORIA =======
    labelGastosCategoria = sorted(categorias.keys())
    dataGastosCategoria = [float(categorias[categoria]) for categoria in labelGastosCategoria]

    # ======= LISTA DE GASTOS POR FORMA DE PAGAMENTO =======
    labelGastosFormaPagamento = sorted(formasPagamento.keys())
    dataGastosFormaPagamento = [float(formasPagamento[formaPagamento]) for formaPagamento in labelGastosFormaPagamento]

    # ======= LISTA DE GASTOS POR DIA =======
    labelGastosDia = sorted(gastosDia.keys())
    dataGastosDia = [float(gastosDia[dia]) for dia in labelGastosDia]

    # ======= LISTA DE GASTOS POR MES =======
    labelsMes = list(range(1, 13))
    dataGastosMes = [float(gastosMes.get(numeroMes, 0)) for numeroMes in labelsMes]

    # ======= LISTA DE CREDITOS POR MES =======
    dataCreditosMes = [float(creditosMes.get(numeroMes, 0)) for numeroMes in labelsMes]

    # ======= SALDO =======
    saldo = valor_credito - valor_debito
    return templates.TemplateResponse(
        request = request,
        name = "home.html",
        context = {
            "mes": mes,
            "ano": ano,
            "parcelas": parcelas,

            # CARDS
            "valor_pago": valor_pago,
            "valor_pendente": valor_pendente,
            "valor_total": valor_total,
            "valor_credito": valor_credito,
            "valor_debito": valor_debito,
            "saldo": saldo,

            # LINHA
            "label_gastos_dia": labelGastosDia,
            "data_gastos_dia": dataGastosDia,

            # COLUNA
            "labels_mes" : labelsMes,
            "data_gastos_mes": dataGastosMes,
            "data_creditos_mes": dataCreditosMes,

            # BARRA HORIZONTAL
            "label_gastos_categoria": labelGastosCategoria,
            "data_gastos_categoria": dataGastosCategoria,

            # PIZZA
            "label_gastos_forma_pagamento": labelGastosFormaPagamento,
            "data_gastos_forma_pagamento": dataGastosFormaPagamento,

        }
    )