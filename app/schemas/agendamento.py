from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict

StatusAgendamento = Literal[

    "agendado", "confirmado", "concluido", "cancelado", "nao_compareceu"

]


class AgendamentoCreate(BaseModel):

    cliente_id: int
    servico_id: int
    data_hora: datetime
    observacoes: Optional[str] = None

    model_config = ConfigDict(

        json_schema_extra={

            "examples": [

                {

                    "cliente_id": 1,
                    "servico_id": 1,
                    "data_hora": "2026-10-20T15:00:00Z",
                    "observacoes": "Primeira visita",

                }

            ]

        }

    )


class AgendamentoRead(BaseModel):

    id: int
    barbearia_id: int
    barbeiro_id: int
    cliente_id: int
    servico_id: int
    data_hora: datetime
    status: str
    valor: float
    observacoes: Optional[str] = None


class AgendamentoUpdate(BaseModel):

    data_hora: Optional[datetime] = None
    observacoes: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"data_hora": "2026-10-21T16:00:00Z"}]}
    )


class StatusUpdate(BaseModel):
    
    status: StatusAgendamento

    model_config = ConfigDict(json_schema_extra={"examples": [{"status": "confirmado"}]})