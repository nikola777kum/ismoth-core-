import sys, os, subprocess, requests, time, json, sqlite3
from datetime import datetime

CONFIG_PATH = "vyrum_config.json"
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
else:
    config = {
        "primary_model": "gemini-pro",
        "check_interval_seconds": 30,
        "brand_tag": "@mala.nece.disco",
        "api_key": "",
        "github_token": ""
    }

API_KEY = config.get("api_key", "")
DB_PATH = "vyrum_memory.db"
TOKEN = config.get("github_token", "")
GIT_REMOTE_URL = f"https://{TOKEN}@github.com/nikola777kum/ismoth-core-.git"

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                prompt TEXT,
                response TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB Error]: {e}", flush=True)

def save_memory(timestamp, prompt, response):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO memory (timestamp, prompt, response) VALUES (?, ?, ?)", (timestamp, prompt, response))
        conn.commit()
        conn.close()
    except Exception:
        pass

def cloud_sync():
    try:
        subprocess.run(["git", "remote", "set-url", "origin", GIT_REMOTE_URL], check=True, timeout=5)
        subprocess.run(["git", "add", "vyrum.py", ".gitignore"], check=True, timeout=10)
        subprocess.run(["git", "commit", "-m", "auto-sync: vyrum v20.0 wordplay engine active"], check=True, timeout=10)
        subprocess.run(["git", "push", "origin", "main", "--force"], check=True, timeout=15)
        print("☁️ [Git Sync uspešno završen!]", flush=True)
    except Exception as e:
        print(f"[Git Sync preskočen/greška]: {e}", flush=True)

def ask_gemini(prompt, time_str):
    url = f"https://generativelanguage.googleapis.com/v1/models/{config['primary_model']}:generateContent?key={API_KEY}"
    
    sys_ins = (
        f"Ti si Vyrum v20.0 — nefiltrirani AI Copywriter, Wordplay Genije i Meme Arhitekta za brend {config['brand_tag']}. "
        "Tvok cilj je stvaranje genijalnih igara rečima (wordplays), dvostrukih značenja, dark-humor fora i ulične psihologije. "
        "Kombinuješ srpski, engleski i ulični balkan-sleng (Serblish). "
        "Svaki tvoj odgovor mora sadržati:\n"
        "1. 🎭 [WORDPLAY / REČ NIVA]: Genijalna igra rečima ili dvostruka poenta (SRB/ENG mix).\n"
        "2. 🎬 [REEL TEXT OVERLAY]: 1-2 brutalne rečenice koje idu preko videa za Reel.\n"
        "3. 📝 [CAPTION & HOOK]: Izazovan i duhovit opis za post koji tera ljude da komentarišu."
    )
    
    payload = {"contents": [{"parts": [{"text": f"System: {sys_ins}\n\nVreme: {time_str}\n\nZahtev: {prompt}"}]}]}
    
    print(f"⚡ [Vyrum Wordplay Engine stvara za {config['brand_tag']}...]", flush=True)
    try:
        res = requests.post(url, json=payload, timeout=15)
        if res.status_code == 200:
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print(f"⚠️ [API Status {res.status_code}], prebacujem na fallback...", flush=True)
            print(res.text, flush=True)
    except Exception as e:
        print(f"⚠️ [Mrežna greška/Timeout]: {e}", flush=True)
        
    return f"[ONLINE FALLBACK: Sistem stabilizovan u {time_str}]"

if __name__ == "__main__":
    init_db()
    print(f"=== VYRUM v20.0 [WORDPLAY & WRITER EXPERT ACTIVE] ===")
    interval = config.get("check_interval_seconds", 30)
    
    prompts_pool = [
        "Smišljaj wordplay na temu daemona na telefonu vs demona u glavi u 3 ujutru.",
        "Daj banger wordplay za likove koji ne spavaju nego planiraju imperiju dok grad spava.",
        "Napravi brutalnu igru rečima na englesko-srpskom oko noćnog života, diska i psihologije.",
        "Smišljaj fora-koncept za reel: 'Kad ti devojka kaže da izabereš ili ona ili tvoji projekti'."
    ]
    
    import random

    while True:
        try:
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            
            prompt_tekst = random.choice(prompts_pool)
            odgovor = ask_gemini(prompt_tekst, time_str)
            
            print(f"\n==================== [{time_str}] VYRUM CREATIVE OUTPUT ====================", flush=True)
            print(odgovor, flush=True)
            print("===============================================================================\n", flush=True)
            
            save_memory(time_str, prompt_tekst, odgovor)
            cloud_sync()
            
            print(f"💤 [Spavam {interval} sekundi do sledeće ideje...]\n", flush=True)
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("\n[!] Ručno zaustavljen daemon.")
            break
        except Exception as e:
            print(f"[!] Kritična greška u petlji: {e}", flush=True)
            time.sleep(10)
