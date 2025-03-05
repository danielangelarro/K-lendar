FROM node:14-alpine AS builder

WORKDIR /app

RUN apk add --no-cache python3 py3-pip netcat-openbsd socat iproute2 dos2unix

COPY package*.json ./
COPY . .

RUN npm cache clean --force && \
    rm -rf node_modules package-lock.json && \
    npm install && \
    npm rebuild esbuild

RUN pip3 install websockets fastapi uvicorn requests

# Copiar los scripts de supervisión y configuración de red
COPY monitor.py /app/monitor.py
COPY monitor.sh /app/monitor.sh
COPY update_env.sh /app/update_env.sh
COPY run_client.sh /app/run_client.sh

# Asegurar que los scripts tengan permisos de ejecución y formato correcto
RUN chmod +x /app/monitor.sh /app/update_env.sh /app/run_client.sh \
    && dos2unix /app/monitor.sh /app/update_env.sh /app/run_client.sh \
    && sed -i 's/\r$//' /app/run_client.sh

EXPOSE 5173

# Ejecutar el script de arranque al iniciar el contenedor
CMD ["/bin/sh", "/app/run_client.sh"]
