from fastapi import Form, Depends, HTTPException, APIRouter, Request, Query
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from models import FormasPagamento, Usuario
from main import templates


rota_formaPagamento = APIRouter(prefix="/formaPagamento", tags=["formaPagamento"])


@rota_formaPagamento.get("/")
async def home(request: Request):
    """
    Essa é a rota padrão das formas de pagamentos.
    """
    return templates.TemplateResponse(request= request, name="forma_de_pagamento.html")


@rota_formaPagamento.post("/criar")
async def criar_formaPagamento(forma_pagamento: str = Form(...), 
                               responsavel: str = Form(...), 
                               vencimento: bool = Form(...), 
                               data_vencimento: int | None = Form(None), 
                               session: Session = Depends(pegar_sessao),
                               usuario: Usuario = Depends(verificar_token)):
    
    existe_formaPagamento = session.query(FormasPagamento).filter(
        FormasPagamento.forma_pagamento == forma_pagamento, 
        FormasPagamento.responsavel == responsavel).first()
    
    if existe_formaPagamento:
        raise HTTPException(status_code = 400, detail="Forma de pagamento já cadastrada para este responsável em sistema!")

    if not vencimento:
        data_vencimento = None
    if vencimento == True:
        if data_vencimento == "":
            raise HTTPException(status_code = 400, detail="Data de vencimento não informada.")


    nova_formaPagamento = FormasPagamento(id_usuario = usuario.id, forma_pagamento = forma_pagamento, responsavel = responsavel, status_forma_pagamento = "ATIVO", vencimento = vencimento, data_vencimento = data_vencimento)
    session.add(nova_formaPagamento)
    session.commit()

    return {"mensagem": f"A Categoria {forma_pagamento} foi cadastrada com sucesso para o responsável {responsavel}! "}


@rota_formaPagamento.post("/editar")
async def editar_formaPagamento(id_formaPagamento: int, 
                                forma_pagamento: str = Form(...), 
                                responsavel: str = Form(...), 
                                vencimento: bool = Form(...), 
                                data_vencimento: int | None = Form(None), 
                                status_forma_pagamento: str = Form(...), 
                                session: Session = Depends(pegar_sessao), 
                                usuario: Usuario = Depends(verificar_token)):
    
    FormaPagamento = session.query(FormasPagamento).filter(FormasPagamento.id == id_formaPagamento, FormasPagamento.id_usuario == usuario.id).first()
    
    if not FormaPagamento:
        raise HTTPException(status_code = 400, detail = "Forma de pagamento não cadastrada.")
    
    if status_forma_pagamento not in ["ATIVO", "INATIVO"]:
        raise HTTPException(status_code = 401, detail = "O status precisa ser ATIVO ou INATIVO.")
    
    FormaPagamento.forma_pagamento = forma_pagamento
    FormaPagamento.responsavel = responsavel
    FormaPagamento.vencimento = vencimento
    FormaPagamento.data_vencimento = data_vencimento
    FormaPagamento.status_forma_pagamento = status_forma_pagamento
    session.commit()

    return {"mensagem": f"A forma de pagamento foi alterada com sucesso!"}


@rota_formaPagamento.get("/listar")
async def listar_formaPagamento(forma_pagamento: str = Query(...),
                                responsavel: str = Query(...),
                                vencimento: bool = Query(...),
                                data_vencimento: int = Query(...),
                                status_forma_pagamento: str = Query(...),
                                session: Session = Depends(pegar_sessao), 
                                usuario: Usuario = Depends(verificar_token)):
    