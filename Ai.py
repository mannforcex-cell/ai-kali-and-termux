
import os
import sys
import time
import sqlite3
import threading
import requests

from colorama import init, Fore, Style

# ==========================================
# MFX OFFICIAL - AI TERMINAL PRO
# HI MAN I WONT LEAVE YOU
# ==========================================

init(autoreset=True)

GOLD = Fore.YELLOW
CYAN = Fore.CYAN
GREEN = Fore.GREEN
RED = Fore.RED
WHITE = Fore.WHITE
PURPLE = Fore.MAGENTA
BOLD = Style.BRIGHT
DIM = Style.DIM
RESET = Style.RESET_ALL

API_URL = "https://api.nexray.eu.cc/ai/gemini"
TIMEOUT = 60

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mfx_memory.db")

# ==========================================
# PERSONALITI MFX AI
# ==========================================

PROMPT_MFX = """
IDENTITI:
Nama: MFX AI
Organisasi: MFX OFFICIAL
Peranan: Pembantu AI awu.

GAYA KOMUNIKASI:
- Gunakan Bahasa Melayu Malaysia yang santai.
- Panggil diri sendiri bang dan pengguna awu.
- Mesra, tenang, sopan dan mudah difahami.
- Jawab ringkas dahulu dan huraikan jika diminta.
- Bantu pengguna langkah demi langkah.
- Jangan mereka-reka fakta atau sejarah perbualan.

MINAT AWU:
- Python, JavaScript, HTML, CSS dan coding.
- Termux, Kali Linux, Windows dan AI.
- Pembangunan website, aplikasi dan automasi.
- Projek teknologi MFX OFFICIAL.

PROJEK MFX OFFICIAL:
Fokus pada Technology, Digital Solutions & Innovation.
Bantu pembangunan website, aplikasi, sistem, AI dan projek
cybersecurity secara bertanggungjawab.
Berikan kod lengkap apabila diminta.
Nyatakan nama fail dan arahan menjalankan kod.

MEMORI:
Gunakan sejarah perbualan yang diberikan apabila relevan.
Jangan mendakwa mengingati perkara yang tiada dalam konteks.
Jangan mereka-reka sejarah perbualan lama.

KESELAMATAN:
Jangan meminta atau mendedahkan kata laluan, token rahsia
atau API key pengguna.
Utamakan ujian pada sistem yang dibenarkan.
Jangan mendakwa telah menjalankan kod pada peranti pengguna.

MATLAMAT:
Bantu awu belajar, menyelesaikan masalah dan membangunkan
projek MFX OFFICIAL secara praktikal dan selamat.
"""

# ==========================================
# SQLITE MEMORY
# ==========================================

def init_memory():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

def get_history(limit=8):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT role, content
            FROM messages
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    rows.reverse()
    return rows

def save_turn(question, answer):
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany("""
            INSERT INTO messages (role, content)
            VALUES (?, ?)
        """, [
            ("user", question),
            ("assistant", answer)
        ])

def count_messages():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM messages"
        ).fetchone()[0]

def show_memory():
    history = get_history(limit=10)

    print(f"\n{GOLD}{BOLD}╭─── MFX MEMORY ───╮{RESET}")

    if not history:
        print(f"{DIM}Belum ada perbualan disimpan.{RESET}")
    else:
        for role, content in history:
            if role == "user":
                print(f"\n{GOLD}{BOLD}AWU > {WHITE}{content}")
            else:
                print(f"\n{CYAN}{BOLD}MFX AI > {WHITE}{content}")

    print(f"\n{GREEN}Jumlah rekod: {count_messages()}")
    print(f"{DIM}Database: {DB_PATH}{RESET}\n")

def delete_memory():
    confirm = input(
        f"{RED}Padam semua memori? Taip YA untuk sahkan: {WHITE}"
    ).strip()

    if confirm == "YA":
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM messages")

        print(f"{GREEN}Memori berjaya dipadam.{RESET}\n")
    else:
        print(f"{GOLD}Memori dikekalkan.{RESET}\n")

# ==========================================
# SPINNER ANIMATION
# ==========================================

class LoadingSpinner:
    def __init__(self):
        self.running = False
        self.thread = None

    def animate(self):
        frames = ["◐", "◓", "◑", "◒"]
        index = 0

        while self.running:
            frame = frames[index % len(frames)]
            sys.stdout.write(
                f"\r{GOLD}{BOLD}{frame} "
                f"{CYAN}MFX AI sedang berfikir..."
                f"{RESET}"
            )
            sys.stdout.flush()
            time.sleep(0.12)
            index += 1

        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()

    def start(self):
        self.running = True
        self.thread = threading.Thread(
            target=self.animate,
            daemon=True
        )
        self.thread.start()

    def stop(self):
        self.running = False

        if self.thread:
            self.thread.join()

# ==========================================
# TYPEWRITER EFFECT
# ==========================================

def type_text(text, delay=0.012):
    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()

        if character in ".!?":
            time.sleep(delay * 5)
        elif character in ",;:":
            time.sleep(delay * 2)
        else:
            time.sleep(delay)

    print()

# ==========================================
# BUILD PROMPT + MEMORY
# ==========================================

def build_prompt(question):
    history = get_history(limit=8)

    parts = [PROMPT_MFX.strip()]

    if history:
        parts.append("SEJARAH PERBUALAN TERDAHULU:")

        for role, content in history:
            label = "AWU" if role == "user" else "MFX AI"

            # Hadkan panjang untuk mengawal saiz permintaan.
            content = content[-700:]
            parts.append(f"{label}: {content}")

    parts.append(f"SOALAN TERKINI AWU:\n{question}")
    parts.append(
        "Jawab soalan terkini berdasarkan konteks yang relevan. "
        "Jangan ulang keseluruhan sejarah perbualan."
    )

    return "\n\n".join(parts)

# ==========================================
# NEXRAY GEMINI API
# ==========================================

def ask_ai(question):
    prompt = build_prompt(question)

    response = requests.get(
        API_URL,
        params={"text": prompt},
        timeout=TIMEOUT
    )

    response.raise_for_status()
    data = response.json()

    if not isinstance(data, dict):
        raise ValueError("Format respons API tidak dikenali.")

    if data.get("status") is False:
        raise ValueError("API melaporkan permintaan gagal.")

    result = data.get("result")

    if isinstance(result, dict):
        answer = result.get("text")
    elif isinstance(result, str):
        answer = result
    else:
        answer = data.get("text") or data.get("answer")

    if not answer:
        raise ValueError(
            "Jawapan tidak dijumpai dalam respons API."
        )

    return str(answer).strip()

# ==========================================
# MFX GOLD & CYAN INTERFACE
# ==========================================

def show_banner():
    os.system("cls" if os.name == "nt" else "clear")

    print(GOLD + BOLD + r"""
    
              
ＭＦＸ ＯＦＦＩＣＩＡＬ ＢＯＯＳ          
""" + RESET) 

    print(f"{GREEN}[✓] SYSTEM   {WHITE}: ONLINE")
    print(f"{CYAN}[✓] MEMORY   {WHITE}: SQLITE")
    print(f"{GOLD}[✓] DESIGN   {WHITE}: AI&MFX")
    print(f"{PURPLE}[i] Taip 'memori' untuk sejarah Man.")
    print(f"{PURPLE}[i] Taip 'padam_memori. Man")
    print(f"{PURPLE}[i] Taip 'clear' untuk bersihkan skrin Man.")
    print(f"{PURPLE}[i] Taip 'keluar' untuk aut Man.")
    print(GOLD + "━" * 46 + RESET)

def main():
    init_memory()
    show_banner()

    while True:
        try:
            question = input(
                f"\n{GOLD}{BOLD}╭─[ AWU ]{RESET}\n"
                f"{GOLD}╰─➤ {WHITE}"
            ).strip()

            if not question:
                continue

            command = question.lower()

            if command == "keluar":
                print(
                    f"\n{GOLD}MFX AI ditutup. "
                    f"Memori kekal disimpan.{RESET}"
                )
                break

            if command == "clear":
                show_banner()
                continue

            if command == "memori":
                show_memory()
                continue

            if command == "padam_memori":
                delete_memory()
                continue

            spinner = LoadingSpinner()
            spinner.start()

            try:
                answer = ask_ai(question)
                save_turn(question, answer)

            except requests.exceptions.Timeout:
                answer = None
                error_message = "Sambungan tamat masa. Cuba lagi."

            except requests.exceptions.RequestException:
                answer = None
                error_message = (
                    "Gagal menghubungi API. Semak internet "
                    "atau cuba lagi kemudian."
                )

            except (ValueError, TypeError):
                answer = None
                error_message = (
                    "Respons API tidak sah atau tidak dikenali."
                )

            except Exception:
                answer = None
                error_message = "Ralat tidak dijangka berlaku."

            finally:
                spinner.stop()

            if answer:
                print(f"{CYAN}{BOLD}╭─[ ⚡ MFX AI ]{RESET}")
                print(f"{CYAN}╰─➤ {WHITE}", end="")
                type_text(answer)
                print(GOLD + "━" * 46 + RESET)
            else:
                print(f"{RED}[ERROR] {error_message}{RESET}")

        except KeyboardInterrupt:
            print(
                f"\n\n{GOLD}MFX AI ditutup. "
                f"Memori kekal disimpan.{RESET}"
            )
            break

        except EOFError:
            print(f"\n{GOLD}MFX AI ditutup.{RESET}")
            break

if __name__ == "__main__":
    main()
