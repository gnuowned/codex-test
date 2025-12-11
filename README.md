# Customer Registry API

Aplicación FastAPI en Python con SQLite para altas, bajas, cambios y consultas de clientes.

## Campos mínimos
- name (string)
- email (string, único)
- phone (string)
- status (string, p.ej. "active" | "inactive")
- notes (string opcional)

## Desarrollo local (Python 3.11/3.12 recomendado)
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Visita `http://localhost:8000/docs` para probar. En macOS con Python 3.14 puede fallar por PyO3/pydantic-core; usa 3.12 o ejecuta vía Docker.

## Docker
```bash
docker build -t customer-registry .
docker run -p 8000:8000 -v $(pwd)/data:/app/data customer-registry
```
El volumen `./data` preserva `data.db` fuera del contenedor.

## Endpoints
- `GET /customers` lista
- `POST /customers` crea
- `GET /customers/{id}` detalle
- `PUT /customers/{id}` actualiza
- `DELETE /customers/{id}` elimina

## Notas
- La base se crea automáticamente (`data.db`).
- Ajusta validaciones, autenticación o estado permitido según necesidades.
