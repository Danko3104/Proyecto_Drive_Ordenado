#!/bin/bash

# Script para iniciar el túnel Cloudflare de forma visible
# Uso: ./start_tunnel.sh

echo "==================================="
echo "  INICIANDO TÚNEL CLOUDFLARE"
echo "==================================="
echo ""

# Iniciar cloudflared en segundo plano y capturar la URL
cloudflared tunnel --url http://localhost:5000 2>&1 &
TUNNEL_PID=$!

# Esperar a que genere la URL
echo "⏳ Generando URL segura..."
echo ""

sleep 5

# Obtener la URL del log (esto es aproximado, se ajusta según el sistema)
URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' ~/.cloudflared/*.log 2>/dev/null | head -1)

if [ -z "$URL" ]; then
    # Intentar obtener de otro log posible
    URL=$(ps aux | grep cloudflared | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' | head -1)
fi

echo "==================================="
echo "  🌐 TU URL PÚBLICA:"
echo ""
echo "  $URL"
echo ""
echo "==================================="
echo "  📋 Comparte esta URL para"
echo "     acceder desde cualquier"
echo "     dispositivo"
echo "==================================="
echo ""
echo "Presiona Ctrl+C para detener el túnel"
echo ""

# Mantener el script corriendo
wait $TUNNEL_PID
