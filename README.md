# Space Bounty Hunters API

REST API for space bounty hunters: a database of **wanted criminals** (with filters and sorting) and a **hunt journal** of capture attempts (full CRUD).

**Stack:** Django 5.2 · Django REST Framework · PostgreSQL 16 · Docker Compose · Gunicorn

## Run

Requirements: Docker Desktop.

```bash
cp .env.example .env        # Windows: copy .env.example .env
# open .env and set DB_PASSWORD, DJANGO_SECRET_KEY, DJANGO_SUPERUSER_PASSWORD
docker compose up --build
```

API: http://127.0.0.1:8000/api/criminals/  ·  Admin: http://127.0.0.1:8000/admin/

If port 8000 is busy (e.g. another project is running), set `HOST_PORT=8001` in `.env`.

Stop: `docker compose down` (data is kept in the `bounty-pgdata` volume). Full reset: `docker compose down -v`.

## Database setup / import

Done automatically on container start by `backend/entrypoint.sh`:

1. `python manage.py migrate` creates the tables.
2. If `SEED_DATA=true` and the database has no criminals yet, `python manage.py loaddata seed` imports
   `backend/bounty/fixtures/seed.json`: **6 criminals and 12 hunt logs**.

Manual import (e.g. after a reset):

```bash
docker compose exec backend python manage.py loaddata seed
```

## Data model

```
WantedCriminal 1 ──── * HuntLog      (HuntLog.criminal → ForeignKey, on_delete=CASCADE, related_name="hunt_logs")
```

**WantedCriminal**: `id`, `name` (may be empty = unknown), `nickname`, `reward`,
last known location (`last_known_latitude`, `last_known_longitude`, `last_known_note`, all optional),
`difficulty` (1–10, validated and enforced by a DB check constraint), `armed`, `has_crew`, `escape_master`.

**HuntLog**: `id`, `criminal` (FK), `success`, `notes`, `created_at` (`auto_now_add`, set by the server only).

## Endpoints

| Method | URL | Description | Success | Errors |
|---|---|---|---|---|
| GET | `/api/criminals/` | list with filters and sorting | 200 | 400 invalid parameter |
| GET | `/api/criminals/{id}/` | one criminal | 200 | 404 |
| GET | `/api/hunts/` | list hunt logs, `?criminal_id=` filter | 200 | 400 invalid id, 404 unknown criminal |
| POST | `/api/hunts/` | record a capture attempt | 201 | 400 |
| GET | `/api/hunts/{id}/` | one hunt log | 200 | 404 |
| PATCH | `/api/hunts/{id}/` | update `success` / `notes` | 200 | 400, 404 |
| DELETE | `/api/hunts/{id}/` | delete a hunt log | 204 | 404 |

`PUT /api/hunts/{id}/` is not supported (405): updates are partial (PATCH).

### Criminal filters (all combine together)

| Parameter | Example | Meaning |
|---|---|---|
| `min_reward` | `5000` | reward ≥ value |
| `max_reward` | `20000` | reward ≤ value |
| `armed`, `has_crew`, `escape_master` | `true` / `false` | filter by attribute |
| `sort` | `reward` / `-reward` | ascending / descending by reward |

```
GET /api/criminals/?min_reward=5000&armed=true&sort=-reward
```

Invalid values (`min_reward=abc`, `armed=maybe`, `sort=name`, `min_reward` > `max_reward`) return **400** with a message.

### Example criminal

```json
{
  "id": 2, "name": "", "nickname": "The Ghost", "reward": 25000,
  "last_known_location": {"latitude": null, "longitude": null, "note": "Hiding somewhere in the Outer Rim nebula"},
  "difficulty": 10, "armed": true, "has_crew": false, "escape_master": true, "hunt_count": 2
}
```

### Create a hunt log

```http
POST /api/hunts/
Content-Type: application/json

{"criminal_id": 3, "success": false, "notes": "Target escaped through an asteroid field."}
```

→ `201 Created`

```json
{"id": 13, "criminal_id": 3, "criminal_nickname": "Silver Fox", "success": false,
 "notes": "Target escaped through an asteroid field.", "created_at": "2026-10-31T13:05:33+05:00"}
```

Validation:
- `criminal_id` must reference an existing criminal → otherwise `400 {"criminal_id": ["Invalid pk \"999\" - object does not exist."]}`
- `criminal_id` and `success` are required; `success` must be a boolean
- `created_at` is read-only: a value sent by the client is ignored
- `criminal_id` can't be changed with PATCH (400)

## Postman

`postman/Space_Bounty_Hunters.postman_collection.json`: 13 requests, run in order.

1. List criminals; combined filters and sorting (`min_reward`, `max_reward`, `armed`, `has_crew`, `escape_master`, `sort`); criminal details.
2. Hunt logs: list, filter by `criminal_id`, create (saves `hunt_id`), read, update (PATCH), delete.
3. Invalid requests: non-existent criminal in POST (400), invalid `armed` filter (400), unknown criminal (404).

Import → right-click the collection → **Run collection**. Variable `base_url` = `http://127.0.0.1:8000` (change the port if `HOST_PORT` is different).

## Project structure

```
backend/
  config/            settings (all secrets from environment variables), urls
  bounty/
    models.py        WantedCriminal, HuntLog
    serializers.py   JSON <-> models, validation
    views.py         generic DRF views, query-parameter filters
    urls.py
    admin.py
    fixtures/seed.json   seed data
  Dockerfile
  entrypoint.sh      migrate → import seed data → create admin → gunicorn
  requirements.txt
compose.yaml         db (PostgreSQL) + backend, network bounty-net, volume bounty-pgdata
.env.example
postman/           Postman collection
```