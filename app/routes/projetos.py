from app.database import models
from app.database.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/projetos", tags=["Projetos"])


class ProjetoCreate(BaseModel):
    nome: str
    descricao: str | None = None


@router.post("/")
def criar_projeto(dados: ProjetoCreate, db: Session = Depends(get_db)):
    novo_projeto = models.Projeto(nome=dados.nome, descricao=dados.descricao)
    db.add(novo_projeto)
    db.commit()
    db.refresh(novo_projeto)
    return novo_projeto


@router.get("/")
def listar_projetos(db: Session = Depends(get_db)):
    return db.query(models.Projeto).all()


@router.get("/{projeto_id}")
def obter_projeto(projeto_id: int, db: Session = Depends(get_db)):
    proj = (
        db.query(models.Projeto)
        .filter(models.Projeto.id == projeto_id)
        .first()
    )
    if not proj:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return proj