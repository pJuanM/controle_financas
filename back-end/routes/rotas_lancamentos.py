from datetime import date, datetime
from decimal import Decimal
from urllib.parse import quote
from typing import Optional
import calendar
import re

import pandas as pd
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse
from io import BytesIO
from ofxparse import OfxParser
from sqlalchemy.orm import Session

from dependencies import pegar_sessao, verificar_token
from main import templates
from models import Categorias, FormasPagamento, Lancamentos, Parcelas, Usuarios

rota_lancamentos = APIRouter(prefix="/lancamentos", tags=["lancamentos"], dependencies=[Depends(verificar_token)])


# === FUNÇÃO PARA CALCULAR VENCIMENTO DE PARCELAS ===
def calcular_primeiro_vencimento(data_compra, forma_pagamento):
    dia_fechamento = forma_pagamento.data_fechamento
    dia_vencimento = forma_pagamento.data_vencimento

    if dia_fechamento is None or dia_vencimento is None:
        return data_compra
    
    ultimo_dia = calendar.monthrange(data_compra.year, data_compra.month)[1]

    fechamento = date(data_compra.year, 
                      data_compra.month,
                      min(dia_fechamento, ultimo_dia))

    if data_compra < fechamento:
        ultimo_dia = calendar.monthrange(data_compra.year, data_compra.month)[1]
        return date(
            data_compra.year,
            data_compra.month,
            min(dia_vencimento, ultimo_dia)
        )
    proximo_mes = data_compra + relativedelta(months=1)

    ultimo_dia = calendar.monthrange(proximo_mes.year, proximo_mes.month)[1]

    return date(
        proximo_mes.year,
        proximo_mes.month,
        min(dia_vencimento, ultimo_dia)
    )   


# === FUNÇÃO PARA IDENTIFICAR SE ALGUMA CATEGORIA CORRESPONDE AO LANÇAMENTO ===
def encontrar_categoria(descricao_lancamento,
                        usuario_id,
                        session):
    categorias = (
        session.query(Categorias).filter(Categorias.id_usuario == usuario_id, 
                                         Categorias.status_categoria == "ATIVO")
    ).all()

    descricao_upper = descricao_lancamento.upper()

    for categoria in categorias:
        if categoria.categoria.upper() == "AVULSO":
            continue

        palavras_chave = re.split(r"[,|]", categoria.descricao.upper())

        for palavra in palavras_chave:
            palavra = palavra.strip()

            if not palavra:
                continue

            padrao = r"\b" + re.escape(palavra) + r"\b"

            if re.search(padrao, descricao_upper):
                return categoria.id

    categoria_avulso = (
        session.query(Categorias)
        .filter(
            Categorias.id_usuario == usuario_id,
            Categorias.categoria == "AVULSO",
            Categorias.status_categoria == "ATIVO"
        )
        .first()
    )

    if categoria_avulso:
        return categoria_avulso.id
    categoria_avulso = Categorias(id_usuario = usuario_id, 
                                categoria = "AVULSO", 
                                status_categoria = "ATIVO", 
                                descricao = "LANÇAMENTOS QUE NÃO POSSUEM UMA CATEGORIA PRÉ ESTABELECIDA.")
    session.add(categoria_avulso)
    session.flush()
    return categoria_avulso.id


# === FUNÇÃO PARA GERAR O EXCEL DA ROTA ===
def gerar_excel(lancamentos):
    dados = []
    for lancamento in lancamentos:
        dados.append({
            "ID": lancamento.id,
            "Data da compra": lancamento.data_compra,
            "Item": lancamento.item_comprado,
            "Categoria": lancamento.categoria.categoria,
            "Forma de pagamento": lancamento.formaPagamento.forma_pagamento,
            "Valor": float(lancamento.valor_lancamento),
            "Parcelado": "SIM" if lancamento.parcelado else "NÃO",
            "Quantidade de parcelas": lancamento.qnt_parcelas,
            "Pagador": lancamento.pagador_responsavel,
            "Tipo": lancamento.tipo_lancamento,
        })

    df = pd.DataFrame(dados)
    arquivo = BytesIO()

    with pd.ExcelWriter(arquivo, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Lançamentos"
        )
    arquivo.seek(0)

    return StreamingResponse(
        arquivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="lancamentos.xlsx"'
            }
    )

# === ROTA PRINCIPAL DE LANÇAMENTOS VISUAL ===
@rota_lancamentos.get("/")
async def listar_lancamentos(request: Request,
                         data_compra_inicio: str | None = Query(None),
                         data_compra_final: str | None = Query(None),
                         data_vencimento_inicio: str | None = Query(None),
                         data_vencimento_final: str | None = Query(None),
                         id_categoria: list[int] | None = Query(None), 
                         id_forma_pagamento: list[int] | None = Query(None),
                         tipo_lancamento: list[str] | None = Query(None),
                         session: Session = Depends(pegar_sessao),
                         acao: str | None = Query(None),
                         usuario: Usuarios = Depends(verificar_token)):
    """
    Essa é a rota padrão das contas.
    """
    
    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")
    categorias = session.query(Categorias).filter(Categorias.id_usuario == usuario.id)
    formas_pagamento = session.query(FormasPagamento).filter(FormasPagamento.id_usuario == usuario.id)
    
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
            query = query.filter(Lancamentos.tipo_lancamento.in_(tipo_lancamento))

        resultadoLancamentos = query.all()
        valor_total = sum(lancamento.valor_lancamento for lancamento in resultadoLancamentos)
    if acao == "excel":
        return gerar_excel(resultadoLancamentos)
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


# === ROTA DE CRIAR LANÇAMENTOS VISUAL ===
@rota_lancamentos.get("/criar")
async def home(request: Request, 
               mensagem: Optional[str] = None,
               session: Session = Depends(pegar_sessao), 
               usuario: Usuarios = Depends(verificar_token)):
    

    if usuario is None:
        return templates.TemplateResponse(request= request, name="sem_login.html")
    categorias = session.query(Categorias).filter(Categorias.id_usuario == usuario.id)
    formas_pagamento = session.query(FormasPagamento).filter(FormasPagamento.id_usuario == usuario.id)
    formas_pagamento = formas_pagamento.order_by(FormasPagamento.responsavel)


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


# === ROTA DE CRIAR LANÇAMENTOS ===
@rota_lancamentos.post("/criar")
async def criar_lancamento(data_compra: date = Form(...), 
                      item_comprado: str = Form(...), 
                      categoria_id: int = Form(...),  
                      forma_pagamento: int = Form(...), 
                      valor_lancamento: str = Form(...),
                      parcelado: bool = Form(...), 
                      tipo_lancamento: str = Form(...),
                      pagador_responsavel: str | None = Form(None),
                      qnt_parcelas: int | None = Form(None), 
                      session: Session = Depends(pegar_sessao), 
                      usuario: Usuarios = Depends(verificar_token)):
    

    valor_lancamento = (valor_lancamento.replace("R$", "").replace(".", "").replace(",", ".").strip())
    valor_lancamento = Decimal(valor_lancamento)
    existelancamento = session.query(Lancamentos).join(Lancamentos.parcela).filter(
                                    Lancamentos.data_compra == data_compra, 
                                    Lancamentos.id_usuario == usuario.id,
                                    Lancamentos.item_comprado == item_comprado.upper(),
                                    Parcelas.status_parcela != "CANCELADO",
                                    Lancamentos.tipo_lancamento == tipo_lancamento,
                                    Lancamentos.valor_lancamento == valor_lancamento,
                                    Lancamentos.pagador_responsavel == pagador_responsavel,
                                    Lancamentos.id_forma_pagamento == forma_pagamento).first()
    if parcelado == False:
        qnt_parcelas = 1
    else:
        if qnt_parcelas == None or qnt_parcelas <= 0 :
            return {
                "sucesso": False,
                "mensagem": "A quantidade de parcelas precisa ser maior do que 0."
            }

        
    if existelancamento:
        return {
            "sucesso": False,
            "mensagem": "Já existe uma compra idêntica a esta em sistema."
        }

    if tipo_lancamento == "DEBITO":
        if not pagador_responsavel:
            pagador_responsavel = usuario.nome
        else:
            pagador_responsavel = pagador_responsavel.upper()
    else:
        if pagador_responsavel:
            pagador_responsavel = pagador_responsavel.upper()
        else:
            return {
                "sucesso": False,
                "mensagem": "Precisa declarar responsável por pagamento quando se é um CRÉDITO."
            }
    
    item_comprado = item_comprado.upper()
    pagador_responsavel = pagador_responsavel.upper()
    novolancamento = Lancamentos(id_usuario = usuario.id, 
                                 data_compra = data_compra, 
                                 item_comprado = item_comprado, 
                                 id_categoria = categoria_id, 
                                 id_forma_pagamento = forma_pagamento, 
                                 valor_lancamento = valor_lancamento, 
                                 parcelado = parcelado, 
                                 qnt_parcelas = qnt_parcelas, 
                                 pagador_responsavel = pagador_responsavel, 
                                 tipo_lancamento = tipo_lancamento)
    session.add(novolancamento)
    session.flush()

    valor_total = Decimal(str(novolancamento.valor_lancamento))
    qtd = novolancamento.qnt_parcelas
    valor_base = (valor_total / qtd).quantize(Decimal("0.01"))
    primeiro_vencimento = calcular_primeiro_vencimento(data_compra, novolancamento.formaPagamento)
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

    return {
        "sucesso": True,
        "mensagem": "Lançamento adicionado com sucesso."
    }
    

# === ROTA DE IMPORTAÇÃO OFX VISUAL ===
@rota_lancamentos.get("/importacao")
def tela_importacao(
    request: Request,
    session: Session = Depends(pegar_sessao),
    usuario: Usuarios = Depends(verificar_token)
):
    if usuario is None:
            return templates.TemplateResponse(request= request, name="sem_login.html")
    
    return templates.TemplateResponse(name="importacao.html", request = request, 
                                      context= {
                                        "request": request
                                        })


# === ROTA DE IMPORTAÇÃO OFX ===
@rota_lancamentos.post("/importacao/ofx")
async def importar_ofx(request: Request, 
                        arquivo: UploadFile = File(...), 
                        confirmar_nubank: bool = Form(False),
                        data_vencimento: int | None = Form(None),
                        data_fechamento: int | None = Form(None),
                        usuario: Usuarios = Depends(verificar_token),
                        session: Session = Depends(pegar_sessao)):
    # === VERIFICAR SE ESTÁ LOGADO ===
    if usuario is None:
        return templates.TemplateResponse(request = request, name = "sem_login.html")

    # === INTERPRETAR ARQUIVO UPADO ===
    if not arquivo.filename:
        raise HTTPException(
            status_code = 400,
            detail="Nenhum arquivo foi selecionado"
        )
    if not arquivo.filename.lower().endswith(".ofx"):
        raise HTTPException(
            status_code = 400,
            detail = "Necessário ser arquivo .ofx"
        )

    arquivo.file.seek(0)
    ofx = OfxParser.parse(arquivo.file)

    # === INTERAGIR COM O ARQUIVO PARA LEITURA DOS DADOS ===
    id_conta = ofx.signon.fi_fid
    conta = ofx.account
    
    # === CASO SEJA NUBANK ===
    if id_conta == "260":
        nome_forma_pagamento = "CARTÃO DE CRÉDITO - NUBANK"
        forma_pagamento_nubank = (
            session.query(FormasPagamento)
            .filter(
                FormasPagamento.forma_pagamento == nome_forma_pagamento,
                FormasPagamento.responsavel == usuario.usuario,
                FormasPagamento.id_usuario == usuario.id
            ).first())
        # === SE NÃO HOUVER FORMA DE PAGAMENTO NUBANK E AINDA NÃO FOI CONFIRMADO GERAR FORMA DE PAGAMENTO NUBANK ===
        if not forma_pagamento_nubank and not confirmar_nubank:
            return {
                "precisa_criar_forma_pagamento": True,
                "forma_pagamento": nome_forma_pagamento
            }
        
        # === SE NÃO HOUVER FORMA DE PAGAMENTO NUBANK MAS FOI CONFIRMADO GERAR FORMA DE PAGAMENTO NUBANK ===
        if not forma_pagamento_nubank and confirmar_nubank:
            if data_vencimento is None:
                raise HTTPException(
                    status_code=400,
                    detail="Data de vencimento não informada."
                )

            if data_fechamento is None:
                raise HTTPException(
                    status_code = 400,
                    detail = "Data de fechamento não informada."
                )

            if not 1 <= data_vencimento <= 31:
                raise HTTPException(
                    status_code = 400,
                    detail = "Data de vencimento deve estar entre 01 e 31.  "
                )
            
            if not 1 <= data_fechamento <= 31:
                raise HTTPException(
                    status_code = 400,
                    detail = "Data de fechamento deve estar entre 01 e 31."
                )

            # === CRIAR FORMA DE PAGAMENTO NUBANK - CARTÃO DE CRÉDITO - NUBANK ===
            forma_pagamento_nubank = FormasPagamento(id_usuario = usuario.id, 
                                                  forma_pagamento = nome_forma_pagamento, 
                                                  responsavel = usuario.nome, 
                                                  status_forma_pagamento = "ATIVO", 
                                                  data_vencimento = data_vencimento, 
                                                  data_fechamento = data_fechamento)
            session.add(forma_pagamento_nubank)
            session.flush()

        # === INTERAGIR COM CADA TRANSAÇÃO DO ARQUIVO .OFX ===
        transacoes = []
        for t in conta.statement.transactions:
            transacoes.append({
                "data_compra": t.date,
                "tipo": t.type,
                "valor_lancamento": t.amount,
                "item_comprado": t.memo,
                "id_transacao": t.id,
            })

        # === SEPARAR DO ARQUIVO - ITENS PARCELADOS / ALTERAR FORMATO DATA DA COMPRA / REMOVER CRÉDITOS / TORNAR DÉBITOS COMO POSITIVOS
        df = pd.DataFrame(transacoes)
        df = df[~df["item_comprado"].str.contains("Parcela", case=False, na=False)]
        df["data_compra"] = pd.to_datetime(df["data_compra"]).dt.date
        df_filtrado = df["tipo"] == "debit"
        df["valor_lancamento"] = df["valor_lancamento"].abs()
        novo_df = df[df_filtrado]

        # === PARA CADA LINHA LIDA DO ARQUIVO .OFX ===
        for _, linha in novo_df.iterrows():
            item_comprado = linha["item_comprado"].upper()

            # === VERIFICAR SE EXISTE LANÇAMENTO COM AQUELE CODIGO ===
            existeLancamento = session.query(Lancamentos).filter(Lancamentos.id_transacao_bancaria == linha["id_transacao"]).first()
            # === SE SIM IGNORAR ===
            if existeLancamento:
                continue
            
            # === VERIFICAR CATEGORIA CORRESPONDENTE ===
            id_categoria = encontrar_categoria(item_comprado,
                                               usuario_id = usuario.id,
                                               session = session
                                               )
            # === CRIAR NOVO LANCAMENTO ===
            novolancamento = Lancamentos(id_usuario = usuario.id, 
                                         id_transacao_bancaria = linha["id_transacao"],
                                        data_compra = linha["data_compra"], 
                                        item_comprado = item_comprado, 
                                        id_categoria = id_categoria, 
                                        id_forma_pagamento = forma_pagamento_nubank.id, 
                                        valor_lancamento = linha["valor_lancamento"], 
                                        parcelado = False, 
                                        qnt_parcelas = 1, 
                                        pagador_responsavel = usuario.nome, 
                                        tipo_lancamento = "DEBITO"
                                        )
            session.add(novolancamento)
            session.flush()

            # === GERAR NOVA PARCELA ===
            qtd = novolancamento.qnt_parcelas
            valor_total = Decimal(str(novolancamento.valor_lancamento))
            qtd = novolancamento.qnt_parcelas
            valor_base = (valor_total / qtd).quantize(Decimal("0.01"))
            primeiro_vencimento = calcular_primeiro_vencimento(linha["data_compra"],
                                                               novolancamento.formaPagamento)
            for numero in range(1, qtd + 1):
                if numero < qtd:
                    valor = valor_base
                else:
                    valor = valor_total - (valor_base * (qtd - 1))
                    vencimento = primeiro_vencimento + relativedelta(months = numero - 1)
            parcela = Parcelas(numero_parcela = 1,
                           valor_parcela = valor,
                           id_lancamento = novolancamento.id,
                           data_vencimento = vencimento,
                           )
            session.add(parcela)
        session.commit()
        return {
            "sucesso": True,
            "mensagem": "Arquivo OFX importado com sucesso."
        }
        

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
    

    lancamento = session.query(Lancamentos).filter(
        Lancamentos.id == id_lancamento, 
        Lancamentos.id_usuario == usuario.id).first()

    if not lancamento:
        return {
            "sucesso": False,
            "mensagem": "Lançamento não encontrado em sistema ou CANCELADO."
        }

    
    if isinstance(valor_lancamento, str):
        valor_lancamento_normalizado = Decimal(valor_lancamento.replace("R$", "").replace(".","").replace(",",".").strip())
    else:
        valor_lancamento_normalizado = Decimal(str(valor_lancamento)) if valor_lancamento is not None else None
    valor_parcelado = bool(parcelado) if parcelado is not None else False
    lancamento_existente = session.query(Lancamentos).filter(
        Lancamentos.id != lancamento.id,
        Lancamentos.item_comprado == item_comprado.upper(),
        Lancamentos.data_compra == data_compra,
        Lancamentos.id_categoria == id_categoria,
        Lancamentos.id_forma_pagamento == id_forma_pagamento,
        Lancamentos.valor_lancamento == valor_lancamento_normalizado,
        Lancamentos.parcelado == valor_parcelado,
        Lancamentos.qnt_parcelas == qnt_parcelas,
        Lancamentos.pagador_responsavel == pagador_responsavel.upper(),
    ).first()


    if lancamento_existente:
        return {
            "sucesso": False,
            "mensagem": "Já existe um lancamento idêntico a este em sistema."
        }

    if data_compra:
        lancamento.data_compra = data_compra
        primeiro_vencimento = calcular_primeiro_vencimento(lancamento.data_compra, lancamento.formaPagamento)

        for indice, parcela in enumerate(lancamento.parcela):
            parcela.data_vencimento = (
                primeiro_vencimento + relativedelta(months=indice)
            )
    
    if item_comprado is not None:
        lancamento.item_comprado = item_comprado

    if id_categoria is not None:
        lancamento.id_categoria = id_categoria

    if id_forma_pagamento is not None:
        lancamento.id_forma_pagamento = id_forma_pagamento
        session.flush()
        primeiro_vencimento = calcular_primeiro_vencimento(lancamento.data_compra, lancamento.formaPagamento)
        for indice, parcela in enumerate(lancamento.parcela):
            parcela.data_vencimento = (
                primeiro_vencimento + relativedelta(months=indice)
            )

    if pagador_responsavel is not None:
        lancamento.pagador_responsavel = pagador_responsavel.upper()

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
        else:
            if lancamento.parcela:
                lancamento.parcela[0].valor_parcela = novo_valor


    if qnt_parcelas is not None and qnt_parcelas != lancamento.qnt_parcelas:
        if qnt_parcelas <= 0:
            raise HTTPException(
                status_code=400,
                detail="Quantidade de parcelas precisa ser maior do que 0"
            )

        valor_total = Decimal(str(lancamento.valor_lancamento))
        lancamento.qnt_parcelas = qnt_parcelas

        lancamento.parcela.clear()

        valor_base = (valor_total / qnt_parcelas).quantize(Decimal("0.01"))
        primeiro_vencimento = calcular_primeiro_vencimento(lancamento.data_compra, lancamento.formaPagamento)

        for numero in range(1, qnt_parcelas + 1):
            if numero < qnt_parcelas:
                valor = valor_base
            else:
                valor = valor_total - (valor_base * (qnt_parcelas - 1))

            vencimento = (
                primeiro_vencimento + relativedelta(months = numero - 1)
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
            primeiro_vencimento = calcular_primeiro_vencimento(lancamento.data_compra, lancamento.formaPagamento)
            lancamento.qnt_parcelas = 1
            lancamento.parcela.clear()
            parcela = Parcelas(numero_parcela = 1,
                               valor_parcela = lancamento.valor_lancamento,
                               id_lancamento = lancamento.id,
                               data_vencimento = primeiro_vencimento)
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

    return {
        "sucesso": True,
        "mensagem": f"Lançamento excluído com sucesso! - ID da conta {conta.id}",
        "conta": conta
    }

