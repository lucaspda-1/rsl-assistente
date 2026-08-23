# RSL Assistant

Assistente de Revisão Sistemática da Literatura (RSL) para gerenciamento de projetos, triagem com apoio de IA, extração de dados e acompanhamento do fluxo PRISMA 2020. A aplicação segue PICO/PICOC e mantém o pesquisador como responsável pela decisão final.

## Tecnologias

- **FastAPI**: API REST e servidor web.
- **SQLite e SQLAlchemy**: persistência e ORM.
- **Jinja2 e TailwindCSS**: interface web.
- **Pandas e OpenPyXL**: processamento e exportação para Excel.
- **Ollama**: análise opcional com modelo local.

## Instalação

Na raiz do projeto, crie e ative a venv:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requeriments.txt
```

No Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requeriments.txt
```

Se necessário, crie os arquivos de pacote:

```bash
touch app/__init__.py app/database/__init__.py app/routes/__init__.py app/services/__init__.py test/__init__.py
```

## Como executar

```bash
python -m uvicorn app.main:app --reload
```

Acesse:

- Dashboard: <http://127.0.0.1:8000/dashboard>
- Protocolo: <http://127.0.0.1:8000/protocolo>
- Artigos: <http://127.0.0.1:8000/artigos>
- Triagem: <http://127.0.0.1:8000/triagem>
- Swagger: <http://127.0.0.1:8000/docs>

As páginas também aceitam um projeto específico: `/dashboard/{projeto_id}`, `/protocolo/{projeto_id}`, `/artigos/{projeto_id}` e `/triagem/{projeto_id}`.

### Primeiro acesso

Se ainda não existir um projeto, clique em **+ Adicionar artigo** na barra superior. A aplicação exibirá o formulário para criar o primeiro projeto. Depois de salvar, o formulário de cadastro do artigo será aberto automaticamente.

Em um projeto existente, use **+ Adicionar artigo** para abrir diretamente o formulário manual. O cadastro exige apenas o título; os demais campos são opcionais.

## Testes

Com a venv ativada:

```bash
python -m pytest
```

## Fluxo PRISMA

Os artigos usam estados explícitos: `IMPORTADO`, `DUPLICADO`, `EXCLUIDO_TRIAGEM`, `LEITURA_COMPLETA`, `EXCLUIDO_TEXTO_COMPLETO` e `INCLUIDO`. A API registra a etapa da decisão com `TITULO_RESUMO` ou `TEXTO_COMPLETO`, separando corretamente as exclusões de cada fase.

## API principal

- `POST /projetos/` e `GET /projetos/`: criar e listar projetos.
- `POST /api/artigos/importar/{projeto_id}`: importar `.csv`, `.bib` ou `.bibtex`.
- `POST /api/artigos/`: cadastrar um artigo manualmente pelo frontend ou JSON.
- `GET /api/artigos/projeto/{projeto_id}`: listar artigos.
- `POST /api/artigos/triagem`: registrar uma decisão em JSON.
- `POST /api/artigos/deduplicar/{projeto_id}`: deduplicar por DOI ou título.
- `GET /exportacao/prisma/{projeto_id}`: consultar métricas PRISMA.
- `GET /exportacao/excel/{projeto_id}`: baixar o relatório Excel.

## Ollama (opcional)

Instale o Ollama, inicie o serviço e baixe o modelo desejado:

```bash
ollama pull llama3
export OLLAMA_URL=http://localhost:11434
export OLLAMA_MODEL=llama3
```

No PowerShell, use `$env:OLLAMA_URL` e `$env:OLLAMA_MODEL`. O código usa esses valores sem exigir alteração dos arquivos Python.

## Estrutura

```text
rsl-assistant/
├── app/
│   ├── main.py
│   ├── database/       # Conexão e modelos SQLite
│   ├── routes/         # Endpoints REST
│   ├── services/       # Importação, deduplicação, PRISMA, Excel e IA
│   └── templates/      # Páginas Jinja2
├── data/               # Uploads e exportações
├── test/               # Testes automatizados
├── requeriments.txt    # Dependências
└── README.md
```

O banco `rsl_assistant.db` é criado automaticamente. Na inicialização, bancos existentes recebem a coluna `etapa` da triagem quando ela ainda não existir.
