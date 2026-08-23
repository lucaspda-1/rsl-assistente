from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Cria o arquivo rsl_assistant.db no diretório raiz do projeto
SQLALCHEMY_DATABASE_URL = "sqlite:///./rsl_assistant.db"

# connect_args={"check_same_thread": False} é necessário para o SQLite no FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency para injetar a sessão do banco nas rotas do FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()