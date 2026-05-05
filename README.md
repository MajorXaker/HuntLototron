# HuntLototron (Huntotron)

A FastAPI backend for tracking and analysing matches of *Hunt: Showdown*. The
service stores match results (loadouts, K/D/A, bounty, fight locations,
playtime, win/lose/flee status) and produces analytics across maps, weapons and
teammates. Data lives in PostgreSQL; the schema is managed with Alembic.

> Originally a Russian-language CLI roulette that picked random gun loadouts
> ("can you prove you can do magic with two shotguns?"). It has since been
> rewritten as a single-tenant FastAPI service backing a separate frontend.
> The legacy Django apps (`HuntLototron/`, `roulette/`, `stats/`) are gone — only
> their stale `.pyc` files lingered in git; they are removed in this commit.

## Tech stack

- **Python** 3.13 (pinned via `pyproject.toml`)
- **Web framework**: FastAPI + Uvicorn
- **ORM / DB**: SQLAlchemy 2.x (async) + asyncpg, PostgreSQL 15.1
- **Migrations**: Alembic
- **Validation**: Pydantic v2, Beartype
- **Config**: Dynaconf (`settings.toml`, `.secrets.toml`, env)
- **Observability**: prometheus-fastapi-instrumentator, sentry-sdk (initialised
  block currently commented out in `config.py`)
- **Tooling**: uv (package manager), ruff, black, pytest, pytest-asyncio,
  coverage, freezegun

## Repository structure

```
.
├── main.py                    # FastAPI app + router registration + uvicorn entrypoint
├── config.py                  # Dynaconf settings loader
├── db.py                      # Async SQLAlchemy engine + session dependencies
├── heartbeat.py               # /__version__, /__heartbeat__, /__lbheartbeat__
├── settings.toml              # Default + test Dynaconf profiles
├── pyproject.toml             # Project metadata + deps (managed by uv)
├── uv.lock                    # uv lockfile
├── Dockerfile                 # uv + python3.13-alpine image
├── docker-compose.yaml        # postgres:15.1 service for local dev
├── Makefile                   # clean / install / migrate / run / lint / test / docker
├── lint.sh                    # ruff helper used by `make lint`
├── alembic.ini, alembic/      # migration config + versioned migrations
├── api/                       # HTTP routers (one module per resource)
│   ├── router_ammo_types.py
│   ├── router_analytics.py
│   ├── router_compounds.py
│   ├── router_maps.py
│   ├── router_match.py
│   ├── router_players.py
│   ├── router_weapon_types.py
│   ├── router_weapons.py
│   └── service_endpoints.py
├── logic/analytics/           # Stat aggregation queries (maps / weapons / teammates)
├── models/
│   ├── db_models/             # SQLAlchemy ORM models
│   ├── schemas/               # Pydantic request/response schemas
│   ├── enums/                 # StrEnums for game modes, statuses, weapon mods
│   └── dto/                   # Plain DTOs used by analytics responses
├── tests/                     # pytest suite + test DB setup (creator.py, conftest.py)
└── utils/typechecking.py
```

## Prerequisites

- Python **3.13.x**
- [`uv`](https://docs.astral.sh/uv/) (`make install-uv` will install it)
- PostgreSQL 15 (run via `docker compose up -d postgres`)
- GNU Make, Docker + docker compose (optional, for the bundled stack)

## Setup

```sh
# 1. install uv + create venv + install deps
make install

# 2. start a local PostgreSQL (5432, user/pass/db = postgres/postgres/huntotron)
docker compose up -d postgres

# 3. apply schema migrations
uv run alembic upgrade head
```

## Configuration

Configuration is layered through Dynaconf. Defaults live in `settings.toml`;
secrets and overrides go in `.secrets.toml` (gitignored) or environment
variables prefixed with `DYNACONF_`. The `ENV_FOR_DYNACONF` variable selects a
profile (`default`, `development`, `test`).

| Key                  | Default      | Purpose                                              |
| -------------------- | ------------ | ---------------------------------------------------- |
| `APPNAME`            | `Huntotron`  | App title (FastAPI + connection `application_name`) |
| `VERSION`            | `0.2.1`      | Reported by `/__version__`                           |
| `DATABASE_HOST`      | `localhost`  | PostgreSQL host (`postgres` in test profile)        |
| `DATABASE_PORT`      | `5432`       |                                                      |
| `DATABASE_USER`      | `postgres`   |                                                      |
| `DATABASE_PASSWORD`  | `postgres`   |                                                      |
| `DATABASE_DB`        | `huntotron`  | (`test-db` in test profile)                          |
| `DATABASE_ECHO_MODE` | `false`      | SQLAlchemy echo                                      |
| `DB_CONN_MAX_OVERFLOW` | `25`       | Pool overflow                                        |
| `MAIN_CHARACTER_ID`  | `0`          | Single-player ID; analytics K/D/A is scoped to this |
| `PIPELINE_ID`, `SOURCE`, `GIT_COMMIT` | — | Surfaced via `/__version__`               |

Provide secrets via `.secrets.toml` or env, e.g.:

```sh
export ENV_FOR_DYNACONF=development
export DYNACONF_DATABASE_PASSWORD=...
```

## Running

Local (after `make install`):

```sh
uv run main.py
# or
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

Docker (the bundled `Dockerfile` runs `alembic upgrade head` then `main.py`):

```sh
docker build -t huntotron .
docker run --rm -p 8000:8000 --env DATABASE_HOST=host.docker.internal huntotron
```

When `ENV_FOR_DYNACONF` is `default` or `development`, `GET /` redirects to the
Swagger UI at `/openapi/swagger`. ReDoc is at `/openapi/redoc`. Prometheus
metrics are exposed at `/metrics`.

## Tests / lint

```sh
make test         # ENV_FOR_DYNACONF=test pytest
make lint         # ruff check + ruff format --check (diff against origin/master)
make format       # black + ruff --fix
make clean        # rm __pycache__, .pytest_cache, .mypy_cache, htmlcov, .coverage
```

`make test` expects the test profile DB (`test-db` on host `postgres`) to be
reachable; `tests/setup_test_db.py` and `tests/creator.py` provision schema and
fixtures.

## API

Interactive docs: **`/openapi/swagger`** (Swagger), **`/openapi/redoc`** (ReDoc),
OpenAPI JSON at the FastAPI default. No authentication is enforced; the service
is intended to be deployed behind a private network or reverse proxy. Errors
follow FastAPI's standard `{"detail": "..."}` JSON shape with HTTP status codes
listed below.

### Service / health

| Method | Path              | Purpose                                                                  |
| ------ | ----------------- | ------------------------------------------------------------------------ |
| GET    | `/`               | Redirects (302) to `/openapi/swagger` (only in `default`/`development`)  |
| GET    | `/__version__`    | `{build, version, source, commit}` from settings                         |
| GET    | `/__heartbeat__`  | DB ping; returns 200 `{status, random, checks}` or 500 on DB error       |
| GET    | `/__lbheartbeat__`| 200 OK liveness probe                                                    |
| GET    | `/metrics`        | Prometheus metrics (instrumented by `prometheus-fastapi-instrumentator`) |
| GET    | `/service/modification-types` | Enumerates all weapon modifier values (ammo size, sights, melee, muzzle, magazine, weapon size) |

### Ammo Types — `/ammo-types`

| Method | Path                       | Body / params                                          | Returns                              | Errors           |
| ------ | -------------------------- | ------------------------------------------------------ | ------------------------------------ | ---------------- |
| GET    | `/ammo-types`              | `skip` (int, default 0), `limit` (int, default 100)    | `[AmmoTypeResponse]`                 | —                |
| GET    | `/ammo-types/{id}`         | path: `id` (int)                                       | `AmmoTypeResponse`                   | 404              |
| POST   | `/ammo-types`              | `AmmoTypeCreate {name}`                                | `AmmoTypeResponse` (201)             | —                |
| PATCH  | `/ammo-types/{id}`         | `AmmoTypeUpdate {name?}`                               | `AmmoTypeResponse`                   | 404              |
| DELETE | `/ammo-types/{id}`         | path: `id` (int)                                       | 204                                  | 404              |

`AmmoTypeResponse = {id: int, name: str}`.

### Weapon Types — `/weapon-types`

| Method | Path                       | Body / params                                          | Returns                              | Errors                  |
| ------ | -------------------------- | ------------------------------------------------------ | ------------------------------------ | ----------------------- |
| GET    | `/weapon-types`            | `skip`, `limit`                                        | `[WeaponTypeResponse]`               | —                       |
| GET    | `/weapon-types/{id}`       | path: `id`                                             | `WeaponTypeResponse`                 | 404                     |
| POST   | `/weapon-types`            | `WeaponTypeCreate {name}`                              | `WeaponTypeResponse` (201)           | 400 empty, 409 conflict |
| PATCH  | `/weapon-types/{id}`       | `WeaponTypeUpdate {name?}`                             | 202 (no body)                        | 404                     |
| DELETE | `/weapon-types/{id}`       | path: `id`                                             | 204                                  | 404                     |

### Weapons — `/weapons`

| Method | Path                | Query / body                                                                                      | Returns                  | Errors                |
| ------ | ------------------- | ------------------------------------------------------------------------------------------------- | ------------------------ | --------------------- |
| GET    | `/weapons`          | `skip`, `limit`, `ammo_size` (`AmmoSizeEnum`), `core_gun_id`, `core_gun_only` (bool), `weapon_type_id` | `[WeaponResponse]`        | —                     |
| GET    | `/weapons/{id}`     | path: `id`                                                                                        | `WeaponResponse`         | 404                   |
| POST   | `/weapons`          | `WeaponCreate` (name, weapon_type_id, slot_size 1–3, sights, melee, muzzle, magazine, weapon_size, ammo_size, price ≥0, has_ammo_B, optional core_gun_id) | `WeaponResponse` (201) | 400 dup name |
| PATCH  | `/weapons/{id}`     | `WeaponUpdate` (any field optional)                                                               | `WeaponResponse`         | 400 self-ref, 404     |
| DELETE | `/weapons/{id}`     | path: `id`                                                                                        | 204                      | 404                   |

### Maps — `/maps`

| Method | Path           | Body / params         | Returns               | Errors           |
| ------ | -------------- | --------------------- | --------------------- | ---------------- |
| GET    | `/maps`        | —                     | `[MapResponse]`       | —                |
| GET    | `/maps/{id}`   | path: `id`            | `MapResponse`         | 404              |
| POST   | `/maps`        | `MapCreate {name}`    | `MapResponse` (201)   | 400 dup name     |
| DELETE | `/maps/{id}`   | path: `id`            | 204                   | 404              |

### Compounds — `/compounds`

Compounds are named fight locations on a map.

| Method | Path                | Query / body                                  | Returns               | Errors                       |
| ------ | ------------------- | --------------------------------------------- | --------------------- | ---------------------------- |
| GET    | `/compounds`        | `skip`, `limit`, `map_id` (filter)            | `[CompoundResponse]`  | —                            |
| GET    | `/compounds/{id}`   | path: `id`                                    | `CompoundResponse`    | 404                          |
| POST   | `/compounds`        | `CompoundCreate {name, map_id, double_clue}`  | `CompoundResponse` (201) | 400 dup name on the map |
| PATCH  | `/compounds/{id}`   | `CompoundUpdate {map_id?, double_clue?}`      | `CompoundResponse`    | 404                          |
| DELETE | `/compounds/{id}`   | path: `id`                                    | 204                   | 404                          |

### Players — `/players`

| Method | Path               | Query / body                                            | Returns               | Errors                  |
| ------ | ------------------ | ------------------------------------------------------- | --------------------- | ----------------------- |
| GET    | `/players`         | `skip`, `limit`, `include_disabled` (bool, default false; default lists only `ACTIVE`) | `[PlayerResponse]` | — |
| GET    | `/players/{id}`    | path: `id`                                              | `PlayerResponse`      | 404                     |
| POST   | `/players`         | `PlayerCreate {username}`                               | `PlayerResponse` (201) | 400 missing username   |
| PATCH  | `/players/{id}`    | `PlayerUpdate {username?, is_disabled?}` (toggles status ACTIVE/INACTIVE) | `PlayerResponse` | 404 |
| DELETE | `/players/{id}`    | path: `id`                                              | 204                   | 404                     |

### Matches — `/matches`

Match flow: create the match (records loadout for player_1), then `POST
/matches/results` with K/D/A, win/lose/flee, playtime, map and an ordered list
of compound IDs (`fights_places_ids`). `_get_matches` joins `Match` with the
three `MatchPlayerData` aliases and aggregates compound IDs from
`M2MFightLocations` ordered by `fight_ordering`.

| Method | Path                          | Body / params                          | Returns                              | Errors |
| ------ | ----------------------------- | -------------------------------------- | ------------------------------------ | ------ |
| POST   | `/matches`                    | `NewMatchSchema` (date, player_1_id required, player_2/3_id optional, slot_a/b loadout, `game_mode` HUNT/QUICKPLAY/CLASH) | `ShortMatchResponseSchema {match_id}` (201) | — |
| POST   | `/matches/results`            | `CreateMatchResultSchema` (match_id, wl_status WIN/LOSE/FLEE, kills_total, kills, assists, deaths, bounty, playtime [ISO 8601 duration], map_id, fights_places_ids) | `ShortMatchResponseSchema` (201) | 404 unknown match |
| GET    | `/matches`                    | `ordering` ASC/DESC (default DESC), `limit` 1–100 (default 50), `offset` ≥0 | `GetMatchesSchema {data: [FullMatchSchema], total_results}` | — |
| GET    | `/matches/specific/{match_id}`| path                                   | Same as above with single result      | 404    |
| PATCH  | `/matches/{match_id}`         | `UpdateMatchSchema` (full payload; player_1_id is ignored — single-player constraint) | `ShortMatchResponseSchema` | 404 |
| DELETE | `/matches/{match_id}`         | path                                   | `ShortMatchResponseSchema`           | 404    |

`FullMatchSchema` includes nested `player_1_data`/`player_2_data`/`player_3_data`
(`MatchPlayerSchema` — loadout + K/D/A/bounty), `wl_status`, `playtime`
(seconds), `map_id`, `fights_places_ids`, `game_mode`. `playtime` is returned
as integer seconds (the timedelta is converted via `total_seconds()`).

### Analytics — `/analytics`

All endpoints accept a `game_mode` query (`hunt`/`clash`/`quickplay`, default
`hunt`); invalid values return 400 `{"detail": "Invalid game_mode"}`. Results
are scoped to the single tracked player (`MAIN_CHARACTER_ID`).

| Method | Path                  | Returns                                                                  |
| ------ | --------------------- | ------------------------------------------------------------------------ |
| GET    | `/analytics/teammates`| `TeammateAnalytics {matches_total, by_teammates: [TeammateStats], by_team_compositions: [TeamCompositionStats]}` |
| GET    | `/analytics/weapons`  | `WeaponAnalytics {matches_total, by_weapons: [WeaponStats]}`             |
| GET    | `/analytics/maps`     | `MapAnalytics {matches_total, by_maps: [MapStats]}`                      |

`*Stats` DTOs (in `models/dto/teammate_stats.py`) include match counts, win/
loss/flee splits, K/D/A and playtime aggregations.

## Cleanup performed in this branch

The following stale build artefacts were tracked in git and have been removed.
They came from the old Django incarnation (`HuntLototron/`, `roulette/`,
`stats/`) whose `.py` sources were deleted during the FastAPI migration —
only the Python 3.8 bytecode caches were left behind:

- `HuntLototron/__pycache__/*.cpython-38.pyc` — 10 files
- `roulette/__pycache__/*.cpython-38.pyc` — 7 files
- `stats/__pycache__/*.cpython-38.pyc` — 8 files

Total: **25 `.pyc` files** removed, leaving the parent directories empty (and
thus removed by git). `.gitignore` already contains `__pycache__/` and
`*.py[cod]`, so future caches will not be re-committed; no `.gitignore` change
was necessary.

## License

See `LICENSE` (MIT-style; check the file for the canonical terms).
