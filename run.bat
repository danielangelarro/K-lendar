@echo off

docker build -t server -f backend/server.Dockerfile backend/
docker run -d -it --name server1 --cap-add NET_ADMIN --cap-add=NET_RAW --network servers --ip 10.0.11.3 -p 5000:5000 server  
docker run --cap-add NET_ADMIN --cap-add=NET_RAW -it --rm --name client1 --network clients --ip 10.0.10.5 -p 5173:5173 -p 8765:8765 client

docker run -d -it --name server1 --cap-add NET_ADMIN -e PYTHONUNBUFFERED=1 --network servers --ip 10.0.11.3 -p 5000:5000 server  
docker run --cap-add NET_ADMIN -e PYTHONUNBUFFERED=1 -it --rm --name client1 --network clients --ip 10.0.10.5 -p 5173:5173 -p 8765:8765 client

docker run -d --rm --name client1 ^
  -e PYTHONUNBUFFERED=1 ^
  --cap-add NET_ADMIN ^
  --network clients ^
  -p 5173:5173 ^
  client

docker run -d --rm --name client2 ^
  -e PYTHONUNBUFFERED=1 ^
  --cap-add NET_ADMIN ^
  --network clients ^
  --ip 10.0.10.2 ^
  -p 5174:5173 ^
  client

docker run -d --rm --name server1 ^
  -e PYTHONUNBUFFERED=1 ^
  --cap-add NET_ADMIN ^
  --network servers ^
  --ip 10.0.11.3 ^
  -p 8000:8000 ^
  server