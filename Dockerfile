FROM python:3.11-slim AS builder 

COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /bin/uv


WORKDIR /app
COPY pyproject.toml uv.lock ./


ENV UV_PYTHON_DOWNLOADS=0

COPY src / ./src/
RUN uv sync --locked --no-dev
COPY approved_models/ /app/approved_models/


FROM python:3.11-slim

RUN useradd --create-home app

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY approved_models/ /app/approved_models/

USER app


EXPOSE  8000

CMD ["uvicorn", "churn.app:app", "--host", "0.0.0.0", "--port", "8000"]