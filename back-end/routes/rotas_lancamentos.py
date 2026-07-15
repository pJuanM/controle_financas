from fastapi import APIRouter, Form, Depends, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from typing import Optional
from urllib.parse import quote
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from models import Lancamentos, Categorias, FormasPagamento, Usuarios, Parcelas
from main import templates
from decimal import Decimal
from datetime import date, datetime
import calendar
from dateutil.relativedelta import relativedelta


rota_lancamentos = APIRouter(prefix="/lancamentos", tags=["lancamentos"], dependencies=[Depends(verificar_token)])


@rota_lancamentos.get("/")
async def listar_lancamentos(request: Request,
                         data_compra_inicio: str | None = Query(None),
                         data_compra_final: str | None = Query(None),
                         data_vencimento_inicio: str | None = Query(None),
                         data_vencimento_final: str | None = Query(None),
                         id_categoria: list[int] | None = Query(None), 
                         id_forma_pagamento: list[int] | None = Query(None), 
                         tipo_lancamento: str | None = Query(None),
                         session: Session = Depends(pegar_sessao), 
                         usuario: Usuarios = Depends(verificar_token)):
    """
    Essa é a rota padrão das contas.
    """
    
    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")
    
    categorias = session.query(Categorias).all()
    formas_pagamento = session.query(FormasPagamento).all()
    
    filtros_aplicados = any([
        data_compra_inicio,
        data_compra_final,
        data_vencimento_inicio,
        data_vencimento_final,
        id_categoria,
        id_forma_pagamento,
        tipo_lancamento
    ])
    resultadoLancamentos = []
    valor_total = 0

    if filtros_aplicados:
        data_compra_inicio = data_compra_inicio or None 
        data_compra_final = data_compra_final or None 
        data_vencimento_inicio = data_vencimento_inicio or None 
        data_vencimento_final = data_vencimento_final or None 

        query = session.query(Lancamentos).join(Lancamentos.parcela).filter(Lancamentos.id_usuario == usuario.id, Parcelas.status_parcela != "CANCELADO")

        if data_compra_inicio or data_compra_final:
            if not data_compra_inicio or not data_compra_final:
                raise HTTPException(status_code= 400, detail="Precisa informar ambas datas compra.")
            query = query.filter(
                Lancamentos.data_compra >= datetime.strptime(data_compra_inicio, "%Y-%m-%d").date(), 
                Lancamentos.data_compra <= datetime.strptime(data_compra_final, "%Y-%m-%d")
            .date())

        if data_vencimento_inicio or data_vencimento_final:
            if not data_vencimento_inicio or not data_vencimento_final:
                raise HTTPException(status_code= 400, detail="Precisa informar ambas datas vencimento.")
            query = query.join(Lancamentos.parcela).filter(
                Parcelas.data_vencimento >= datetime.strptime(data_vencimento_inicio, "%Y-%m-%d").date(), 
                Parcelas.data_vencimento <= datetime.strptime(data_vencimento_final, "%Y-%m-%d").date()
            ).distinct()

        if id_categoria is not None:
            ids_categorias = [int(i) for i in id_categoria]
            query = query.filter(Lancamentos.id_categoria.in_(ids_categorias))

        if id_forma_pagamento is not None:
            formasPagamento = [int(i) for i in id_forma_pagamento]
            query = query.filter(Lancamentos.id_forma_pagamento.in_(formasPagamento))

        if tipo_lancamento is not None:
            query = query.filter(Lancamentos.tipo_lancamento == tipo_lancamento)

        resultadoLancamentos = query.all()
        valor_total = sum(lancamento.valor_lancamento for lancamento in resultadoLancamentos)

    return templates.TemplateResponse(
        name="lista_lancamentos.html", 
        request=request,    
        context={
            "lancamentos": resultadoLancamentos,
            "usuario": usuario,
            "filtros_aplicados": filtros_aplicados,
            "categorias": categorias,
            "formas_pagamento": formas_pagamento,
            "valor_total": valor_total,
            "data_compra_inicio" : data_compra_inicio,
            "data_compra_final" : data_compra_final,
            "data_vencimento_inicio" : data_vencimento_inicio,
            "data_vencimento_final" : data_vencimento_final,
            "id_categoria" : id_categoria,
            "id_forma_pagamento" : id_forma_pagamento,
            "tipo_lancamento" : tipo_lancamento,
        }
    )


@rota_lancamentos.get("/criar")
async def home(request: Request, 
               mensagem: Optional[str] = None,
               session: Session = Depends(pegar_sessao), 
               usuario: Usuarios = Depends(verificar_token)):
    

    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")
    categorias = session.query(Categorias).all()
    formas_pagamento = session.query(FormasPagamento).all()


    return templates.TemplateResponse(
        name="lancamentos.html", 
        request=request, 
        context={
            "categorias": categorias,
            "formas_pagamento": formas_pagamento,
            "usuario": usuario,
            "mensagem":mensagem
        }
    )


@rota_lancamentos.post("/criar")
async def criar_lancamento(data_compra: date = Form(...), 
                      item_comprado: str = Form(...), 
                      categoria_id: int = Form(...),  
                      forma_pagamento: int = Form(...), 
                      valor_lancamento: str = Form(...),
                      parcelado: bool = Form(...), 
                      tipo_lancamento: str = Form(...),
                      pagador_responsavel: str = Form(...),
                      qnt_parcelas: int | None = Form(None), 
                      session: Session = Depends(pegar_sessao), 
                      usuario: Usuarios = Depends(verificar_token)):
    

    valor_lancamento = (valor_lancamento.replace("R$", "").replace(".", "").replace(",", ".").strip())
    valor_lancamento = Decimal(valor_lancamento)
    existelancamento = session.query(Lancamentos).join(Lancamentos.parcela).filter(Lancamentos.data_compra == data_compra, 
                                                    Lancamentos.id_usuario == usuario.id,
                                                    Lancamentos.item_comprado == item_comprado,
                                                    Parcelas.status_parcela != "CANCELADO",
                                                    Lancamentos.tipo_lancamento == tipo_lancamento,
                                                    Lancamentos.valor_lancamento == valor_lancamento,
                                                    Lancamentos.id_forma_pagamento == forma_pagamento).first()
    if parcelado == False:
        qnt_parcelas = 1
    else:
        if qnt_parcelas == None or qnt_parcelas <= 0 :
            raise HTTPException(status_code = 400, detail = "A quantidade de parcelas precisa ser maior do que 0.")
        
    if existelancamento:
        return RedirectResponse(
            url = f"/lancamentos/criar?mensagem=Já existe uma compra idêntica.",
            status_code = 303
    )

    if tipo_lancamento == "DEBITO":
        pagador_responsavel = usuario.nome
    else:
        pagador_responsavel = pagador_responsavel
    
    
    novolancamento = Lancamentos(id_usuario = usuario.id, data_compra = data_compra, item_comprado = item_comprado, id_categoria = categoria_id, id_forma_pagamento = forma_pagamento, valor_lancamento = valor_lancamento, parcelado = parcelado, qnt_parcelas = qnt_parcelas, pagador_responsavel = pagador_responsavel, tipo_lancamento = tipo_lancamento)
    session.add(novolancamento)
    session.flush()

    valor_total = Decimal(str(novolancamento.valor_lancamento))
    qtd = novolancamento.qnt_parcelas
    valor_base = (valor_total / qtd).quantize(Decimal("0.01"))

    # ======= DT. VENC. PARCELAS COM BASE NO FECHAMENTO + COMPRA + VENCIMENTO =======
    dia_fechamento = novolancamento.formaPagamento.data_fechamento
    dia_vencimento = novolancamento.formaPagamento.data_vencimento

    if dia_fechamento is None or dia_vencimento is None:
        primeiro_vencimento = data_compra
    else:
        ultimo_dia = calendar.monthrange(data_compra.year, data_compra.month)[1]
        fechamento = date(
                data_compra.year,
                data_compra.month,
                min(dia_fechamento, ultimo_dia)
            )
        if data_compra < fechamento:
                ultimo_dia = calendar.monthrange(data_compra.year, data_compra.month)[1]
                primeiro_vencimento = date(
                    data_compra.year,
                    data_compra.month,
                    min(dia_vencimento, ultimo_dia)
                )
        else:
            proximo_mes = data_compra + relativedelta(months = 1)

            ultimo_dia = calendar.monthrange(proximo_mes.year, proximo_mes.month)[1]
            
            primeiro_vencimento = date(
                proximo_mes.year,
                proximo_mes.month,
                min(dia_vencimento, ultimo_dia)
                )

    
    for numero in range(1, qtd + 1):
        if numero < qtd:
            valor = valor_base
        else:
            valor = valor_total - (valor_base * (qtd - 1))
        
        vencimento = primeiro_vencimento + relativedelta(months = numero - 1)
            
        parcela = Parcelas(numero_parcela = numero,
                           valor_parcela = valor,
                           id_lancamento = novolancamento.id,
                           data_vencimento = vencimento,
                           )
        session.add(parcela)
    session.commit()
    mensagem = quote("Compra adicionada com sucesso!")
    return RedirectResponse(
        url = f"/lancamentos/criar?mensagem={mensagem}",
        status_code = 303
    )
    

@rota_lancamentos.post("/editar")
async def editar_lancamento(id_lancamento: int = Form(...),
                        item_comprado: str | None = Form(None),
                        data_compra: date = Form(...),
                        id_categoria: int | None = Form(None),
                        id_forma_pagamento: int | None = Form(None),
                        valor_lancamento: str | None = Form(None),
                        parcelado: bool | None = Form(None),
                        qnt_parcelas: int | None = Form(None),
                        pagador_responsavel: str | None = Form(None),
                        session: Session = Depends(pegar_sessao), 
                        usuario: Usuarios= Depends(verificar_token)):
    

    lancamento = session.query(Lancamentos).filter(Lancamentos.id == id_lancamento, Lancamentos.id_usuario == usuario.id).first()

    if not lancamento:
        raise HTTPException(status_code = 400, detail = "Lançamento não cadastrado")

    if data_compra is not None:
        lancamento.data_compra = data_compra
    
    if item_comprado is not None:
        lancamento.item_comprado = item_comprado

    if id_categoria is not None:
        lancamento.id_categoria = id_categoria

    if id_forma_pagamento is not None:
        lancamento.id_forma_pagamento = id_forma_pagamento

    if pagador_responsavel:
        lancamento.pagador_responsavel = pagador_responsavel

    if valor_lancamento is not None:
        valor_lancamento = (
            valor_lancamento.replace("R$", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )
        novo_valor = Decimal(valor_lancamento)
        lancamento.valor_lancamento = novo_valor

        if lancamento.parcelado:
            qtd = lancamento.qnt_parcelas
            valor_base = (novo_valor / qtd).quantize(Decimal("0.01"))

            for indice, parcela in enumerate(lancamento.parcela, start=1):
                if indice < qtd:
                    parcela.valor_parcela = valor_base
                else:
                    parcela.valor_parcela = novo_valor - (valor_base * (qtd - 1))


    if qnt_parcelas is not None and qnt_parcelas != lancamento.qnt_parcelas:
        if qnt_parcelas <= 0:
            raise HTTPException(
                status_code=400,
                detail="Quantidade de parcelas precisa ser maior do que 0"
            )

        valor_total = Decimal(str(lancamento.valor_lancamento))
        lancamento.qnt_parcelas = qnt_parcelas

        dia_vencimento = lancamento.formaPagamento.data_vencimento

        lancamento.parcela.clear()

        valor_base = (valor_total / qnt_parcelas).quantize(Decimal("0.01"))

        for numero in range(1, qnt_parcelas + 1):
            if numero < qnt_parcelas:
                valor = valor_base
            else:
                valor = valor_total - (valor_base * (qnt_parcelas - 1))

            vencimento = (
                lancamento.data_compra.replace(day=dia_vencimento)
                + relativedelta(months=numero)
            )

            parcela = Parcelas(
                numero_parcela=numero,
                valor_parcela=valor,
                id_lancamento=lancamento.id,
                data_vencimento=vencimento
            )

            session.add(parcela)
    
    if parcelado is not None:
        lancamento.parcelado = parcelado
        if parcelado is False:
            lancamento.qnt_parcelas = 1
            vencimento = (lancamento.data_compra.replace(day = lancamento.formaPagamento.data_vencimento) + relativedelta(months = 1))
            lancamento.parcela.clear()
            parcela = Parcelas(numero_parcela = 1,
                               valor_parcela = lancamento.valor_lancamento,
                               id_lancamento = lancamento.id,
                               data_vencimento = vencimento)
            session.add(parcela)

    
    session.commit()

    return {
        "sucesso": True,
        "mensagem": "Lançamento atualizado com sucesso!!",
        "item_comprado": lancamento.item_comprado,
        "data_compra": lancamento.data_compra,
        "valor_lancamento": f"R$ {lancamento.valor_lancamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    }
     

@rota_lancamentos.post("/excluir")
async def deletar_conta(id_lancamento: int = Form(...), 
                        session: Session = Depends(pegar_sessao), 
                        usuario: Usuarios = Depends(verificar_token)):
    
    
    conta = session.query(Lancamentos).filter(Lancamentos.id == id_lancamento).first()

    if not conta:
        raise HTTPException(status_code = 400, detail = "Conta não encontrada em sistema")
    
    if usuario.id != conta.id_usuario:
        raise HTTPException(status_code = 401, detail = "Usuário não tem permissão para excluir esta conta.")  
    
    for parcela in conta.parcela:
        parcela.status_parcela = "CANCELADO"
    session.commit()

    return {"mensagem": f"Conta excluída com sucesso! - ID da conta {conta.id}",
            "conta": conta}

