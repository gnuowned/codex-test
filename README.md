# Customer Registry API

Aplicación Starlette (Python 3.14 compatible) con SQLite y consultas directas (sin ORM) para altas, bajas, cambios y consultas de clientes.

## Campos mínimos
- name (string)
- email (string, único)
- phone (string)
- status (string, p.ej. "active" | "inactive")
- notes (string opcional)

## Desarrollo local (Python 3.14)
```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Visita `http://localhost:8000/customers` o usa herramientas como curl para probar.

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
- La base se crea automáticamente (`data.db`) sin necesidad de ORM.
- Validación ligera manual (longitudes y email con "@"); ajusta reglas según negocio.

## Ejemplos rápidos (curl)
- Crear:
```bash
curl -X POST http://localhost:8000/customers \
  -H "Content-Type: application/json" \
  -d '{"name":"Ada Lovelace","email":"ada@example.com","phone":"+1-555","status":"active","notes":"VIP"}'
```
- Listar: `curl http://localhost:8000/customers`
- Detalle: `curl http://localhost:8000/customers/1`
- Actualizar: 
```bash
curl -X PUT http://localhost:8000/customers/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"inactive","notes":"paused"}'
```
- Borrar: `curl -X DELETE http://localhost:8000/customers/1`

Errores esperados:
- Email duplicado: 400 `{"detail":"email already exists"}`
- Cliente no encontrado (GET/PUT/DELETE): 404 `{"detail":"Customer not found"}`

## Interfaz web
- Visita `http://localhost:8000/ui` (sirve `static/index.html`).
- Incluye formulario para crear, leer, actualizar y borrar, además de tabla de listado.

## Pruebas
```bash
pip install -r requirements.txt
pytest
```
