from sqlmodel import SQLModel 
from app.db.session import engine 
import app.models # noqa: F401 (avisa ferramentas de lint que esse import 'não usado' é proposital.)

def create_db_and_tables(): SQLModel.metadata.create_all(engine)