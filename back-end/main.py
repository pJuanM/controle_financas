# PARAR COLOCAR A API NO AR, PRECISAMOS EXECUTAR -> UVIVORN MAIN:APP --RELOAD
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS"))

app = FastAPI()

templates = Jinja2Templates(directory = "../front-end/templates")
app.mount("/static", StaticFiles(directory="../front-end"), name="static")

from routes.rotas_categorias import rota_categoria
from routes.rotas_formaPagamento import rota_formaPagamento
from routes.rotas_autenticacao import rota_autenticacao
from routes.rotas_contas import rota_conta

app.include_router(rota_categoria)
app.include_router(rota_formaPagamento)
app.include_router(rota_autenticacao)
app.include_router(rota_conta)
