FROM python:3.11

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /bin/uv

COPY pyproject.toml /app/

COPY src / ./src/
RUN uv sync --locked --no-dev



ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "consumer.py"]