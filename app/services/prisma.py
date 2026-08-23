from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import models


def calcular_fluxo_prisma(db: Session, projeto_id: int) -> dict:
    """Calcula dinamicamente todas as métricas do fluxo PRISMA 2020

    a partir dos artigos cadastrados no projeto.
    """
    # 1. Total de registros identificados nas bases
    total_encontrados = (
        db.query(models.Artigo)
        .filter(models.Artigo.projeto_id == projeto_id)
        .count()
    )

    # 2. Registros removidos antes da triagem (Duplicados)
    duplicados = (
        db.query(models.Artigo)
        .filter(
            models.Artigo.projeto_id == projeto_id,
            models.Artigo.status == models.StatusArtigo.DUPLICADO,
        )
        .count()
    )

    # 3. Registros que realmente passaram pela triagem de título e resumo
    triados_titulo_resumo = (
        db.query(models.Artigo)
        .filter(
            models.Artigo.projeto_id == projeto_id,
            models.Artigo.status.in_(
                [
                    models.StatusArtigo.EXCLUIDO_TRIAGEM,
                    models.StatusArtigo.LEITURA_COMPLETA,
                    models.StatusArtigo.EXCLUIDO_TEXTO_COMPLETO,
                    models.StatusArtigo.INCLUIDO,
                ]
            ),
        )
        .count()
    )

    # 4. Registros excluídos na triagem (Título/Resumo)
    excluidos_triagem = (
        db.query(models.Artigo)
        .filter(
            models.Artigo.projeto_id == projeto_id,
            models.Artigo.status == models.StatusArtigo.EXCLUIDO_TRIAGEM,
        )
        .count()
    )

    # 5. Artigos buscados para leitura do texto completo
    texto_completo_avaliado = (
        db.query(models.Artigo)
        .filter(
            models.Artigo.projeto_id == projeto_id,
            models.Artigo.status.in_(
                [
                    models.StatusArtigo.LEITURA_COMPLETA,
                    models.StatusArtigo.EXCLUIDO_TEXTO_COMPLETO,
                    models.StatusArtigo.INCLUIDO,
                ]
            ),
        )
        .count()
    )

    # 6. Artigos incluídos no estudo final
    incluidos = (
        db.query(models.Artigo)
        .filter(
            models.Artigo.projeto_id == projeto_id,
            models.Artigo.status == models.StatusArtigo.INCLUIDO,
        )
        .count()
    )

    # 7. Artigos excluídos na leitura completa
    excluidos_completo = (
        db.query(models.Artigo)
        .filter(
            models.Artigo.projeto_id == projeto_id,
            models.Artigo.status == models.StatusArtigo.EXCLUIDO_TEXTO_COMPLETO,
        )
        .count()
    )

    # 8. Detalhamento dos motivos de exclusão (para a caixa de justificativas do PRISMA)
    motivos_exclusao_query = (
        db.query(
            models.Triagem.motivo_exclusao,
            func.count(models.Triagem.id),
        )
        .join(models.Artigo)
        .filter(
            models.Artigo.projeto_id == projeto_id,
            models.Triagem.decisao == models.DecisaoTriagem.EXCLUIR,
        )
        .group_by(models.Triagem.motivo_exclusao)
        .all()
    )

    motivos_exclusao = {
        motivo or "Sem motivo especificado": qtd
        for motivo, qtd in motivos_exclusao_query
    }

    return {
        "total_encontrados": total_encontrados,
        "duplicados": duplicados,
        "apos_duplicados": total_encontrados - duplicados,
        "triados_titulo_resumo": triados_titulo_resumo,
        "excluidos_triagem": excluidos_triagem,
        "texto_completo_avaliado": texto_completo_avaliado,
        "excluidos_texto_completo": excluidos_completo,
        "motivos_exclusao": motivos_exclusao,
        "estudos_incluidos": incluidos,
    }