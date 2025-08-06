FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root

COPY ./src/backend /app/src/backend

CMD ["poetry", "run", "uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "3434"]
