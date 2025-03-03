#!/bin/sh

# Verificar que el script se está ejecutando
echo "Ejecutando run_client.sh"

# Modificar la tabla de rutas
ip route del default
ip route add default via 10.0.10.254

# Mostrar la configuración de la red para depuración
ip route show

# Iniciar los procesos requeridos
nohup sh /app/monitor.sh &
nohup python3 /app/monitor.py &

# Iniciar la aplicación FastAPI y el frontend
exec python3 client:app & npm run dev
