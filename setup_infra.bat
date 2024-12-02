@echo off

rem check clients docker networks existence

docker network inspect clients > nul 2>&1
if %errorlevel% equ 0 (
    echo Network clients exists.
) else (
    docker network create clients --subnet 10.0.10.0/24
    echo Network clients created.
)

rem check servers docker network existence 

docker network inspect servers > nul 2>&1
if %errorlevel% equ 0 (
    echo Network servers exists.
) else (
    docker network create servers --subnet 10.0.11.0/24
    echo Network servers created.
)

rem check router docker image existence 

docker image inspect router > nul 2>&1
if %errorlevel% equ 0 (
    echo Image router exists.
) else (
    docker build -t router -f router/router.Dockerfile .
    echo Image router created.
)

rem check router container existence

docker container inspect router > nul 2>&1
if %errorlevel% equ 0 (
    docker container stop router
    docker container rm router
    echo Container router removed.
)

docker run -d --rm --name router router
echo Container router executed.

docker network connect --ip 10.0.10.100 clients router
docker network connect --ip 10.0.11.100 servers router

echo Container router connected to client and server networks

rem check client docker image existence 

docker image inspect client > nul 2>&1
if %errorlevel% equ 0 (
    echo Image client exists.
) else (
    docker build -t client -f frontend/client.Dockerfile frontend/
    echo Image client created.
)

docker image inspect server > nul 2>&1
if %errorlevel% equ 0 (
    echo Image server exists.
) else (
    docker build -t server -f backend/server.Dockerfile backend/
    echo Image server created.
)