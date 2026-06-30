from fastapi import Form, Depends, HTTPException, APIRouter, Request, Query
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from models import FormasPagamento, Usuarios
from main import templates


rota_formasPagamento = APIRouter(prefix="/formaPagamento", tags=["formaPagamento"], dependencies=[Depends(verificar_token)])


@rota_formasPagamento.get("/")
async def home(request: Request, usuario: Usuarios = Depends(verificar_token)):
    """
    Essa é a rota padrão das formas de pagamentos.
    """
    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")
    return templates.TemplateResponse(request= request, name="forma_de_pagamento.html")


@rota_formasPagamento.post("/criar")
async def criar_formaPagamento(forma_pagamento: str = Form(...), 
                               responsavel: str = Form(...), 
                               data_vencimento: int | None = Form(None), 
                               session: Session = Depends(pegar_sessao),
                               usuario: Usuarios = Depends(verificar_token)):
    
    existe_formaPagamento = session.query(FormasPagamento).filter(
        FormasPagamento.forma_pagamento == forma_pagamento, 
        FormasPagamento.responsavel == responsavel).first()
    
    if existe_formaPagamento:
        raise HTTPException(status_code = 400, detail="Forma de pagamento já cadastrada para este responsável em sistema!")

    if data_vencimento == "":
        raise HTTPException(status_code = 422, detail="Data de vencimento não informada.")


    nova_formaPagamento = FormasPagamento(id_usuario = usuario.id, forma_pagamento = forma_pagamento, responsavel = responsavel, status_forma_pagamento = "ATIVO", data_vencimento = data_vencimento)
    session.add(nova_formaPagamento)
    session.commit()

    return {"mensagem": f"A Categoria {forma_pagamento} foi cadastrada com sucesso para o responsável {responsavel}! "}


@rota_formasPagamento.post("/editar")
async def editar_formaPagamento(id_formaPagamento: int, 
                                forma_pagamento: str = Form(...), 
                                responsavel: str = Form(...), 
                                data_vencimento: int | None = Form(None), 
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
    FormaPagamento.status_forma_pagamento = status_forma_pagamento
    session.commit()

    return {"mensagem": f"A forma de pagamento foi alterada com sucesso!"}


@rota_formasPagamento.post("/excluir/{formaPagamento_id}")
async def excluir_formaPagamento(formaPagamento_id: int, session: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    existeFormaPagamento = session.query(FormasPagamento).filter(FormasPagamento.id == formaPagamento_id, FormasPagamento.id_usuario == usuario.id).first()

    if not existeFormaPagamento:
        raise HTTPException(status_code = 401, detail = "Não existe essa forma de pagamento cadastrada para este usuário")
    
    existeFormaPagamento.status_forma_pagamento = "INATIVO"
    session.commit()

    return {"mensagem": "Forma de pagamento excluida com sucesso."}


@rota_formasPagamento.get("/listar")
async def listar_formaPagamento(request: Request,
                                forma_pagamento: str | None = Query(None),
                                responsavel: str | None = Query(None),
                                data_vencimento: str | None = Query(None),
                                status_forma_pagamento: str | None = Query(None),
                                session: Session = Depends(pegar_sessao), 
                                usuario: Usuarios = Depends(verificar_token)):
    
    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")
    
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

    if not formasDePagamento:
        formasDePagamento = []
    

    return templates.TemplateResponse(
        name="lista_formasPagamento.html", 
        request=request, 
        context={
            "formasDePagamento": formasDePagamento,
            "usuario": usuario
        }
    )

