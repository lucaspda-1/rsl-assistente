import json
import os
import requests
from pypdf import PdfReader


def extrair_texto_pdf(caminho_pdf: str) -> str:
    """Extrai o texto de um arquivo PDF enviado."""
    reader = PdfReader(caminho_pdf)
    texto = ""
    for page in reader.pages:
        conteudo = page.extract_text()
        if conteudo:
            texto += conteudo + "\n"
    return texto[:8000]  # Limita tamanho para otimizar janela de contexto


def analisar_artigo_com_ollama(
    texto_artigo: str,
    criterios_inclusao: list,
    criterios_exclusao: list,
    modelo: str | None = None,
) -> dict:
    """Envia o texto do artigo e os critérios para o Ollama avaliar a triagem."""
    url = f"{os.getenv('OLLAMA_URL', 'http://localhost:11434').rstrip('/')}/api/generate"
    modelo = modelo or os.getenv("OLLAMA_MODEL", "llama3")

    prompt = f"""
    Você é um especialista em Revisão Sistemática da Literatura (RSL).
    Analise o texto do artigo abaixo com base nos critérios de inclusão e exclusão informados.

    CRITÉRIOS DE INCLUSÃO:
    {json.dumps(criterios_inclusao, ensure_ascii=False)}

    CRITÉRIOS DE EXCLUSÃO:
    {json.dumps(criterios_exclusao, ensure_ascii=False)}

    TEXTO DO ARTIGO:
    {texto_artigo}

    Responda EXATAMENTE no seguinte formato JSON:
    {{
        "recomendacao": "INCLUIR" ou "EXCLUIR",
        "confianca": 85,
        "justificativa": "Sua explicação detalhada aqui com base nos critérios."
    }}
    """

    payload = {"model": modelo, "prompt": prompt, "stream": False, "format": "json"}

    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            resultado_str = response.json().get("response", "{}")
            return json.loads(resultado_str)
    except Exception as e:
        return {
            "recomendacao": "DUVIDA",
            "confianca": 0,
            "justificativa": f"Erro na conexão com Ollama: {str(e)}",
        }
    return {
        "recomendacao": "DUVIDA",
        "confianca": 0,
        "justificativa": "O Ollama não conseguiu processar o artigo.",
    }


def extrair_resposta_rq(
    texto_artigo: str, pergunta_rq: str, modelo: str | None = None
) -> dict:
    """Responde a uma Questão de Pesquisa (RQ) específica extraindo trechos do artigo."""
    url = f"{os.getenv('OLLAMA_URL', 'http://localhost:11434').rstrip('/')}/api/generate"
    modelo = modelo or os.getenv("OLLAMA_MODEL", "llama3")

    prompt = f"""
    Com base no texto do artigo científico abaixo, responda à Questão de Pesquisa (RQ) e extraia a evidência textual direta.

    QUESTÃO DE PESQUISA:
    {pergunta_rq}

    TEXTO DO ARTIGO:
    {texto_artigo}

    Responda EXATAMENTE no seguinte formato JSON:
    {{
        "resposta": "Sua resposta direta aqui",
        "evidencia": "Trecho/Citação exata extraída do texto do artigo"
    }}
    """

    payload = {"model": modelo, "prompt": prompt, "stream": False, "format": "json"}

    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            return json.loads(response.json().get("response", "{}"))
    except Exception as e:
        return {"resposta": "Erro ao processar", "evidencia": str(e)}
    return {"resposta": "Não foi possível processar a questão.", "evidencia": ""}