#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "📤 Sincronizando aplicación y datos locales hacia el servidor remoto (oracle)..."
rsync -avz "$DIR/templates/" oracle:/home/ubuntu/airbus_esop/templates/
rsync -avz "$DIR/app.py" "$DIR/airbus_esop.py" "$DIR/Airbus_ESOP_Standalone.html" "$DIR/airbus_esop.html" oracle:/home/ubuntu/airbus_esop/
rsync -avz "$DIR/data/" oracle:/home/ubuntu/airbus_esop/data/
ssh oracle "sudo systemctl restart airbus-esop || systemctl --user restart airbus-esop || true"
echo "✅ ¡Aplicación y datos sincronizados con éxito en el servidor!"
read -p "Presiona Enter para cerrar..."
