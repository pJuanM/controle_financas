from typing import Optional
from urllib.parse import quote

from dependencies import pegar_sessao, verificar_token
from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from main import templates
from models import FormasPagamento, Usuarios
from sqlalchemy.orm import Session


rota_formasPagamento = APIRouter(prefix="/formaPagamento", tags=["formaPagamento"], dependencies=[Depends(verificar_token)])


@rota_formasPagamento.get("/")
async def listar_formaPagamento(request: Request,
                                forma_pagamento: str | None = Query(None),
                                responsavel: str | None = Query(None),
                                data_vencimento: str | None = Query(None),
                                data_fechamento: str | None = Query(None),
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
        data_fechamento,
        status_forma_pagamento
    ])
    formasDePagamento = []
    if filtros_aplicados:
        query = session.query(FormasPagamento).filter(FormasPagamento.id_usuario == usuario.id)
        if forma_pagamento:
            forma_pagamento = forma_pagamento.upper()
            query = query.filter(FormasPagamento.forma_pagamento == forma_pagamento)
        
        if responsavel:
            responsavel = responsavel.upper()
            query = query.filter(FormasPagamento.responsavel == responsavel)

        if data_vencimento:
            query = query.filter(FormasPagamento.data_vencimento == int(data_vencimento))

        if data_fechamento:
            query = query.filter(FormasPagamento.data_fechamento == int(data_fechamento))

        if status_forma_pagamento:
            query = query.filter(FormasPagamento.status_forma_pagamento == status_forma_pagamento)

        formasDePagamento = query.all()

    return templates.TemplateResponse(
        name="lista_formasPagamento.html", 
        request=request, 
        context={
            "formasDePagamento": formasDePagamento,
            "usuario": usuario,
            "forma_pagamento": forma_pagamento,
            "responsavel": responsavel,
            "data_vencimento": data_vencimento,
            "status_forma_pagamento": status_forma_pagamento,
            "data_fechamento": data_fechamento  
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
                               responsavel: str | None = Form(None), 
                               data_vencimento: int | None = Form(None),
                               data_fechamento: int | None = Form(None), 
                               session: Session = Depends(pegar_sessao),
                               usuario: Usuarios = Depends(verificar_token)):
    
    if not responsavel:
        responsavel = usuario.usuario

    
    existe_formaPagamento = session.query(FormasPagamento).filter(
        FormasPagamento.forma_pagamento == forma_pagamento.upper(), 
        FormasPagamento.responsavel == responsavel.upper()).first()
    
    if existe_formaPagamento:
        return {
            "sucesso": False,
            "mensagem": "Forma de Pagamento idêntica já cadastrada em sistema."
        }

    if data_vencimento is not None and not (1 <= data_vencimento <= 31):
        return {
            "sucesso": False,
            "mensagem": "Data de Vencimento precisa estar entre 1 e 31."
        }
    if data_fechamento is not None and not (1 <= data_fechamento <= 31):
        return {
            "sucesso": False,
            "mensagem": "Data de Fechamento precisa estar entre 1 e 31."
        }
        


    nova_formaPagamento = FormasPagamento(id_usuario = usuario.id, 
                                          forma_pagamento = forma_pagamento.upper(), 
                                          responsavel = responsavel.upper(), 
                                          status_forma_pagamento = "ATIVO", 
                                          data_vencimento = data_vencimento, 
                                          data_fechamento = data_fechamento)
    session.add(nova_formaPagamento)
    session.commit()
    return {
        "sucesso": True,
        "mensagem": "Forma de Pagamento criada com sucesso."
    }


@rota_formasPagamento.post("/editar")
async def editar_formaPagamento(id_formaPagamento: int = Form(...), 
                                forma_pagamento: str = Form(...), 
                                responsavel: str = Form(...), 
                                data_vencimento: int | None = Form(None), 
                                data_fechamento: int | None = Form(None),
                                status_forma_pagamento: str = Form(...), 
                                session: Session = Depends(pegar_sessao), 
                                usuario: Usuarios = Depends(verificar_token)):
    
    
    FormaPagamento = session.query(FormasPagamento).filter(
        FormasPagamento.id == id_formaPagamento, 
        FormasPagamento.id_usuario == usuario.id).first()
    
    if not FormaPagamento:
        return {
            "sucesso": False,
            "mensagem": "Forma de Pagamento não cadastrada ou INATIVA."
        }
        
    if forma_pagamento:
            forma_pagamento_existente = session.query(FormasPagamento).filter(
                FormasPagamento.forma_pagamento == forma_pagamento.upper(),
                FormasPagamento.id_usuario == usuario.id,
                FormasPagamento.id != FormaPagamento.id
            ).first()
            if forma_pagamento_existente:
                return {
                    "sucesso": False,
                    "mensagem": "Já existe uma Forma de Pagamento com este nome."
                }

    
    if status_forma_pagamento not in ["ATIVO", "INATIVO"]:
        return {
            "sucesso": False,
            "mensagem": "Status da Forma de Pagamento deve ser ATIVO ou INATIVO."
        }

    if data_vencimento is not None and not (1 <= data_vencimento <= 31):
        return {
            "sucesso": False,
            "mensagem": "Data de Vencimento precisa estar entre 1 e 31."
        }
    if data_fechamento is not None and not (1 <= data_fechamento <= 31):
        return {
            "sucesso": False,
            "mensagem": "Data de Fechamento precisa estar entre 1 e 31."
        }

        
    
    FormaPagamento.forma_pagamento = forma_pagamento.upper()
    FormaPagamento.responsavel = responsavel.upper()
    FormaPagamento.data_vencimento = data_vencimento
    FormaPagamento.data_fechamento = data_fechamento
    FormaPagamento.status_forma_pagamento = status_forma_pagamento.upper()
    session.commit()

    vencimento = ("À VISTA" if FormaPagamento.data_vencimento is None else FormaPagamento.data_vencimento)

    return {
        "sucesso": True,
        "mensagem": "Forma de pagamento editada com sucesso!",
        "formaPagamento": FormaPagamento.forma_pagamento,
        "responsavel": FormaPagamento.responsavel,
        "data_vencimento": vencimento,
        "status": FormaPagamento.status_forma_pagamento
    }


@rota_formasPagamento.post("/excluir")
async def excluir_formaPagamento(id_formaPagamento: int = Form(...), 
                                 session: Session = Depends(pegar_sessao), 
                                 usuario: Usuarios = Depends(verificar_token)):
    
    
    existeFormaPagamento = session.query(FormasPagamento).filter(FormasPagamento.id == id_formaPagamento, FormasPagamento.id_usuario == usuario.id).first()

    if not existeFormaPagamento:
        return {
            "sucesso": False,
            "mensagem": "Não existe esta Forma de Pagamento cadastrada para este usuário."
        }
    
    existeFormaPagamento.status_forma_pagamento = "ATIVO"
    session.commit()

    return {
        "sucesso": True,
        "mensagem": "Forma de pagamento excluida com sucesso."
    }


