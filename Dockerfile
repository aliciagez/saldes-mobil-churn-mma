FROM python:3.11-slim AS builder 

COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /bin/uv

WORKDIR /app

ENV UV_PYTHON_DOWNLOADS=0

COPY pyproject.toml uv.lock ./

COPY src/ ./src/

RUN uv sync --locked --no-dev



FROM python:3.11-slim

RUN useradd --create-home app

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY --from=builder /app/src /app/src

ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONPATH="app/src"

COPY approved-model/ approved-model/

USER app

EXPOSE  8000

CMD ["uvicorn", "churn.app:app", "--host", "0.0.0.0", "--port", "8000"]