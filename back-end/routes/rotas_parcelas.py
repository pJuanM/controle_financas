from fastapi import APIRouter, Form, Depends, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from models import Usuarios, Parcelas, Debitos, FormasPagamento
from dependencies import pegar_sessao, verificar_token
from sqlalchemy.orm import Session
from datetime import date
from main import templates

rota_parcelas = APIRouter(prefix="/parcelas", tags=["parcela"], dependencies=[Depends(verificar_token)])


@rota_parcelas.get("/")
async def home(request: Request, 
               usuario: Usuarios = Depends(verificar_token)):
    """
    Essa é a rota padrão das parcelas
    """
    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")
    return templates.TemplateResponse(request= request, name="parcelas.html")

@rota_parcelas.get("/listar")
async def listar_parcelas(request: Request,
                          session: Session = Depends(pegar_sessao),
                          usuario: Usuarios = Depends(verificar_token),
                          data_vencimento: date | None = Query(None),
                          data_compra: date | None = Query(None),
                          id_categoria: int | None = Query(None),
                          id_forma_pagamento: int | None = Query(None),
                          responsavel: str | None = Query(None)):
    
    
    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")

    query = session.query(Parcelas).join(Parcelas.debito).filter(Debitos.id_usuario == usuario.id)

    if data_vencimento is not None:
        query = query.filter(Parcelas.data_vencimento == data_vencimento)

    if data_compra is not None:
        query = query.filter(Debitos.data_compra == data_compra)

    if id_categoria is not None:
        query = query.filter(Debitos.id_categoria == id_categoria)

    if id_forma_pagamento is not None:
        query = query.filter(Debitos.id_forma_pagamento == id_forma_pagamento)

    if responsavel is not None:
        query = query.join(Debitos.formaPagamento).filter(FormasPagamento.responsavel == responsavel)

    resultado_parcelas = query.all()

    if not resultado_parcelas:
        return {
            "mensagem": "Nenhuma parcela encontrada com os filtros aplicados."
        }
    resultado = []
    for parcela in resultado_parcelas:
        resultado.append({
            "Item Comprado": parcela.debito.item_comprado,
            "Parcelas": f"{parcela.numero_parcela}/{parcela.debito.qnt_parcelas}",
            "Valor Parcela": parcela.valor_parcela,
            "Forma de Pagamento": parcela.debito.formaPagamento.forma_pagamento,
            "Responsável": parcela.debito.formaPagamento.responsavel,
        })

    return {
        "Parcelas": resultado    
    }


@rota_parcelas.post("/editar")                        
async def editar_parcela(id_parcela: int,
                         session : Session = Depends(pegar_sessao),
                         usuario: Usuarios = Depends(verificar_token),
                         status_parcela: str | None = Form(...)):
    

    parcela = session.query(Parcelas).join(Parcelas.debito).filter(Parcelas.id == id_parcela, Debitos.id_usuario == usuario.id).first()

    if not parcela:
        raise HTTPException(status_code = 400, detail = "Parcela inexistente.")
    
    if status_parcela is not None:
        if status_parcela not in ["PAGO", "PENDENTE"]:
            raise HTTPException(status_code= 400, detail = "O status da parcela só pode ser PAGO ou PENDENTE.")
        parcela.status_parcela = status_parcela

    session.commit()

    return {
        "mensagem": "Status da parcela alterado com sucesso!"
    }
