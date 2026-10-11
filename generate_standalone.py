import re
from pathlib import Path

BASE_DIR = Path("/Users/joseantonio/Developer/airbus_esop")
INDEX_PATH = BASE_DIR / "index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    index_content = f.read()

# We take the HTML structure from index.html up to the final <script> tag
split_marker = "  <!-- SCRIPT LÓGICA FRONTEND -->"
if split_marker not in index_content:
    split_marker = "<script>"
    # find last <script>
    idx = index_content.rfind("<script>")
    html_part = index_content[:idx]
else:
    idx = index_content.find(split_marker)
    html_part = index_content[:idx]

# Let's inspect what html_part has
print("HTML part length:", len(html_part))
