#!/bin/sh

# Verificar que el script se está ejecutando
echo "Ejecutando run.sh"

# Modificar la tabla de rutas
ip route del default
ip route add default via 10.0.11.254

# Verificar la ruta por depuración
ip route show

# Iniciar la aplicación
exec poetry run python main.py