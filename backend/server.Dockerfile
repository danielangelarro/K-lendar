FROM python:3.12-alpine AS base

WORKDIR /app

RUN apk add --no-cache iproute2 bash dos2unix
RUN pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-root

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

RUN rm -rf database.sqlite && alembic upgrade head

COPY run_server.sh /app
RUN chmod +x /app/run_server.sh && dos2unix /app/run_server.sh
RUN sed -i 's/\r$//' /app/run_server.sh

CMD ["/bin/sh", "/app/run_server.sh"]
