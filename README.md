# Employee REST API

This project is a FastAPI-based REST API for managing employee records and computing simple salary analytics. It uses SQLite for storage, SQLAlchemy for persistence, Pydantic v2 for request and response validation, and Pytest for automated testing.

## Setup Instructions

### Prerequisites

- Python 3.10 or newer
- `pip`

### Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy pydantic pytest
```

### Run the Application

```bash
uvicorn main:app --reload
```

### Open API Docs

```text
http://127.0.0.1:8000/docs
```

### Run Tests

```bash
pytest
```

## API Endpoints

### Employee CRUD

- `POST /employees/`
  Creates a new employee record.
- `GET /employees/`
  Returns all employees.
- `GET /employees/{emp_id}`
  Returns one employee by ID.
- `PUT /employees/{emp_id}`
  Updates an existing employee.
- `DELETE /employees/{emp_id}`
  Deletes an employee and returns a confirmation message.

### Salary and Metrics

- `GET /employees/{emp_id}/salary`
  Returns salary breakdown for one employee.
- `GET /metrics/country/{country}`
  Returns `min_salary`, `max_salary`, and `avg_salary` for the given country.
- `GET /metrics/job/{job_title}`
  Returns `avg_salary` for the given job title.

## Example Payloads

### Create or Update Employee

```json
{
  "full_name": "John Doe",
  "job_title": "Software Engineer",
  "country": "India",
  "salary": 50000
}
```

### Salary Response

```json
{
  "employee_id": 1,
  "full_name": "John Doe",
  "country": "India",
  "gross": 50000,
  "deduction": 5000,
  "net_salary": 45000
}
```

## Architecture Explanation

The codebase is split into a small set of focused modules:

- `main.py`
  Defines the FastAPI application, wires dependency injection for database sessions, creates tables on startup, and exposes the HTTP endpoints.
- `database.py`
  Configures the SQLite engine, SQLAlchemy session factory, and declarative base.
- `models.py`
  Defines the SQLAlchemy `Employee` table with `id`, `full_name`, `job_title`, `country`, and `salary`.
- `schemas.py`
  Defines the Pydantic v2 models used for request validation and response serialization.
- `crud.py`
  Contains database operations and domain logic such as employee CRUD, salary deduction rules, country aggregates, and average salary by job title.
- `test_main.py`
  Contains API-level tests using FastAPI’s `TestClient`.
- `test_crud.py`
  Contains CRUD and analytics tests directly against the database layer.

### Request Flow

1. A request hits a route in `main.py`.
2. The route gets a database session through `get_db()`.
3. The request body is validated using Pydantic schemas from `schemas.py`.
4. Business logic is delegated to `crud.py`.
5. SQLAlchemy models from `models.py` are persisted through the session defined in `database.py`.
6. The response is returned to the client.

### Salary Logic

The current deduction rules in `crud.py` are:

- `India`: 10% deduction
- `USA` or `United States`: 12% deduction
- Any other country: 0% deduction

## TDD Workflow

The repository already includes two layers of tests:

- `test_crud.py` for data and business logic
- `test_main.py` for HTTP endpoint behavior

A practical TDD workflow for this project is:

1. Write or update a failing test for the feature or bug.
2. Implement the smallest code change needed in `crud.py`, `schemas.py`, `models.py`, or `main.py`.
3. Re-run tests and confirm the new behavior passes.
4. Refactor carefully once tests protect the change.

This setup works well because business rules can be validated in `test_crud.py` first, then confirmed through the API layer in `test_main.py`.

## AI Usage Disclosure

AI tools used: ChatGPT

Usage:

- FastAPI route and Pydantic schema design guidance
- CRUD flow and salary analytics implementation suggestions
- test case suggestions for API and database operations
- refactoring ideas, including cleanup for Pydantic v2 syntax

## Future Improvements

- Align `test_main.py` with the current API paths and salary response keys used in `main.py` and `crud.py`
- Add a `requirements.txt` or `pyproject.toml` for reproducible dependency setup
- Add response models for salary and metrics endpoints for stronger API contracts
- Replace automatic table creation in `main.py` with proper migrations
- Add pagination and filtering to employee listing endpoints
- Add stricter validation for country names and salary bounds
- Improve README setup with virtual environment steps and version-pinned installs
