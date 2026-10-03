from typing import Optional 
from sqlmodel import SQLModel, Field 

#modelando a tabela barbeiro
class Barbeiro(SQLModel, table=True): 
    id: Optional[int] = Field(default=None, primary_key=True) #Optional[int] com default=None no id é porque o banco gera esse valor sozinho (auto-incremento) — nunca vai preencher o id manualmente
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id") #usuario_id é Optional porque no MVP o próprio dono pode ser o barbeiro sem ter um registro de login separado (isso só vai importar quando tivermos múltiplos barbeiros)
    barbearia_id: int = Field(foreign_key="barbearia.id") 
    especialidade: Optional[str] = None 
    ativo: bool = Field(default=True)