# Ritter Finder Project Structure

This project follows a scalable architecture pattern suitable for large API applications.

## Directory Structure

```
ritter-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                # Application entry point
│   ├── config.py              # Configuration settings (env vars, app settings)
│   ├── dependencies.py        # Shared dependencies
│   │
│   ├── api/                   # API routes and endpoints
│   │   ├── __init__.py
│   │   ├── v1/                # API versioning
│   │   │   ├── __init__.py
│   │   │   ├── router.py      # Main v1 router
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── users.py       # User endpoints
│   │   │   └── products.py    # Product endpoints
│   │   └── v2/                # Future API versions
│   │
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py        # JWT, password hashing, etc.
│   │   ├── database.py        # Database connection
│   │   └── exceptions.py      # Custom exceptions
│   │
│   ├── models/                # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── product.py
│   │
│   ├── schemas/               # Pydantic models (DTOs)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── product.py
│   │
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── product_service.py
│   │
│   ├── repositories/          # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user_repo.py
│   │   └── product_repo.py
│   │
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       └── helpers.py
│
├── tests/                     # Test files (mirrors app structure)
├── migrations/                # Alembic migration files
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

## Architecture Overview

### Key Design Principles

- **Separation of Concerns**: Each layer has a specific responsibility
- **API Versioning**: Enables backward compatibility as the API evolves
- **Service Layer Pattern**: Business logic is separated from API endpoints
- **Repository Pattern**: Data access is abstracted from business logic
- **Centralized Configuration**: All settings managed through `config.py`

### Layer Responsibilities

| Layer | Purpose |
|-------|---------|
| **API** | HTTP request/response handling, validation, serialization |
| **Services** | Business logic, orchestration of operations |
| **Repositories** | Data access, database queries |
| **Models** | Database schema definitions (SQLAlchemy) |
| **Schemas** | Request/response data models (Pydantic) |
| **Core** | Shared utilities, security, database connections |


## Getting Started

1. Clone the repository
2. Install dependencies: `uv sync`
3. Set up environment variables in `.env`
4. Start the application: `uv run uvicorn app.main:app --reload`

## API Documentation

Once the application is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`