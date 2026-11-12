# MATH WEB Backend Deployment

## Production architecture

GitHub Pages frontend -> Render FastAPI backend -> SQLite database.

## Render settings

The repository already contains `render.yaml`. Create the Render Web Service from the `main` branch. The service name is `math-web-api-tralalerotralala2011`.

Build command:
`pip install -r requirements.txt`

Start command:
`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Health check:
`/health`

Expected API URL:
`https://math-web-api-tralalerotralala2011.onrender.com`

## Database note

SQLite is kept to preserve the existing project architecture. A Render service without a persistent disk has an ephemeral filesystem, so SQLite data can be lost after restarts/redeploys. For durable production accounts/XP, attach a Render persistent disk mounted at `/var/data` and set `MATHWEB_DB_PATH=/var/data/mathweb.db`, or migrate the database layer to managed Postgres later.

## Frontend

`js/api-config.js` automatically uses the Render API when the frontend is served from GitHub Pages, while localhost keeps using `http://127.0.0.1:8000`.
