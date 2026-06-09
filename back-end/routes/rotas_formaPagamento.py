from fastapi import Form, Depends, HTTPException, APIRouter, Request
from sqlalchemy.orm import Session
from dependencies import pegar_sessao
from models import FormaPagamento
from main import templates


rota_formaPagamento = APIRouter(prefix="/formaPagamento", tags=["formaPagamento"])


@rota_formaPagamento.get("/")
async def home(request: Request):
    """
    Essa é a rota padrão das formas de pagamentos.
    """
    return templates.TemplateResponse(request= request, name="forma_de_pagamento.html")


@rota_formaPagamento.post("/criarFormaPagamento")
async def criar_formaPagamento(forma_pagamento: str = Form(...), 
                               responsavel: str = Form(...), 
                               vencimento: bool = Form(...), 
                               data_vencimento: int | None = Form(None), 
                               session: Session = Depends(pegar_sessao)):
    existe_formaPagamento = session.query(FormaPagamento).filter(
        FormaPagamento.forma_pagamento == forma_pagamento, 
        FormaPagamento.responsavel == responsavel).first()
    
    if existe_formaPagamento:
        raise HTTPException(status_code = 400, detail="Forma de pagamento já cadastrada para este responsável em sistema!")

    if not vencimento:
        data_vencimento = None
    if vencimento == True:
        if data_vencimento != "":
            raise HTTPException(status_code = 400, detail="Data de vencimento não informada.")


    nova_formaPagamento = FormaPagamento(forma_pagamento = forma_pagamento, responsavel = responsavel, vencimento = vencimento, data_vencimento = data_vencimento)
    session.add(nova_formaPagamento)
    session.commit()

    return {"mensagem": f"A Categoria {forma_pagamento} foi cadastrada com sucesso para o responsável {responsavel}! "}
