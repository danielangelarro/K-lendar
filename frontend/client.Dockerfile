FROM node:14-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY . .

RUN npm cache clean --force && \
    rm -rf node_modules package-lock.json && \
    npm install && \
    npm rebuild esbuild

# Instalar Python, netcat y socat para manejar conexiones multicast
RUN apk add --no-cache python3 py3-pip netcat-openbsd socat iproute2
RUN pip3 install websockets fastapi uvicorn requests

# Copiar los scripts de supervisión al contenedor
COPY monitor.py /app/monitor.py
COPY monitor.sh /app/monitor.sh
COPY update_env.sh /app/update_env.sh
RUN chmod +x /app/monitor.sh /app/update_env.sh

EXPOSE 5173
EXPOSE 8765

# Definir variables de entorno para el host y el puerto
ENV FASTAPI_HOST=0.0.0.0
ENV FASTAPI_PORT=8765

# Ejecutar el script en segundo plano y luego iniciar la aplicación
CMD ["sh", "-c", "uvicorn client:app --host $FASTAPI_HOST --port $FASTAPI_PORT & npm run dev"]