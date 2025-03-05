#!/bin/sh

# Verificar que el script se está ejecutando
echo "Ejecutando run_client.sh"

# Modificar la tabla de rutas
ip route del default
ip route add default via 10.0.10.254

sleep 5
# Mostrar la configuración de la red para depuración
ip route show

# Iniciar los procesos requeridos
nohup python3 client.py &

# Iniciar el front
exec npm run dev
