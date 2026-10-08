# FastAPI Project

A small FastAPI app with a health check, in-memory items CRUD, and an Ollama-powered customer complaint triage API.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` if you want to change the app name, API prefix, or Ollama settings.

Ollama must be running locally (`ollama serve`) with the configured model, default `llama3.2:3b`.

## Run

```bash
uvicorn app.main:app --reload
```

Then open:

- API: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/health

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Welcome message |
| GET | `/api/health` | Health check |
| GET | `/api/items` | List items |
| POST | `/api/items` | Create item |
| GET | `/api/items/{id}` | Get one item |
| PATCH | `/api/items/{id}` | Update item |
| DELETE | `/api/items/{id}` | Delete item |
| POST | `/api/complaints` | Triage a complaint with Ollama and store a ticket |
| GET | `/api/complaints` | List tickets (`urgency`, `status` query filters) |
| GET | `/api/complaints/{id}` | Get one ticket |
| PATCH | `/api/complaints/{id}` | Update ticket status (`open`, `in_review`, `resolved`) |

## Tests

```bash
pytest
```
# complaints_mgt
