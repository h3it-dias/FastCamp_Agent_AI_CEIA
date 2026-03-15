from pydantic import BaseModel

class EstudosRequest(BaseModel):
    assunto: str
    dias: int
    horas_dia: float