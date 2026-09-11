import sys, os, subprocess, time, json, sqlite3, random
from datetime import datetime

CONFIG_PATH = "vyrum_config.json"
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
else:
    config = {
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
            subprocess.run(["git", "commit", "-m", "auto-sync: clean interactive fix"], check=True, timeout=10)
            subprocess.run(["git", "push", "origin", "main", "--force"], check=True, timeout=15)
            print("☁️ [Git Sync uspešno ažuriran!]")
        else:
            print("☁️ [Git Sync: Nema novih promena na fajlu]")
    except Exception as e:
        print(f"[Git Sync preskočen]: {e}")

def generate_output(user_input):
    inp = user_input.strip()
    up = inp.upper()
    
    styles = [
        {
            "wordplay": f"Kad {inp} uđe u sistem, frekvencija se menja. Nije ovo običan ritam, ovo je takt koji preživljava noć.",
            "overlay": f"{up} // Udar u centar.",
            "caption": f"Sve je rečeno u jednoj reči. ⚡ {config['brand_tag']}"
        },
        {
            "wordplay": f"Tražiš {inp}? Dok oni spavaju, mi kompajliramo značenje iza svakog koraka na betonu.",
            "overlay": f"BEZ GREŠKE: {up}",
            "caption": f"Ulična psihologija i noćni program. 🪩🔥 {config['brand_tag']}"
        },
        {
            "wordplay": f"Igra reči: {inp} nije opcija, {inp} je protokol koji se izvršava bez prava na žalbu.",
            "overlay": f"STATUS: {up} ACTIVE",
            "caption": f"Sistem drži konce u svojim rukama. 🌙💻 {config['brand_tag']}"
        }
    ]
    
    item = random.choice(styles)
    
    return (
        f"1. 🎭 [WORDPLAY]: {item['wordplay']}\n"
        f"2. 🎬 [REEL TEXT OVERLAY]: {item['overlay']}\n"
        f"3. 📝 [CAPTION]: {item['caption']}"
    )

if __name__ == "__main__":
    init_db()
    print("=== VYRUM v22.2 [CLEAN INTERACTIVE ENGINE] ===")
    print("Kucaj temu, reč ili misao, a za izlaz stisni Enter na prazno ili kucaj 'exit'.\n")

    while True:
        try:
            user_input = input("💬 [Tebe čujem] > ").strip()
            if not user_input or user_input.lower() in ["exit", "kraj", "quit"]:
                print("\n[!] Gasimo interaktivnu konzolu. Vidimo se!")
                break
                
            time_str = datetime.now().strftime("%I:%M %p")
            output = generate_output(user_input)
            
            print(f"\n==================== [{time_str}] VYRUM CREATIVE OUTPUT ====================", flush=True)
            print(output, flush=True)
            print("===============================================================================\n", flush=True)
            
            save_memory(time_str, user_input, output)
            cloud_sync()
            print()
            
        except KeyboardInterrupt:
            print("\n[!] Prekinuto ručno.")
            break
        except Exception as e:
            print(f"[!] Greška: {e}")
