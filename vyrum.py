import sys, os, subprocess, time, json, sqlite3, random
from datetime import datetime

CONFIG_PATH = "vyrum_config.json"
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
else:
    config = {
        "check_interval_seconds": 30,
        "brand_tag": "@mala.nece.disco",
        "github_token": ""
    }

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
    except Exception:
        pass

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
        subprocess.run(["git", "add", "vyrum.py"], check=True, timeout=10)
        status = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if status.returncode != 0:
            subprocess.run(["git", "commit", "-m", "auto-sync: local wordplay engine active"], check=True, timeout=10)
            subprocess.run(["git", "push", "origin", "main", "--force"], check=True, timeout=15)
            print("☁️ [Git Sync uspešno ažuriran!]", flush=True)
        else:
            print("☁️ [Git Sync: Nema novih promena na fajlu]", flush=True)
    except Exception as e:
        print(f"[Git Sync preskočen]: {e}", flush=True)

# Brutalna lokalna baza wordplay-a i reels ideja za @mala.nece.disco
wordplay_pool = [
    {
        "prompt": "Tema: Daemon u Termuxu vs Demon u glavi u 3 ujutru",
        "wordplay": "Dok daemon vrti proces u Termuxu, demon u glavi vrti isti film u krug. Background process koji nikad ne ide u sleep mode.",
        "overlay": "3:00 AM. Daemon u kodu, demon u glavi. Koji proces prvi pada?",
        "caption": "Kad nemaš san nego imaš sistem. 🌙💻 @mala.nece.disco"
    },
    {
        "prompt": "Tema: Grad spava, imperija se gradi",
        "wordplay": "Dok grad gasi svetla, mi palimo procesore. Night shift mentalitet: nije nesanica, nego noćna smena za budućnost.",
        "overlay": "Grad spava. Mi kompajliramo.",
        "caption": "Tišina najglasnije zvuči u 3 ujutru. 🏗️✨ @mala.nece.disco"
    },
    {
        "prompt": "Tema: Noćni život, disko i psihologija",
        "wordplay": "Svetla u klubu se gase, ali unutrašnji puls tek diže frekvenciju. Psihologija ritma: bass udara tačno tamo gde misli prestaju.",
        "overlay": "Muzika staje, ali sistem nastavlja da radi.",
        "caption": "Nije to samo disko, to je frekvencija preživljavanja. 🪩🔥 @mala.nece.disco"
    },
    {
        "prompt": "Tema: Autonomni sistem i kontrola",
        "wordplay": "Kad napraviš sistem da radi umesto tebe, shvatiš da najveća sloboda dolazi kad kod preuzme kontrolu nad haosom.",
        "overlay": "Automatski režim: ON. Nema stajanja.",
        "caption": "Pustio sam mašinu da misli dok ja gledam kako brojevi rastu. ⚡🤖 @mala.nece.disco"
    }
]

if __name__ == "__main__":
    init_db()
    print(f"=== VYRUM v21.0 [ULTIMATE LOCAL WORDPLAY ENGINE ACTIVE] ===")
    interval = config.get("check_interval_seconds", 30)

    while True:
        try:
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            
            item = random.choice(wordplay_pool)
            
            output = (
                f"1. 🎭 [WORDPLAY]: {item['wordplay']}\n"
                f"2. 🎬 [REEL TEXT OVERLAY]: {item['overlay']}\n"
                f"3. 📝 [CAPTION]: {item['caption']}"
            )
            
            print(f"\n==================== [{time_str}] VYRUM CREATIVE OUTPUT ====================", flush=True)
            print(output, flush=True)
            print("===============================================================================\n", flush=True)
            
            save_memory(time_str, item['prompt'], output)
            cloud_sync()
            
            print(f"💤 [Spavam {interval} sekundi do sledeće ideje...]\n", flush=True)
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("\n[!] Ručno zaustavljen daemon.")
            break
        except Exception as e:
            print(f"[!] Greška u petlji: {e}", flush=True)
            time.sleep(10)
