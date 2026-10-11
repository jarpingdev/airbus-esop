import re
from bs4 import BeautifulSoup
from pathlib import Path

BASE_DIR = Path("/Users/joseantonio/Developer/airbus_esop")
INDEX_PATH = BASE_DIR / "index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# Let's inspect panel-guia and panel-ventas in index.html
soup = BeautifulSoup(html, "html.parser")
panel_ventas = soup.find(id="panel-ventas")
panel_guia = soup.find(id="panel-guia")
panel_simulador = soup.find(id="panel-simulador")
panel_optimizador = soup.find(id="panel-optimizador")

print("Found panel_ventas:", bool(panel_ventas))
print("Found panel_guia:", bool(panel_guia))
print("Parent of panel_ventas:", panel_ventas.parent.name, panel_ventas.parent.get("id"))
