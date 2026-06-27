from fastapi import APIRouter, Form, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from models import Debitos, Categorias, FormasPagamento, Usuarios, Parcelas
from main import templates
from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta


rota_debitos = APIRouter(prefix="/debitos", tags=["debitos"])

@rota_debitos.get("/")
async def home(request: Request, session: Session = Depends(pegar_sessao)):
    """
    Essa é a rota padrão das contas.
    """
    categorias = session.query(Categorias).all()
    formas_pagamento = session.query(FormasPagamento).all()


    return templates.TemplateResponse(
        name="debitos.html", 
        request=request, 
        context={
            "categorias": categorias,
            "formas_pagamento": formas_pagamento
        }
    )


@rota_debitos.post("/criar")
async def criar_debito(data_compra: date = Form(...), 
                      item_comprado: str = Form(...), 
                      categoria_id: int = Form(...),  
                      forma_pagamento: int = Form(...), 
                      valor_debito: str = Form(...),
                      parcelado: bool = Form(...), 
                      qnt_parcelas: int | None = Form(None), 
                      session: Session = Depends(pegar_sessao), 
                      usuario: Usuarios = Depends(verificar_token)):
    valor_debito = (valor_debito.replace("R$", "").replace(".", "").replace(",", ".").strip())
    valor_debito = Decimal(valor_debito)
    existeDebito = session.query(Debitos).filter(Debitos.data_compra == data_compra, 
                                                    Debitos.id_usuario == usuario.id,
                                                    Debitos.item_comprado == item_comprado, 
                                                    Debitos.id_forma_pagamento == forma_pagamento).first()
    if parcelado == False:
        qnt_parcelas = 1
    else:
        if qnt_parcelas == None or qnt_parcelas <= 0 :
            raise HTTPException(status_code = 400, detail = "A quantidade de parcelas precisa ser maior do que 0.")
    if existeDebito:
        return {"mensagem": "Compra adicionada com sucesso. - Já existe uma compra idêntica em sistema, por gentileza analise."}
    novoDebito = Debitos(id_usuario = usuario.id, data_compra = data_compra, item_comprado = item_comprado, id_categoria = categoria_id, id_forma_pagamento = forma_pagamento, valor_debito = valor_debito, parcelado = parcelado, qnt_parcelas = qnt_parcelas)
    session.add(novoDebito)
    session.flush()
    valor_total = Decimal(str(novoDebito.valor_debito))
    qtd = novoDebito.qnt_parcelas
    valor_base = (valor_total / qtd).quantize(Decimal("0.01"))
    for numero in range(1, qtd + 1):
        if numero < qtd:
            valor = valor_base
        else:
            valor = valor_total - (valor_base * (qtd - 1))
        dia_vencimento = novoDebito.formaPagamento.data_vencimento
        vencimento = None
        if dia_vencimento is not None:
            if numero <= 1: 
                if data_compra.day < dia_vencimento:
                    vencimento = (data_compra.replace(day = dia_vencimento) + relativedelta(months = 0))
            vencimento = (data_compra.replace(day = dia_vencimento) + relativedelta(months = numero))
        parcela = Parcelas(numero_parcela = numero,
                           valor_parcela = valor,
                           id_debito = novoDebito.id,
                           data_vencimento = vencimento
                           )
        session.add(parcela)
    session.commit()
    return {"mensagem": "Compra adicionada com sucesso!"}


@rota_debitos.patch("/editar")
async def editar_debito(id_debito: int,
                        item_comprado: str | None = Query(None),
                        categoria_id: int | None = Query(None),
                        forma_pagamento: int | None = Query(None),
                        valor_debito: str | None = Query(None),
                        parcelado: bool | None = Query(None),
                        qnt_parcelas: int | None = Query(None),
                        session: Session = Depends(pegar_sessao), 
                        usuario: Usuarios= Depends(verificar_token)):
    
    debito = session.query(Debitos).filter(Debitos.id == id_debito, Debitos.id_usuario == usuario.id).first()

    if not debito:
        raise HTTPException(status_code = 400, detail = "Débito não cadastrado")
    
    if item_comprado is not None:
        debito.item_comprado = item_comprado

    if categoria_id is not None:
        debito.id_categoria = categoria_id

    if forma_pagamento is not None:
        debito.id_forma_pagamento = forma_pagamento

    if valor_debito is not None and qnt_parcelas is None:
        valor_debito = (valor_debito.replace("R$", "").replace(".", "").replace(",", ".").strip())
        novo_valor = Decimal(str(valor_debito))
        debito.valor_debito = novo_valor
        if debito.parcelado:
            qtd = debito.qnt_parcelas
            valor_base = (novo_valor / qtd).quantize(Decimal("0.01"))
            for indice, parcela in enumerate(debito.parcela, start=1):
                if indice < qtd:
                    parcela.valor_parcela = valor_base
                else:
                    parcela.valor_parcela = novo_valor - (valor_base * (qtd - 1))
            session.commit()

    if valor_debito is None and qnt_parcelas is not None:
        valor_debito = Decimal(str(debito.valor_debito))
        if qnt_parcelas <= 0:
            raise HTTPException(status_code = 400, detail = "Quantidade de parcelas precisa ser maior do que 0")
        qtd = qnt_parcelas
        debito.qnt_parcelas = qtd
        dia_vencimento = debito.formaPagamento.data_vencimento
        debito.parcela.clear()
        valor_base = (valor_debito / qtd).quantize(Decimal("0.01"))

        for numero in range(1, qtd + 1):
            if numero < qtd:
                valor = valor_base
            else:
                valor = valor_debito - (valor_base * (qtd - 1))
            vencimento = (debito.data_compra.replace(day = dia_vencimento) + relativedelta(months = numero))
            parcela = Parcelas(numero_parcela = numero,
                            valor_parcela = valor,
                            id_debito = debito.id,
                            data_vencimento = vencimento
                            )
            session.add(parcela)
    

    if parcelado is not None:
        debito.parcelado = parcelado
        if parcelado is False:
            debito.qnt_parcelas = 1
            vencimento = (debito.data_compra.replace(day = debito.formaPagamento.data_vencimento) + relativedelta(months = 1))
            debito.parcela.clear()
            parcela = Parcelas(numero_parcela = 1,
                               valor_parcela = debito.valor_debito,
                               id_debito = debito.id,
                               data_vencimento = vencimento)
            session.add(parcela)

    
    session.commit()

    return {"mensagem": "Débito alterado com sucesso!"}
     

@rota_debitos.post("/cancelar/{id_debito}")
async def deletar_conta(id_debito: int, session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    conta = session.query(Debitos).filter(Debitos.id == id_debito).first()

    if not conta:
        raise HTTPException(status_code = 400, detail = "Conta não encontrada em sistema")
    
    if usuario.id != conta.id_usuario:
        raise HTTPException(status_code = 401, detail = "Usuário não tem permissão para excluir esta conta.")  
    
    for parcela in conta.parcela:
        parcela.status_parcela = "CANCELADO"
    session.commit()

    return {"mensagem": f"Conta excluída com sucesso! - ID da conta {conta.id}",
            "conta": conta}


@rota_debitos.get("/listar")
async def listar_debitos(data_compra_inicio: date | None = Query(None),
                         data_compra_final: date | None = Query(None),
                         data_vencimento_inicio: date | None = Query(None),
                         data_vencimento_final: date | None = Query(None),
                         status_debito: str | None = Query(None), 
                         id_categoria: int | None = Query(None), 
                         id_forma_pagamento: int | None = Query(None), 
                         session: Session = Depends(pegar_sessao), 
                         usuario: Usuarios = Depends(verificar_token)):
    query = session.query(Debitos).filter(Debitos.id_usuario == usuario.id)

    if data_compra_inicio is not None or data_compra_final is not None:
        if data_compra_inicio is None or data_compra_final is None:
            raise HTTPException(status_code= 400, detail="Precisa informar ambas datas.")
        query = query.filter(Debitos.data_compra >= data_compra_inicio, Debitos.data_compra <= data_compra_final)

    if data_vencimento_inicio is not None or data_vencimento_final is not None:
        if data_vencimento_inicio is None or data_vencimento_final is None:
            raise HTTPException(status_code= 400, detail="Precisa informar ambas datas.")
        query = query.join(Debitos.parcela).filter(Parcelas.data_vencimento >= data_vencimento_inicio, Parcelas.data_vencimento <= data_vencimento_final)

    if status_debito is not None:
        query = query.filter(Debitos.status_debito == status_debito)

    if id_categoria is not None:
        query = query.filter(Debitos.id_categoria == id_categoria)

    if id_forma_pagamento is not None:
        query = query.filter(Debitos.id_forma_pagamento == id_forma_pagamento)

    resultadoDebitos = query.all()

    if not resultadoDebitos:
        return {"mensagem": "Não existe dados com os filtros aplicados."}
    
    return {"Débitos": resultadoDebitos}


