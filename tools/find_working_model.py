import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("OPENROUTER_API_KEY")
if not key:
    raise RuntimeError("Нет OPENROUTER_API_KEY в .env")

headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "folder-summarizer",
}

models_url = "https://openrouter.ai/api/v1/models"
chat_url = "https://openrouter.ai/api/v1/chat/completions"

models = requests.get(models_url, headers={"Authorization": f"Bearer {key}"}, timeout=30).json()["data"]
free_models = [m["id"] for m in models if ":free" in m["id"]]

print("Всего free:", len(free_models))

test_payload_base = {
    "messages": [
        {"role": "system", "content": "Отвечай одним словом."},
        {"role": "user", "content": "готов?"},
    ],
    "max_tokens": 10,
    "temperature": 0.2,
}

for mid in free_models[:20]:  # пробуем первые 20
    payload = dict(test_payload_base)
    payload["model"] = mid

    try:
        r = requests.post(chat_url, headers=headers, json=payload, timeout=60)
        data = r.json()
        if "error" in data:
            print("NO:", mid, "|", data["error"].get("message", "err"))
        else:
            text = data["choices"][0]["message"]["content"].strip()
            print("\n✅ WORKS:", mid, "->", text)
            break
    except Exception as e:
        print("ERR:", mid, "|", e)

    time.sleep(0.5)
