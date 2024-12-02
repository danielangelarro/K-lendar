#!/bin/sh

ip route del default
ip route add default via 10.0.10.100

# Construye la imagen Docker
docker build -t react-client -f client.Dockerfile .

# Ejecuta el contenedor en la red clients
docker run -d --rm --name react-client \
  --network clients \
  --ip 10.0.10.100 \
  react-client