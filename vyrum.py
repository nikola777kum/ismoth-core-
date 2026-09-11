import sys, os, subprocess, time, json, sqlite3, random

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
            subprocess.run(["git", "commit", "-m", "auto-sync: interactive mode"], check=True, timeout=10)
            subprocess.run(["git", "push", "origin", "main", "--force"], check=True, timeout=15)
            print("☁️ [Git Sync uspešno ažuriran!]")
        else:
            print("☁️ [Git Sync: Nema novih promena na fajlu]")
    except Exception as e:
        print(f"[Git Sync preskočen]: {e}")

# Baza opcija za generisanje na osnovu tvog unosa
def generate_output(user_input):
    clean_input = user_input.strip()
    wordplay = f"Igra reči na temu '{clean_input}': Kad {clean_input} postane sistem, stara pravila pale alarm."
    overlay = f"{clean_input.upper()} // Nema nazad."
    caption = f"Sistem je postavljen. Fokus je jasan. ⚡ {config['brand_tag']}"
    
    return (
        f"1. 🎭 [WORDPLAY]: {wordplay}\n"
        f"2. 🎬 [REEL TEXT OVERLAY]: {overlay}\n"
        f"3. 📝 [CAPTION]: {caption}"
    )

if __name__ == "__main__":
    init_db()
    print("=== VYRUM v22.0 [INTERAKTIVNI MOD ZA @mala.nece.disco] ===")
    print("Kucaj temu ili reč, a za izlaz stisni Enter na prazno ili kucaj 'exit'.\n")

    while True:
        try:
            user_input = input("💬 [Tebe čujem] > ").strip()
            if not user_input or user_input.lower() in ["exit", "kraj", "quit"]:
                print("\n[!] Gasimo interaktivnu konzolu. Vidimo se!")
                break
                
            from datetime import datetime
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
