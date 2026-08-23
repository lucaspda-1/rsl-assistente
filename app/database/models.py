from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from .database import Base


# Status possível do artigo no fluxo PRISMA
class StatusArtigo(str, PyEnum):
    IMPORTADO = "IMPORTADO"
    DUPLICADO = "DUPLICADO"
    TRIAGEM = "TRIAGEM"
    EXCLUIDO_TRIAGEM = "EXCLUIDO_TRIAGEM"
    EXCLUIDO_TEXTO_COMPLETO = "EXCLUIDO_TEXTO_COMPLETO"
    # Mantido para leitura de bases antigas; novos registros usam estados específicos.
    EXCLUIDO = "EXCLUIDO"
    LEITURA_COMPLETA = "LEITURA_COMPLETA"
    INCLUIDO = "INCLUIDO"


class TipoCriterio(str, PyEnum):
    INCLUSAO = "INCLUSAO"
    EXCLUSAO = "EXCLUSAO"


class DecisaoTriagem(str, PyEnum):
    INCLUIR = "INCLUIR"
    EXCLUIR = "EXCLUIR"
    DUVIDA = "DUVIDA"


class EtapaTriagem(str, PyEnum):
    TITULO_RESUMO = "TITULO_RESUMO"
    TEXTO_COMPLETO = "TEXTO_COMPLETO"


class Projeto(Base):
    __tablename__ = "projetos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    protocolo = relationship("Protocolo", back_populates="projeto", uselist=False, cascade="all, delete-orphan")
    questoes = relationship("QuestaoPesquisa", back_populates="projeto", cascade="all, delete-orphan")
    criterios = relationship("Criterio", back_populates="projeto", cascade="all, delete-orphan")
    artigos = relationship("Artigo", back_populates="projeto", cascade="all, delete-orphan")
    buscas = relationship("Busca", back_populates="projeto", cascade="all, delete-orphan")


class Protocolo(Base):
    __tablename__ = "protocolos"

    id = Column(Integer, primary_key=True, index=True)
    projeto_id = Column(Integer, ForeignKey("projetos.id"), nullable=False, unique=True)
    objetivo = Column(Text, nullable=True)
    populacao = Column(Text, nullable=True)
    intervencao = Column(Text, nullable=True)
    comparacao = Column(Text, nullable=True)
    outcome = Column(Text, nullable=True)

    projeto = relationship("Projeto", back_populates="protocolo")


class QuestaoPesquisa(Base):
    __tablename__ = "questoes_pesquisa"

    id = Column(Integer, primary_key=True, index=True)
    projeto_id = Column(Integer, ForeignKey("projetos.id"), nullable=False)
    codigo = Column(String(10), nullable=False)  # Ex: RQ1
    pergunta = Column(Text, nullable=False)

    projeto = relationship("Projeto", back_populates="questoes")
    extracoes = relationship("Extracao", back_populates="questao", cascade="all, delete-orphan")


class Criterio(Base):
    __tablename__ = "criterios"

    id = Column(Integer, primary_key=True, index=True)
    projeto_id = Column(Integer, ForeignKey("projetos.id"), nullable=False)
    tipo = Column(Enum(TipoCriterio), nullable=False)
    codigo = Column(String(10), nullable=False)  # Ex: CI01, CE01
    descricao = Column(Text, nullable=False)

    projeto = relationship("Projeto", back_populates="criterios")


class Artigo(Base):
    __tablename__ = "artigos"

    id = Column(Integer, primary_key=True, index=True)
    projeto_id = Column(Integer, ForeignKey("projetos.id"), nullable=False)
    titulo = Column(String(500), nullable=False)
    autores = Column(Text, nullable=True)
    ano = Column(Integer, nullable=True)
    resumo = Column(Text, nullable=True)
    palavras_chave = Column(Text, nullable=True)
    doi = Column(String(100), nullable=True)
    url = Column(String(500), nullable=True)
    fonte = Column(String(100), nullable=True)  # Ex: IEEE, ACM, Scopus
    arquivo_pdf = Column(String(255), nullable=True)
    status = Column(Enum(StatusArtigo), default=StatusArtigo.IMPORTADO, nullable=False)
    data_importacao = Column(DateTime, default=datetime.utcnow)

    projeto = relationship("Projeto", back_populates="artigos")
    triagens = relationship("Triagem", back_populates="artigo", cascade="all, delete-orphan")
    extracoes = relationship("Extracao", back_populates="artigo", cascade="all, delete-orphan")


class Triagem(Base):
    __tablename__ = "triagens"

    id = Column(Integer, primary_key=True, index=True)
    artigo_id = Column(Integer, ForeignKey("artigos.id"), nullable=False)
    decisao = Column(Enum(DecisaoTriagem), nullable=False)
    etapa = Column(Enum(EtapaTriagem), default=EtapaTriagem.TITULO_RESUMO, nullable=False)
    motivo_exclusao = Column(Text, nullable=True)
    avaliacao_ia = Column(Text, nullable=True)
    confianca_ia = Column(Integer, nullable=True)  # 0 a 100%
    revisor = Column(String(100), default="Humano")
    data_avaliacao = Column(DateTime, default=datetime.utcnow)

    artigo = relationship("Artigo", back_populates="triagens")


class Extracao(Base):
    __tablename__ = "extracoes"

    id = Column(Integer, primary_key=True, index=True)
    artigo_id = Column(Integer, ForeignKey("artigos.id"), nullable=False)
    rq_id = Column(Integer, ForeignKey("questoes_pesquisa.id"), nullable=False)
    resposta = Column(Text, nullable=False)
    evidencia = Column(Text, nullable=True)
    revisor = Column(String(100), default="Humano")
    data = Column(DateTime, default=datetime.utcnow)

    artigo = relationship("Artigo", back_populates="extracoes")
    questao = relationship("QuestaoPesquisa", back_populates="extracoes")

class Busca(Base):
    __tablename__ = "buscas"

    id = Column(Integer, primary_key=True, index=True)
    projeto_id = Column(Integer, ForeignKey("projetos.id"), nullable=False)
    fonte = Column(String(100), nullable=False)  # Ex: IEEE Xplore, Scopus, ACM
    string_busca = Column(Text, nullable=False)
    data_busca = Column(DateTime, default=datetime.utcnow)
    total_encontrados = Column(Integer, default=0)

    projeto = relationship("Projeto", back_populates="buscas")

