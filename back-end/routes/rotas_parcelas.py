from datetime import datetime
from io import BytesIO
from typing import Optional
from urllib.parse import quote

import pandas as pd
from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from dependencies import pegar_sessao, verificar_token
from main import templates
from models import Categorias, FormasPagamento, Lancamentos, Parcelas, Usuarios



rota_parcelas = APIRouter(prefix="/parcelas", tags=["parcela"], dependencies=[Depends(verificar_token)])


def gerar_excel(parcelas):
    dados = []
    for parcela in parcelas:
        dados.append({
            "ID": parcela.id,
            "ITEM": parcela.lancamento.item_comprado,
            "DATA DA COMPRA": parcela.lancamento.data_compra,
            "DATA DE VENCIMENTO": parcela.data_vencimento,
            "FORMA DE PAGAMENTO": parcela.lancamento.formaPagamento.forma_pagamento,
            "CATEGORIA": parcela.lancamento.categoria.categoria,
            "VALOR": parcela.valor_parcela,
            "PAGADOR RESPONSAVEL": parcela.lancamento.pagador_responsavel,
            "PARCELA": f"{parcela.numero_parcela}/{parcela.lancamento.qnt_parcelas}",
            "STATUS": parcela.status_parcela,
        })
    df = pd.DataFrame(dados)

    arquivo = BytesIO()

    with pd.ExcelWriter(arquivo, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Parcelas"
        )
    arquivo.seek(0)

    return StreamingResponse(
        arquivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="parcelas.xlsx"'
            }
    )

@rota_parcelas.get("/")
async def listar_parcelas(request: Request,
                          session: Session = Depends(pegar_sessao),
                          usuario: Usuarios = Depends(verificar_token),
                          data_compra_inicio: str | None = Query(None),
                          data_compra_final: str | None = Query(None),
                          data_vencimento_inicio: str | None = Query(None),
                          data_vencimento_final: str | None = Query(None),
                          status_parcela: list[str] | None = Query(None),
                          id_forma_pagamento: list[int] | None = Query(None),
                          id_categoria: list[int] | None = Query(None),
                          acao: str | None = Query(None),
                          pagador_responsavel: list[str] | None = Query(None)):
    
    
    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")
    
    categorias = session.query(Categorias).filter(Categorias.id_usuario == usuario.id)
    lancamentos = [responsavel.pagador_responsavel for responsavel in session.query(Lancamentos.pagador_responsavel).filter(Lancamentos.id_usuario == usuario.id).distinct().all()]
    lancamentos.sort()
    formas_pagamento = session.query(FormasPagamento).filter(FormasPagamento.id_usuario == usuario.id)

    filtros_aplicados = any([
        data_compra_inicio,
        data_compra_final,
        data_vencimento_inicio,
        data_vencimento_final,
        status_parcela,
        id_forma_pagamento,
        id_categoria,
        pagador_responsavel,
    ])
    resultado_parcelas = []
    valor_total = 0

    if filtros_aplicados:
        query = session.query(Parcelas).join(Parcelas.lancamento).filter(Lancamentos.id_usuario == usuario.id)

        if data_compra_inicio or data_compra_final:
            if not data_compra_inicio or not data_compra_final  :
                raise HTTPException(status_code= 400, detail="Precisa informar ambas datas compra.")
            query = query.filter(
                Lancamentos.data_compra >= datetime.strptime(data_compra_inicio, "%Y-%m-%d").date(), 
                Lancamentos.data_compra <= datetime.strptime(data_compra_final, "%Y-%m-%d").date()
            )

        if data_vencimento_inicio or data_vencimento_final:
            if not data_vencimento_inicio or not data_vencimento_final:
                    raise HTTPException(status_code= 400, detail="Precisa informar ambas datas vencimento.")
            query = query.filter(
                    Parcelas.data_vencimento >= datetime.strptime(data_vencimento_inicio, "%Y-%m-%d").date(), 
                    Parcelas.data_vencimento <= datetime.strptime(data_vencimento_final, "%Y-%m-%d").date()
                )

        if status_parcela:
            query = query.filter(Parcelas.status_parcela.in_(status_parcela))

        if id_forma_pagamento:
            query = query.filter(Lancamentos.id_forma_pagamento.in_(id_forma_pagamento))

        if id_categoria:
            ids_categorias = [int(i) for i in id_categoria]
            query = query.filter(Lancamentos.id_categoria.in_(ids_categorias))

        if pagador_responsavel:
            query = query.filter(Lancamentos.pagador_responsavel.in_(pagador_responsavel))

        resultado_parcelas = query.all()
        valor_total = sum(parcela.valor_parcela for parcela in resultado_parcelas)
    if acao == "excel":
        return gerar_excel(resultado_parcelas)

    return templates.TemplateResponse(
        name="parcelas.html", 
        request=request, 
        context={
            "usuario": usuario,
            "parcelas": resultado_parcelas, 
            "lancamentos": lancamentos,
            "valor_total": valor_total,
            "filtros_aplicados": filtros_aplicados,
            "categorias": categorias,
            "formas_pagamento": formas_pagamento,
            "data_compra_inicio": data_compra_inicio,
            "data_compra_final": data_compra_final,
            "data_vencimento_inicio": data_vencimento_inicio,
            "data_vencimento_final": data_vencimento_final,
            "status_parcela": status_parcela,
            "id_forma_pagamento": id_forma_pagamento,
            "id_categoria": id_categoria,
            "pagador_responsavel": pagador_responsavel,
        }
    )


@rota_parcelas.post("/editar")                        
async def editar_parcela(id_parcela: int = Form(...),
                         session : Session = Depends(pegar_sessao),
                         usuario: Usuarios = Depends(verificar_token),
                         status_parcela: str | None = Form(None)):
    

    parcela = session.query(Parcelas).join(Parcelas.lancamento).filter(Parcelas.id == id_parcela, Lancamentos.id_usuario == usuario.id).first()
    if not parcela:
        raise HTTPException(status_code = 400, detail = "Parcela inexistente.")
    
    if status_parcela:
        if status_parcela not in ["PAGO", "PENDENTE",]:
            raise HTTPException(status_code= 400, detail = "O status da parcela só pode ser PAGO ou PENDENTE.")
        parcela.status_parcela = status_parcela

    session.commit()
    return {
        "sucesso": True,
        "mensagem": "Parcela alterada com sucesso!",
    }


