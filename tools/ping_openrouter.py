import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("OPENROUTER_API_KEY")

if not key:
    raise RuntimeError("Нет OPENROUTER_API_KEY в .env")

url = "https://openrouter.ai/api/v1/models"
headers = {"Authorization": f"Bearer {key}"}

r = requests.get(url, headers=headers, timeout=30)
print("STATUS:", r.status_code)
print("BODY:", r.text[:500])
