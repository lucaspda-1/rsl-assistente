from app.database import models
from app.database.database import get_db
from app.services.deduplicacao import encontrar_duplicados
from app.services.artigos import importar_artigos_bibtex, importar_artigos_csv
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/artigos", tags=["Artigos"])


class TriagemCreate(BaseModel):
    artigo_id: int
    decisao: models.DecisaoTriagem
    etapa: models.EtapaTriagem = models.EtapaTriagem.TITULO_RESUMO
    motivo_exclusao: str | None = None
    revisor: str = "Humano"


class ArtigoCreate(BaseModel):
    projeto_id: int
    titulo: str
    autores: str | None = None
    ano: int | None = None
    resumo: str | None = None
    palavras_chave: str | None = None
    doi: str | None = None
    url: str | None = None
    fonte: str | None = "Cadastro manual"


@router.get("/projeto/{projeto_id}")
def listar_artigos_projeto(
    projeto_id: int, status: str | None = None, db: Session = Depends(get_db)
):
    query = db.query(models.Artigo).filter(
        models.Artigo.projeto_id == projeto_id
    )
    if status:
        query = query.filter(models.Artigo.status == status)
    return query.all()


@router.post("/")
def criar_artigo(dados: ArtigoCreate, db: Session = Depends(get_db)):
    projeto = db.query(models.Projeto).filter(models.Projeto.id == dados.projeto_id).first()
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    artigo = models.Artigo(**dados.model_dump())
    db.add(artigo)
    db.commit()
    db.refresh(artigo)
    return artigo


@router.post("/triagem")
def registrar_triagem(dados: TriagemCreate, db: Session = Depends(get_db)):
    artigo = (
        db.query(models.Artigo)
        .filter(models.Artigo.id == dados.artigo_id)
        .first()
    )
    if not artigo:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")

    nova_triagem = models.Triagem(**dados.model_dump())

    if dados.etapa == models.EtapaTriagem.TITULO_RESUMO:
        if dados.decisao == models.DecisaoTriagem.INCLUIR:
            artigo.status = models.StatusArtigo.LEITURA_COMPLETA
        elif dados.decisao == models.DecisaoTriagem.EXCLUIR:
            artigo.status = models.StatusArtigo.EXCLUIDO_TRIAGEM
    elif dados.etapa == models.EtapaTriagem.TEXTO_COMPLETO:
        if dados.decisao == models.DecisaoTriagem.INCLUIR:
            artigo.status = models.StatusArtigo.INCLUIDO
        elif dados.decisao == models.DecisaoTriagem.EXCLUIR:
            artigo.status = models.StatusArtigo.EXCLUIDO_TEXTO_COMPLETO

    db.add(nova_triagem)
    db.commit()
    return {"message": "Triagem registrada com sucesso", "status_artigo": artigo.status}


@router.post("/deduplicar/{projeto_id}")
def executar_deduplicacao(projeto_id: int, db: Session = Depends(get_db)):
    artigos = (
        db.query(models.Artigo)
        .filter(models.Artigo.projeto_id == projeto_id)
        .all()
    )
    duplicados_ids = encontrar_duplicados(artigos)

    # Marca os artigos como DUPLICADO no banco
    if duplicados_ids:
        db.query(models.Artigo).filter(
            models.Artigo.id.in_(duplicados_ids)
        ).update(
            {models.Artigo.status: models.StatusArtigo.DUPLICADO},
            synchronize_session=False,
        )
        db.commit()

    return {
        "total_analisados": len(artigos),
        "duplicados_encontrados": len(duplicados_ids),
    }


@router.post("/importar/{projeto_id}")
async def importar_artigos(
    projeto_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    conteudo = await arquivo.read()
    nome = (arquivo.filename or "").lower()
    if nome.endswith(".csv"):
        total = importar_artigos_csv(db, projeto_id, conteudo, arquivo.filename or "CSV")
    elif nome.endswith((".bib", ".bibtex")):
        total = importar_artigos_bibtex(db, projeto_id, conteudo.decode("utf-8", errors="ignore"), arquivo.filename or "BibTeX")
    else:
        raise HTTPException(status_code=400, detail="Envie um arquivo CSV ou BibTeX")
    return {"message": "Artigos importados com sucesso", "total_importado": total}