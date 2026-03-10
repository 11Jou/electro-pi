# Electro PI Task – FastAPI Backend

This project is a FastAPI backend that manages organizations, users, memberships, items, and audit logs, with JWT-based auth, PostgreSQL via SQLAlchemy, Alembic migrations, and an AI-powered chat endpoint over organization audit logs.

---

## 1. Architecture Overview

- **API framework**: FastAPI (async) with Pydantic v2 schemas.
- **Database**: PostgreSQL, accessed via SQLAlchemy 2.x async (`AsyncSession`).
- **Migrations**: Alembic (separate sync engine + URL from app’s async engine).
- **Auth**: Email + password, JWT tokens via `python-jose`.
- **Domain modules**:
  - `modules/auth`: user model, auth routes, JWT utilities.
  - `modules/organization`: organizations, memberships, items, audit logs, chat.
- **Repositories & services**:
  - Repositories (`modules/organization/repository/*`) encapsulate DB access.
  - Services (`modules/organization/services/*`) implement business logic.
  - Controllers (`modules/organization/controller.py`, `modules/auth/controller.py`) expose HTTP endpoints.
- **Config**: `core/config.py` using `pydantic-settings`, reading `project/.env`.
- **Chat bot**:
  - `modules/organization/services/chat_bot_service.py` defines a `IChatBotService` and `ChatGPTBotService` implementation using the OpenAI API.
  - `utils/factory.py` chooses concrete implementation using `CHAT_BOT_SERVICE` env var.
  - Controller exposes `POST /organization/{organization_id}/chat` using audit logs as context.

### Design tradeoffs

- **Repo/service split**: Controllers stay thin; data access logic is unit-testable and can be swapped out (e.g., for different storage or mocking).
- **Async app, sync migrations**: The app uses async DB access (`asyncpg`), but Alembic uses a sync engine with `psycopg2` for reliability and simplicity.
- **Audit logs centralization**: All audit creation goes through `AuditService` so logging is consistent and decoupled from core write operations.
- **AI integration via factory**: `get_chat_bot_service()` is isolated in `utils/factory.py` so adding providers (Anthropic, etc.) does not touch controllers.

---

## 2. Database Design

Core models live in `modules/organization/models.py` and `modules/auth/models.py`.

### 2.1 Users (`users`)

- `id` (PK, int)
- `full_name` (str, required)
- `email` (str, unique)
- `password` (hashed)
- `created_at`, `updated_at` (timezone-aware `DateTime`)
- Relationships:
  - `memberships`: one-to-many to `Membership`
  - `items`: one-to-many to `Item`
  - `audit_logs`: one-to-many to `AuditLog`

### 2.2 Organizations (`organizations`)

- `id` (PK, int)
- `name` (str, required)
- `created_at`, `updated_at`
- Relationships:
  - `memberships`: one-to-many to `Membership` (org members)
  - `items`: one-to-many to `Item`
  - `audit_logs`: one-to-many to `AuditLog`

### 2.3 Memberships (`memberships`)

- Composite PK: `(organization_id, user_id)`
- `organization_id` (FK → `organizations.id`)
- `user_id` (FK → `users.id`)
- `role` (enum `Role` = `ADMIN` or `MEMBER`)
- `created_at`, `updated_at`
- Relationships:
  - `organization` (many-to-one)
  - `user` (many-to-one)

Usage:

- Controls access to org endpoints (via `get_org_membership` and `require_org_admin`).
- Determines visibility of items (admins see all, members see their own).

### 2.4 Items (`items`)

- `id` (PK, int)
- `organization_id` (FK → `organizations.id`, indexed)
- `user_id` (FK → `users.id`, indexed) – creator/owner
- `details` (JSONB) – flexible payload per item
- `created_at`, `updated_at`
- Relationships:
  - `organization` (many-to-one)
  - `user` (many-to-one)

### 2.5 Audit Logs (`audit_logs`)

- `id` (PK, int)
- `user_id` (FK → `users.id`, indexed)
- `organization_id` (FK → `organizations.id`, indexed)
- `action` (str) – human-readable description, used by chat bot.
- `created_at`
- Relationships:
  - `user` (many-to-one)
  - `organization` (many-to-one)

Audit logs are created by `AuditService.log_action()` whenever:

- An organization is created.
- A membership is created.
- An item is created.

These logs form the context for the chat bot.

---

## 3. Running with Docker & docker-compose

The project ships with a `Dockerfile` and `docker-compose.yml` that:

- Build an image with the FastAPI app.
- Run PostgreSQL as `db`.
- Run Alembic migrations automatically before starting the app.

### 4.1 Environment variables for Docker

Create a `.env` file in the project root. You can copy from `.env.example`:

```bash
cp .env.example .env
```
Then Update the OPENAI_API_KEY

### 4.2 Build and start the container

```bash
docker compose up --build
```

This will:

1. Start PostgreSQL and wait until healthy.
2. Run `alembic upgrade head` in the backend container.
3. Start `uvicorn main:app --host 0.0.0.0 --port 8000`.

The API is available at `http://localhost:8000`.

---

## 6. Security & Access Control

- **JWT auth**:
  - `get_current_user` decodes JWT `sub` (email) and loads `User`.
- **Org admin checks**:
  - `require_org_admin` ensures the caller is an `ADMIN` member of the org.
- **Membership checks**:
  - `get_org_membership` ensures the caller is at least a member (`ADMIN` or `MEMBER`).
---

## 7. Extensibility Notes

- To add a new chat provider:
  - Implement `IChatBotService`.
  - Extend `get_chat_bot_service()` in `utils/factory.py` to select by `CHAT_BOT_SERVICE`.
- To add new audit events:
  - Call `AuditService.log_action()` from the relevant service after writes succeed.
