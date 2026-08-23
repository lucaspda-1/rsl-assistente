from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.database import models
from app.database.database import engine, get_db
from app.routes import artigos, exportacao, ia, projetos, protocolo
from app.services.prisma import calcular_fluxo_prisma

models.Base.metadata.create_all(bind=engine)
if "etapa" not in {column["name"] for column in inspect(engine).get_columns("triagens")}:
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE triagens ADD COLUMN etapa VARCHAR(20) DEFAULT 'TITULO_RESUMO' NOT NULL"))

app = FastAPI(title="Assistente RSL", version="0.1.0")

# Configuração do Jinja2
templates = Jinja2Templates(directory="app/templates")

# Registro das Rotas REST
app.include_router(projetos.router)
app.include_router(protocolo.router)
app.include_router(artigos.router)
app.include_router(exportacao.router)
app.include_router(ia.router)

# Rotas de Web / Interface HTML
@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse(url="/dashboard", status_code=307)


def obter_projeto(db: Session, projeto_id: int):
    projeto = db.query(models.Projeto).filter(models.Projeto.id == projeto_id).first()
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return projeto


@app.get("/dashboard")
def dashboard_padrao(request: Request, db: Session = Depends(get_db)):
    projeto = db.query(models.Projeto).order_by(models.Projeto.id).first()
    if projeto:
        return RedirectResponse(url=f"/dashboard/{projeto.id}", status_code=307)
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"prisma": calcular_fluxo_prisma(db, 0), "projeto": None})


@app.get("/dashboard/{projeto_id}")
def view_dashboard(projeto_id: int, request: Request, db: Session = Depends(get_db)):
    projeto = obter_projeto(db, projeto_id)
    prisma_data = calcular_fluxo_prisma(db, projeto.id)
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"prisma": prisma_data, "projeto": projeto})


@app.get("/protocolo")
def protocolo_padrao(request: Request, db: Session = Depends(get_db)):
    projeto = db.query(models.Projeto).order_by(models.Projeto.id).first()
    if projeto:
        return RedirectResponse(url=f"/protocolo/{projeto.id}", status_code=307)
    raise HTTPException(status_code=404, detail="Nenhum projeto cadastrado")


@app.get("/protocolo/{projeto_id}")
def view_protocolo(projeto_id: int, request: Request, db: Session = Depends(get_db)):
    projeto = obter_projeto(db, projeto_id)
    return templates.TemplateResponse(request=request, name="protocolo.html", context={"protocolo": projeto.protocolo, "projeto": projeto})


@app.get("/artigos")
def artigos_padrao(request: Request, db: Session = Depends(get_db)):
    projeto = db.query(models.Projeto).order_by(models.Projeto.id).first()
    if projeto:
        return RedirectResponse(url=f"/artigos/{projeto.id}", status_code=307)
    return templates.TemplateResponse(request=request, name="artigos.html", context={"artigos": [], "projeto": None})


@app.get("/artigos/{projeto_id}")
def view_artigos(projeto_id: int, request: Request, db: Session = Depends(get_db)):
    projeto = obter_projeto(db, projeto_id)
    return templates.TemplateResponse(request=request, name="artigos.html", context={"artigos": projeto.artigos, "projeto": projeto})

@app.get("/triagem")
def triagem_padrao(request: Request, db: Session = Depends(get_db)):
    artigo = db.query(models.Artigo).filter(models.Artigo.status.in_([models.StatusArtigo.IMPORTADO, models.StatusArtigo.TRIAGEM])).first()
    if artigo:
        return RedirectResponse(url=f"/triagem/{artigo.projeto_id}", status_code=307)
    raise HTTPException(status_code=404, detail="Nenhum artigo pendente para triagem")


@app.get("/triagem/{projeto_id}")
def view_triagem(projeto_id: int, request: Request, db: Session = Depends(get_db)):
    projeto = obter_projeto(db, projeto_id)
    artigo_pendente = db.query(models.Artigo).filter(models.Artigo.projeto_id == projeto_id, models.Artigo.status.in_([models.StatusArtigo.IMPORTADO, models.StatusArtigo.TRIAGEM])).first()
    return templates.TemplateResponse(request=request, name="triagem.html", context={"artigo": artigo_pendente, "projeto": projeto})