from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

TipoFinanceiro = Literal["receita", "despesa"]


class CategoriaCreate(BaseModel):

    nome: str = Field(min_length=1)
    tipo: TipoFinanceiro

    model_config = ConfigDict(

        json_schema_extra={"examples": [{"nome": "Aluguel", "tipo": "despesa"}]}

    )


class CategoriaRead(BaseModel):

    id: int
    barbearia_id: int
    nome: str
    tipo: str


class MovimentacaoCreate(BaseModel):

    tipo: TipoFinanceiro
    categoria_id: int
    descricao: Optional[str] = None
    valor: float = Field(gt=0)
    data: date

    model_config = ConfigDict(

        json_schema_extra={

            "examples": [

                {

                    "tipo": "despesa",
                    "categoria_id": 1,
                    "descricao": "Aluguel de outubro",
                    "valor": 800.0,
                    "data": "2026-10-05",

                }

            ]

        }

    )


class MovimentacaoRead(BaseModel):

    id: int
    barbearia_id: int
    tipo: str
    categoria_id: int
    descricao: Optional[str] = None
    valor: float
    data: date
    agendamento_id: Optional[int] = None


class ResumoFinanceiro(BaseModel):
    
    inicio: Optional[date] = None
    fim: Optional[date] = None
    receitas: float
    despesas: float
    saldo: float
    quantidade: int