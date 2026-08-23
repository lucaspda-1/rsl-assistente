from app.database import models
from app.database.database import get_db
from app.services.ollama_service import (
    analisar_artigo_com_ollama,
    extrair_texto_pdf,
)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/ia", tags=["Inteligência Artificial"])


@router.post("/triagem/{artigo_id}")
def executar_triagem_ia(artigo_id: int, db: Session = Depends(get_db)):
    artigo = (
        db.query(models.Artigo)
        .filter(models.Artigo.id == artigo_id)
        .first()
    )
    if not artigo:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")

    # Busca os critérios cadastrados no mesmo projeto
    criterios = (
        db.query(models.Criterio)
        .filter(models.Criterio.projeto_id == artigo.projeto_id)
        .all()
    )
    c_inc = [
        c.descricao
        for c in criterios
        if c.tipo == models.TipoCriterio.INCLUSAO
    ]
    c_exc = [
        c.descricao
        for c in criterios
        if c.tipo == models.TipoCriterio.EXCLUSAO
    ]

    texto = artigo.resumo
    if artigo.arquivo_pdf:
        texto = extrair_texto_pdf(artigo.arquivo_pdf)

    analise = analisar_artigo_com_ollama(texto, c_inc, c_exc)

    # Salva o parecer da IA na tabela de Triagem para validação do pesquisador
    triagem_ia = models.Triagem(
        artigo_id=artigo.id,
        decisao=models.DecisaoTriagem.DUVIDA,
        avaliacao_ia=f"[{analise.get('recomendacao')}] {analise.get('justificativa')}",
        confianca_ia=analise.get("confianca", 0),
        revisor="Ollama (IA)",
    )
    db.add(triagem_ia)
    db.commit()

    return {"artigo_id": artigo_id, "resultado_ia": analise}