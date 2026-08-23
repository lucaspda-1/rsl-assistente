import re
import unicodedata


def normalizar_texto(texto: str) -> str:
    if not texto:
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    texto = texto.lower()
    return re.sub(r"[^\w\s]", "", texto).strip()


def normalizar_doi(doi: str) -> str:
    valor = doi.strip().lower()
    valor = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", valor)
    return re.sub(r"^doi:\s*", "", valor).rstrip(".")


def encontrar_duplicados(artigos: list) -> list:
    """Recebe uma lista de objetos Artigo do banco e retorna

    os IDs dos artigos que são duplicados de algum já existente.
    """
    duplicados_ids = []
    vistos_doi = set()
    vistos_titulos = set()

    for artigo in artigos:
        eh_duplicado = False

        # Check por DOI
        if artigo.doi:
            doi_limpo = normalizar_doi(artigo.doi)
            if doi_limpo in vistos_doi:
                eh_duplicado = True
            else:
                vistos_doi.add(doi_limpo)

        # Check por Título normalizado
        titulo_limpo = normalizar_texto(artigo.titulo)
        if titulo_limpo:
            if titulo_limpo in vistos_titulos:
                eh_duplicado = True
            else:
                vistos_titulos.add(titulo_limpo)

        if eh_duplicado:
            duplicados_ids.append(artigo.id)

    return duplicados_ids