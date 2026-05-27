#!/bin/bash
# ============================================================================
# start.sh - Script de inicio para Drive Ordenado
# ============================================================================
# Este script:
#   1. Instala las dependencias de Python
#   2. Descarga cloudflared si no existe
#   3. Inicia el servidor Flask en background
#   4. Crea un túnel con trycloudflare para acceso público
# ============================================================================

set -e

echo "=========================================="
echo "   Drive Ordenado - Iniciando Servidor"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# 1. INSTALAR DEPENDENCIAS
# ============================================================================
echo -e "${BLUE}[1/4] Instalando dependencias de Python...${NC}"

pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencias instaladas correctamente${NC}"
else
    echo -e "${RED}✗ Error al instalar dependencias${NC}"
    exit 1
fi

echo ""

# ============================================================================
# 2. DESCARGAR CLOUDFLARED
# ============================================================================
echo -e "${BLUE}[2/4] Verificando cloudflared...${NC}"

CLOUDFLARED_BIN="./cloudflared-linux-amd64"

if [ ! -f "$CLOUDFLARED_BIN" ]; then
    echo "Descargando cloudflared..."
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Cloudflared descargado${NC}"
    else
        echo -e "${RED}✗ Error al descargar cloudflared${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Cloudflared ya existe${NC}"
fi

# Dar permisos de ejecución
chmod +x "$CLOUDFLARED_BIN"

echo ""

# ============================================================================
# 3. INICIAR FLASK
# ============================================================================
echo -e "${BLUE}[3/4] Iniciando servidor Flask...${NC}"

# Matar procesos previos si existen
pkill -f "python.*app.py" 2>/dev/null || true

# Iniciar Flask en background
export FLASK_APP=app.py
export FLASK_ENV=development
python app.py &

FLASK_PID=$!

# Esperar a que Flask inicie
echo "Esperando que Flask esté listo..."
sleep 3

# Verificar que Flask está corriendo
if curl -s http://localhost:5000 > /dev/null; then
    echo -e "${GREEN}✓ Flask iniciado en http://localhost:5000${NC}"
else
    echo -e "${YELLOW}⚠ Esperando un poco más...${NC}"
    sleep 3
    if curl -s http://localhost:5000 > /dev/null; then
        echo -e "${GREEN}✓ Flask iniciado correctamente${NC}"
    else
        echo -e "${RED}✗ No se pudo iniciar Flask${NC}"
        exit 1
    fi
fi

echo ""

# ============================================================================
# 4. CREAR TÚNEL CON CLOUDFLARE
# ============================================================================
echo -e "${BLUE}[4/4] Creando túnel público con trycloudflare...${NC}"
echo ""
echo -e "${YELLOW}Este proceso puede tardar unos segundos...${NC}"
echo ""

# Crear túnel y capturar la URL
echo -e "${GREEN}========================================${NC}"
echo ""

# Ejecutar cloudflared y extraer la URL
$CLOUDFLARED_BIN tunnel --url http://localhost:5000 2>&1 &

CLOUDFLARED_PID=$!

# Esperar a que se genere la URL
echo "Generando URL pública..."
sleep 8

# Extraer URL del log de cloudflared (esto es un workaround)
# En la práctica, el usuario verá la URL en el output

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Servidor iniciado correctamente!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}URLs de acceso:${NC}"
echo -e "  • Local:    ${BLUE}http://localhost:5000${NC}"
echo ""
echo -e "  • Pública:  ${BLUE}Ver URL arriba (trycloudflare.com)${NC}"
echo ""
echo "=========================================="
echo "Para detener el servidor, presiona Ctrl+C"
echo "=========================================="
echo ""

# Mantener el script corriendo
wait $FLASK_PID
