#!/bin/bash
# Acceso directo para iniciar la versión web de Airbus ESOP
cd "$(dirname "$0")"
echo "Iniciando panel web de Airbus ESOP..."
.venv/bin/python app.py
