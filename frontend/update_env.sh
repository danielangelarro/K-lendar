#!/bin/sh

ENV_FILE="/app/.env"
while read -r message; do
    # Extraer IP y puerto del mensaje
    IFS=',' read -r ip port <<EOF
$message
EOF

    # Validar IP y puerto
    if [ -n "$ip" ] && [ -n "$port" ]; then
        echo "SERVER_URL=http://$ip:$port" > "$ENV_FILE"
        echo "Servidor descubierto: $ip:$port"
    else
        echo "Mensaje de servidor no válido: $message"
    fi
done
