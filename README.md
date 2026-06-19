# Coolify CRUD Demo - db_app1

App mínima para probar el flujo:

GitHub → Coolify → Docker → FastAPI → PostgreSQL nativo en Ubuntu Server.

## Stack

- FastAPI
- PostgreSQL
- Docker
- Coolify

## Variables de entorno

Copiar `.env.example` a `.env` para pruebas locales, o cargar estas variables en Coolify:

```env
DB_HOST=10.5.0.122
DB_PORT=5432
DB_NAME=db_app1
DB_USER=db_app1
DB_PASSWORD=therian_app1
```

## Endpoints

- `GET /` health check
- `GET /db-check` prueba de conexión a DB
- `GET /notes` listar notas
- `GET /notes/{id}` obtener nota
- `POST /notes` crear nota
- `PUT /notes/{id}` actualizar nota
- `DELETE /notes/{id}` eliminar nota
- `GET /docs` Swagger UI

## Prueba con Docker

```bash
docker build -t coolify-crud-db-app1 .

docker run --rm -p 8001:8000 \
  -e DB_HOST=10.5.0.122 \
  -e DB_PORT=5432 \
  -e DB_NAME=db_app1 \
  -e DB_USER=db_app1 \
  -e DB_PASSWORD=therian_app1 \
  coolify-crud-db-app1
```

Probar:

```bash
curl http://localhost:8001/
curl http://localhost:8001/db-check
curl http://localhost:8001/notes
```

Crear nota:

```bash
curl -X POST http://localhost:8001/notes \
  -H "Content-Type: application/json" \
  -d '{"title":"Nota desde API","content":"Creada desde contenedor Docker"}'
```

## Coolify

Configurar como app Dockerfile:

- Build Pack: Dockerfile
- Internal Port: 8000
- Variables de entorno: las indicadas arriba

