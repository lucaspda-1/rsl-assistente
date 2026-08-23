from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home_endpoint():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/dashboard"

def test_listar_projetos():
    response = client.get("/projetos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_rotas_de_interface():
    assert client.get("/dashboard").status_code in (200, 307)
    assert client.get("/protocolo").status_code in (200, 307)
    assert client.get("/artigos").status_code in (200, 307)


def test_normalizacao_de_doi():
    from app.services.deduplicacao import normalizar_doi

    assert normalizar_doi("https://doi.org/10.1000/ABC123") == "10.1000/abc123"