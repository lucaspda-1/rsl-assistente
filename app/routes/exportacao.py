import os
from app.database.database import get_db
from app.services.exportacao import exportar_projeto_excel
from app.services.prisma import calcular_fluxo_prisma
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/exportacao", tags=["Exportação & PRISMA"])


@router.get("/prisma/{projeto_id}")
def obter_prisma(projeto_id: int, db: Session = Depends(get_db)):
    """Retorna os dados numéricos do fluxo PRISMA 2020 em formato JSON."""
    return calcular_fluxo_prisma(db, projeto_id)


@router.get("/excel/{projeto_id}")
def baixar_excel(projeto_id: int, db: Session = Depends(get_db)):
    """Gera e faz o download do arquivo .xlsx do projeto."""
    caminho_dir = "data/exports"
    os.makedirs(caminho_dir, exist_ok=True)
    caminho_arquivo = os.path.join(
        caminho_dir, f"RSL_Projeto_{projeto_id}.xlsx"
    )

    try:
        exportar_projeto_excel(db, projeto_id, caminho_arquivo)
        return FileResponse(
            path=caminho_arquivo,
            filename=f"RSL_Projeto_{projeto_id}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao gerar Excel: {str(e)}"
        )