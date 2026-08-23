from app.database import models
from app.database.database import get_db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/protocolo", tags=["Protocolo"])


class QuestaoCreate(BaseModel):
    projeto_id: int
    codigo: str  # Ex: RQ1
    pergunta: str


class CriterioCreate(BaseModel):
    projeto_id: int
    tipo: models.TipoCriterio  # INCLUSAO ou EXCLUSAO
    codigo: str  # Ex: CI01, CE01
    descricao: str


@router.post("/questao")
def adicionar_questao(dados: QuestaoCreate, db: Session = Depends(get_db)):
    q = models.QuestaoPesquisa(**dados.model_dump())
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


@router.post("/criterio")
def adicionar_criterio(dados: CriterioCreate, db: Session = Depends(get_db)):
    c = models.Criterio(**dados.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c