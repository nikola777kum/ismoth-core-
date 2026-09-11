import sys, os, subprocess, time, json, sqlite3
from datetime import datetime
import requests

CONFIG_PATH = "vyrum_config.json"
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
else:
    config = {"brand_tag": "@mala.nece.disco", "api_key": "", "github_token": ""}

API_KEY = config.get("api_key", "")
DB_PATH = "vyrum_memory.db"
TOKEN = config.get("github_token", "")
GIT_REMOTE_URL = f"https://{TOKEN}@github.com/nikola777kum/ismoth-core-.git"

# Pamćenje istorije razgovora da model "uči" i prati kontekst u toku sesije
chat_history = []

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, prompt TEXT, response TEXT)')
        conn.commit(); conn.close()
    except Exception: pass

def save_memory(timestamp, prompt, response):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO memory (timestamp, prompt, response) VALUES (?, ?, ?)", (timestamp, prompt, response))
        conn.commit(); conn.close()
    except Exception: pass

def cloud_sync():
    try:
        subprocess.run(["git", "remote", "set-url", "origin", GIT_REMOTE_URL], check=True, timeout=5)
        subprocess.run(["git", "add", "vyrum.py"], check=True, timeout=10)
        status = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if status.returncode != 0:
            subprocess.run(["git", "commit", "-m", "auto-sync: AI chat partner active"], check=True, timeout=10)
            subprocess.run(["git", "push", "origin", "main", "--force"], check=True, timeout=15)
    except Exception: pass

def ask_gemini_chat(user_input):
    global chat_history
    # Koristimo stabilnu v1beta rutu sa modelom koji podržava generisanje
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    system_instruction = (
        f"Ti si inteligentni AI partner i ulični saputnik za brend {config['brand_tag']}. "
        "Govoriš opušteno, u našem fazonu, kombinuješ srpski i ulični žargon, pružaš vrhunske ideje za social media, "
        "reels, wordplay i strategiju, i učiš iz razgovora sa korisnikom. Budi direktan, oštar i koristan."
    )
    
    # Dodajemo novu poruku u istoriju
    chat_history.append({"role": "user", "parts": [{"text": user_input}]})
    
    payload = {
        "contents": chat_history,
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    
    try:
        res = requests.post(url, json=payload, timeout=20)
        if res.status_code == 200:
            data = res.json()
            reply = data["candidates"][0]["content"]["parts"][0]["text"]
            # Zabeleži i odgovor modela u istoriju radi konteksta (učenja)
            chat_history.append({"role": "model", "parts": [{"text": reply}]})
            return reply
        else:
            return f"[Greška API-ja: {res.status_code} - Proveri API ključ u fajlu]"
    except Exception as e:
        return f"[Mrežna greška: {e}]"

if __name__ == "__main__":
    init_db()
    print("=== VYRUM v24.0 [ŽIVI AI PARTNER & LEARNING ENGINE] ===\n")
    print("Baci poruku, pričamo normalno. Kucaj 'exit' za izlaz.\n")

    while True:
        try:
            user_input = input("💬 > ").strip()
            if not user_input or user_input.lower() in ["exit", "kraj", "quit"]:
                print("\n[!] Gasim sesiju. Vidimo se!")
                break
                
            time_str = datetime.now().strftime("%I:%M %p")
            
            # Pozivamo pravog AI partnera
            response_text = ask_gemini_chat(user_input)
            
            print(f"\n{response_text}\n")
            
            save_memory(time_str, user_input, response_text)
            cloud_sync()
            
        except KeyboardInterrupt:
            print("\n[!] Prekinuto.")
            break
        except Exception as e:
            print(f"[!] Greška: {e}")
