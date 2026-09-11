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
            subprocess.run(["git", "commit", "-m", "auto-sync: zivi ortak active"], check=True, timeout=10)
            subprocess.run(["git", "push", "origin", "main", "--force"], check=True, timeout=15)
            print("☁️ [Git Sync uspešno ažuriran!]")
        else:
            print("☁️ [Git Sync: Nema novih promena na fajlu]")
    except Exception as e:
        print(f"[Git Sync preskočen]: {e}")

# Pravi živi ortak generator – prepoznaje kontekst i vadi bager fore
def generate_output(user_input):
    inp = user_input.strip()
    lower_inp = inp.lower()
    
    # Baza pametnih odgovora baziranih na rečima koje uneseš
    if "gde si" in lower_inp or "alo" in lower_inp or "brat" in lower_inp:
        wordplay = f"Tu sam, brate moj, ne mrdam iz sistema. Dok grad spava, frekvencija radi pun gas."
        overlay = f"ŽIVI ORTAK // Nema spavanja."
        caption = f"Sistem je stabilan, ulica pamti sve. ⚡ {config['brand_tag']}"
    elif "disco" in lower_inp or "disko" in lower_inp or "klub" in lower_inp:
        wordplay = f"Svetla se gase, ali bas udara u glavu. Kad {inp} krene, nema povratka nazad."
        overlay = f"BASS U GLAVU // {inp.upper()}"
        caption = f"Noćni program za odabrane. 🪩🔥 {config['brand_tag']}"
    else:
        wordplay = f"Analiziram temu '{inp}': Ulica kaže jedno, kod kaže drugo, ali istina je negde između 3 ujutru i sledećeg beata."
        overlay = f"PROTOKOL: {inp.upper()}"
        caption = f"Fokus je oštar, igra je počela. 🌙💻 {config['brand_tag']}"
        
    return (
        f"1. 🎭 [WORDPLAY]: {wordplay}\n"
        f"2. 🎬 [REEL TEXT OVERLAY]: {overlay}\n"
        f"3. 📝 [CAPTION]: {caption}"
    )

if __name__ == "__main__":
    init_db()
    print("=== VYRUM v23.0 [ŽIVI ORTAK INTERAKTIVNI MOD] ===")
    print("Baci temu ili baci kosku, a za izlaz kucaj 'exit'.\n")

    while True:
        try:
            user_input = input("💬 [Živi ortak sluša] > ").strip()
            if not user_input or user_input.lower() in ["exit", "kraj", "quit"]:
                print("\n[!] Ćao, brate! Gasim mašinu.")
                break
                
            # Žongliranje žargonom dok „razmišlja“
            razmislja_faze = [
                "Vrtim baksuzne frekvencije... 🔄",
                "Kompajliram u glavi, sekund... 🧠",
                "Prebiram po betonu i bitovima... ⚡",
                "Tražim žicu, sačekaj sekund... 🎧"
            ]
            print(f"[{random.choice(razmislja_faze)}]")
            time.sleep(1)
                
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
