@echo off

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