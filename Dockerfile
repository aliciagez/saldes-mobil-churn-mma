FROM python:3.11-slim AS builder 

COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /bin/uv

#assuming api is i app-main.py
WORKDIR /app
COPY pyproject.toml /app/

ENV UV_PYTHON_DOWNLOADS=0

COPY src / ./src/
RUN uv sync --locked --no-dev
COPY outputs/ outputs/


FROM python:3.11-slim

RUN useradd --create-home app

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY app/ /app/

USER app


EXPOSE  8000

CMD ["uvicorn", "app.main.app", "--host", "0.0.0.0", "--port", "8000 "]