
FROM python:3.11-slim

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/
COPY src /app/src/

RUN poetry config virtualenvs.create false \
    && poetry install --no-root

CMD ["/bin/bash"]
