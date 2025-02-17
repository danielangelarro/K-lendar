FROM python:3.12-alpine AS base

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-root

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

RUN rm -rf database.sqlite && alembic upgrade head

CMD ["poetry", "run", "python", "main.py"]
