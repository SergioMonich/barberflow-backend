from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import auth, clientes, servicos
from app.db.init_db import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="BarberFlow API", lifespan=lifespan)

# Libera chamadas vindas do app Flutter web (em desenvolvimento).
# Em producao, trocar "*" pelos dominios reais.
app.add_middleware(

    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    
)

app.include_router(auth.router, prefix="/auth", tags=["Autenticacao"])
app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
app.include_router(servicos.router, prefix="/servicos", tags=["Servicos"])


@app.get("/health")
def health_check():
    return {"status": "ok"}