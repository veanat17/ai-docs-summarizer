import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise RuntimeError("Нет OPENROUTER_API_KEY в .env")

url = "https://openrouter.ai/api/v1/models"
headers = {"Authorization": f"Bearer {API_KEY}"}

r = requests.get(url, headers=headers, timeout=30)
r.raise_for_status()
data = r.json()

models = data.get("data", [])
free_models = []

for m in models:
    mid = m.get("id", "")
    if ":free" in mid:
        free_models.append(mid)

print("Найдено free-моделей:", len(free_models))
print("\n".join(free_models[:50]))
