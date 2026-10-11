#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "📥 Descargando datos del servidor remoto (oracle) al Mac..."
rsync -avz oracle:/home/ubuntu/airbus_esop/data/ "$DIR/data/"
echo "✅ ¡Datos sincronizados con éxito en este Mac!"
read -p "Presiona Enter para cerrar..."
