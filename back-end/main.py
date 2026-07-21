# PARAR COLOCAR A API NO AR, PRECISAMOS EXECUTAR -> UVIVORN MAIN:APP --RELOAD
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS"))

app = FastAPI()

oauth2_schema = OAuth2PasswordBearer(tokenUrl="usuario/login")

templates = Jinja2Templates(directory = "../front-end/templates")
app.mount("/static", StaticFiles(directory="../front-end/static"), name="static")

from routes.rotas_categorias import rota_categorias
from routes.rotas_formaPagamento import rota_formasPagamento
from routes.rotas_autenticacao import rota_autenticacao
from routes.rotas_lancamentos import rota_lancamentos
from routes.rotas_parcelas import rota_parcelas
from routes.rota_home import rota_home

app.include_router(rota_categorias)
app.include_router(rota_formasPagamento)
app.include_router(rota_autenticacao)
app.include_router(rota_lancamentos)
app.include_router(rota_parcelas)
app.include_router(rota_home)

