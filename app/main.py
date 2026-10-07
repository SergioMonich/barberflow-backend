from contextlib import asynccontextmanager 
from fastapi import FastAPI 
from app.db.init_db import create_db_and_tables 
from app.api.routers import auth 

@asynccontextmanager 
async def lifespan(app: FastAPI):

    create_db_and_tables() 
    yield 
    
app = FastAPI(title="BarberFlow API", lifespan=lifespan) 

#include_router pluga as rotas do auth.py no app principal.prefix="/auth" faz com que /registro vire /auth/registro automaticamente (por isso as rotas no auth.py não precisam repetir 'auth' no caminho)
app.include_router(auth.router, prefix="/auth", tags=["Autenticacao"]) 

@app.get("/health") 
def health_check(): 

    return {"status": "ok"}