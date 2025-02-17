#!/bin/sh

# Configuración de variables
MULTICAST_GROUP="224.0.0.1"  # Reemplaza con la dirección del grupo multicast adecuada
PROXY_MULTICAST_PORT=10000   # Reemplaza con el puerto multicast adecuado
DELIMITER="<<DELIM>>"                # Reemplaza con el delimitador adecuado
ENV_FILE=".env"

# Crear el archivo .env si no existe
[ -f "$ENV_FILE" ] || touch "$ENV_FILE"

# Unirse al grupo multicast y escuchar mensajes
# Utilizando netcat para escuchar en el puerto UDP especificado
while true; do
    echo "Esperando datos en el grupo multicast $MULTICAST_GROUP:$PROXY_MULTICAST_PORT"

    # Recibir datos del socket multicast
    data=$(nc -lu -p "$PROXY_MULTICAST_PORT" 2>/dev/null)

    echo "Datos recibidos: $data"
    
    if [ -n "$data" ]; then
        echo "Datos recibidos: $data"

        # Separar la dirección IP y el puerto utilizando el delimitador
        node_ip=$(echo "$data" | cut -d"$DELIMITER" -f1)
        node_port=$(echo "$data" | cut -d"$DELIMITER" -f2)
        
        # Verificar que se hayan obtenido ambos valores
        if [ -n "$node_ip" ] && [ -n "$node_port" ]; then
            # Registrar el nodo descubierto
            echo "Descubierto nodo: $node_ip:$node_port"
            
            # Almacenar la información en el archivo .env
            {
                echo "NODE_IP=$node_ip"
                echo "NODE_PORT=$node_port"
            } >> "$ENV_FILE"
        else
            echo "Error: Datos recibidos en formato incorrecto: $data" >&2
        fi
    fi
done
