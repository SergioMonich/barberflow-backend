from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ServicoCreate(BaseModel):

    nome: str
    descricao: Optional[str] = None
    preco: float = Field(gt=0)
    duracao_minutos: int = Field(default=30, gt=0)


class ServicoRead(BaseModel):

    id: int
    barbearia_id: int
    nome: str
    descricao: Optional[str] = None
    preco: float
    duracao_minutos: int
    ativo: bool


class ServicoUpdate(BaseModel):

    nome: Optional[str] = None
    descricao: Optional[str] = None
    preco: Optional[float] = Field(default=None, gt=0)
    duracao_minutos: Optional[int] = Field(default=None, gt=0) #(gt=0) faz o FastAPI recusar preço zero ou negativo com erro 422, sem código extra.

    model_config = ConfigDict(json_schema_extra={"examples": [{"preco": 45.0}]})