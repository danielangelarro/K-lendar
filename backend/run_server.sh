#!/bin/sh

ip route del default
ip route add default via 10.0.11.254

# Construye la imagen Docker
docker build -t fastapi-server -f server.Dockerfile .

# Ejecuta el contenedor en la red servers
docker run -d --rm --name fastapi-server \
  --network servers \
  --ip 10.0.11.100 \
  fastapi-server