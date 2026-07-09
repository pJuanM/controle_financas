from fastapi import Form, Depends, HTTPException, APIRouter, Request, Query
from fastapi.responses import RedirectResponse
from urllib.parse import quote
from typing import Optional
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from models import FormasPagamento, Usuarios
from main import templates


rota_formasPagamento = APIRouter(prefix="/formaPagamento", tags=["formaPagamento"], dependencies=[Depends(verificar_token)])


@rota_formasPagamento.get("/")
async def listar_formaPagamento(request: Request,
                                forma_pagamento: str | None = Query(None),
                                responsavel: str | None = Query(None),
                                data_vencimento: str | None = Query(None),
                                status_forma_pagamento: str | None = Query(None),
                                session: Session = Depends(pegar_sessao), 
                                usuario: Usuarios = Depends(verificar_token)):
    """
    Essa é a rota padrão das formas de pagamentos.
    """
    
    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")
    
    filtros_aplicados = any([
        forma_pagamento,
        responsavel,
        data_vencimento,
        status_forma_pagamento
    ])
    formasDePagamento = []
    if filtros_aplicados:
        query = session.query(FormasPagamento).filter(FormasPagamento.id_usuario == usuario.id)
        if forma_pagamento:
            query = query.filter(FormasPagamento.forma_pagamento == forma_pagamento)
        
        if responsavel:
            query = query.filter(FormasPagamento.responsavel == responsavel)

        if data_vencimento:
            query = query.filter(FormasPagamento.data_vencimento == int(data_vencimento))

        if status_forma_pagamento:
            query = query.filter(FormasPagamento.status_forma_pagamento == status_forma_pagamento)

        formasDePagamento = query.all()

    return templates.TemplateResponse(
        name="lista_formasPagamento.html", 
        request=request, 
        context={
            "formasDePagamento": formasDePagamento,
            "usuario": usuario
        }
    )


@rota_formasPagamento.get("/criar")
async def home(request: Request, 
               mensagem: Optional[str] = None,
               usuario: Usuarios = Depends(verificar_token)):
    

    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")

    return templates.TemplateResponse(
        name="forma_de_pagamento.html", 
        request=request, 
        context={
            "usuario": usuario,
            "mensagem":mensagem
        }
    )


@rota_formasPagamento.post("/criar")
async def criar_formaPagamento(forma_pagamento: str = Form(...), 
                               responsavel: str = Form(...), 
                               data_vencimento: int | None = Form(None),
                               data_fechamento: int | None = Form(None), 
                               session: Session = Depends(pegar_sessao),
                               usuario: Usuarios = Depends(verificar_token)):
    

    existe_formaPagamento = session.query(FormasPagamento).filter(
        FormasPagamento.forma_pagamento == forma_pagamento, 
        FormasPagamento.responsavel == responsavel).first()
    
    if existe_formaPagamento:
        mensagem = quote("Já existe uma forma de pagamento idêntica.")
        return RedirectResponse(
            url = f"/formaPagamento/criar?mensagem={mensagem}",
            status_code = 303
        )

    if data_vencimento == "":
        return RedirectResponse(
            url = f"/formaPagamento/criar?mensagem=Data de vencimento não informada.",
            status_code = 303
        )


    nova_formaPagamento = FormasPagamento(id_usuario = usuario.id, forma_pagamento = forma_pagamento, responsavel = responsavel, status_forma_pagamento = "ATIVO", data_vencimento = data_vencimento, data_fechamento = data_fechamento)
    session.add(nova_formaPagamento)
    session.commit()
    mensagem = quote("Forma de pagamento cadastrada com sucesso.")
    return RedirectResponse(
        url = f"/formaPagamento/criar?mensagem={mensagem}",
        status_code = 303,
    )


@rota_formasPagamento.post("/editar")
async def editar_formaPagamento(id_formaPagamento: int = Form(...), 
                                forma_pagamento: str = Form(...), 
                                responsavel: str = Form(...), 
                                data_vencimento: int | None = Form(None), 
                                data_fechamento: int | None = Form(None),
                                status_forma_pagamento: str = Form(...), 
                                session: Session = Depends(pegar_sessao), 
                                usuario: Usuarios = Depends(verificar_token)):
    
    
    FormaPagamento = session.query(FormasPagamento).filter(FormasPagamento.id == id_formaPagamento, FormasPagamento.id_usuario == usuario.id).first()
    if not FormaPagamento:
        raise HTTPException(status_code = 400, detail = "Forma de pagamento não cadastrada.")
    
    if status_forma_pagamento not in ["ATIVO", "INATIVO"]:
        raise HTTPException(status_code = 401, detail = "O status precisa ser ATIVO ou INATIVO.")
    
    FormaPagamento.forma_pagamento = forma_pagamento
    FormaPagamento.responsavel = responsavel
    FormaPagamento.data_vencimento = data_vencimento
    FormaPagamento.data_fechamento = data_fechamento
    FormaPagamento.status_forma_pagamento = status_forma_pagamento
    session.commit()

    return RedirectResponse(
        "/formaPagamento",
        status_code=303
    )


@rota_formasPagamento.post("/excluir")
async def excluir_formaPagamento(id_formaPagamento: int = Form(...), 
                                 session: Session = Depends(pegar_sessao), 
                                 usuario: Usuarios = Depends(verificar_token)):
    
    
    existeFormaPagamento = session.query(FormasPagamento).filter(FormasPagamento.id == id_formaPagamento, FormasPagamento.id_usuario == usuario.id).first()

    if not existeFormaPagamento:
        raise HTTPException(status_code = 401, detail = "Não existe essa forma de pagamento cadastrada para este usuário")
    
    existeFormaPagamento.status_forma_pagamento = "INATIVO"
    session.commit()

    return {"mensagem": "Forma de pagamento excluida com sucesso."}


