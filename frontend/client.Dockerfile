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
RUN pip3 install websockets

# Copiar los scripts de supervisión al contenedor
COPY monitor.py /app/monitor.py
COPY monitor.sh /app/monitor.sh
COPY update_env.sh /app/update_env.sh
RUN chmod +x /app/monitor.sh /app/update_env.sh

EXPOSE 5173
EXPOSE 8765

# Ejecutar el script en segundo plano y luego iniciar la aplicación
CMD ["/bin/sh", "-c", "python3 /app/monitor.py & npm run dev"]
