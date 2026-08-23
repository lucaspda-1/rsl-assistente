import csv
import io
import bibtexparser
from sqlalchemy.orm import Session
from app.database import models


def importar_artigos_csv(db: Session, projeto_id: int, conteudo_bytes: bytes, fonte: str = "CSV Import"):
    """Lê um arquivo CSV com metadados de artigos e insere no banco de dados."""
    texto = conteudo_bytes.decode("utf-8", errors="ignore")
    leitor = csv.DictReader(io.StringIO(texto))
    
    artigos_criados = 0
    for linha in leitor:
        # Tenta mapear nomes comuns de colunas de exportadores acadêmicos
        titulo = linha.get("Title") or linha.get("title") or linha.get("Document Title") or "Sem título"
        autores = linha.get("Authors") or linha.get("authors") or linha.get("Author") or ""
        
        ano_str = linha.get("Year") or linha.get("year") or linha.get("Publication Year") or ""
        try:
            ano = int(ano_str) if ano_str else None
        except ValueError:
            ano = None
            
        resumo = linha.get("Abstract") or linha.get("abstract") or ""
        doi = linha.get("DOI") or linha.get("doi") or ""
        url = linha.get("URL") or linha.get("url") or ""
        
        novo_artigo = models.Artigo(
            projeto_id=projeto_id,
            titulo=titulo,
            autores=autores,
            ano=ano,
            resumo=resumo,
            doi=doi,
            url=url,
            fonte=fonte,
            status=models.StatusArtigo.IMPORTADO
        )
        db.add(novo_artigo)
        artigos_criados += 1
        
    db.commit()
    return artigos_criados




def importar_artigos_bibtex(
    db: Session,
    projeto_id: int,
    conteudo_bibtex: str,
    fonte: str = "Parsifal BibTeX",
):
    """Importa arquivos .bib exportados do Parsifal ou de bases acadêmicas."""
    bib_database = bibtexparser.loads(conteudo_bibtex)
    artigos_criados = 0

    def converter_ano(valor):
        try:
            return int(str(valor).strip()[:4])
        except (TypeError, ValueError):
            return None

    for entry in bib_database.entries:
        novo_artigo = models.Artigo(
            projeto_id=projeto_id,
            titulo=entry.get("title", "Sem título").strip("{}"),
            autores=entry.get("author", "").strip("{}"),
            ano=converter_ano(entry.get("year")),
            resumo=entry.get("abstract", "").strip("{}"),
            doi=entry.get("doi", "").strip("{}"),
            url=entry.get("url", "").strip("{}"),
            fonte=fonte,
            status=models.StatusArtigo.IMPORTADO,
        )
        db.add(novo_artigo)
        artigos_criados += 1

    db.commit()
    return artigos_criados