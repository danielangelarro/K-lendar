FROM python:3.12-alpine AS base

WORKDIR /app

# Instalar poetry
RUN pip install poetry

# Copiar archivos de configuración de dependencias
COPY pyproject.toml poetry.lock* ./

# Verificar contenido de los archivos copiados
RUN ls -la

# Crear entorno virtual con poetry
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-dev --no-interaction

# Copiar todo el proyecto
COPY . .

# Verificar contenido de la carpeta .venv
RUN ls -la .venv/bin

# Activar entorno virtual
ENV PATH="/app/.venv/bin:$PATH"

# Verificar que Python se está ejecutando del entorno virtual
RUN python --version
RUN which python

# Verificar instalación de Alembic
RUN which alembic

# Ejecutar migraciones
RUN alembic upgrade head

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]