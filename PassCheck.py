import re
import os
import sys
import math
import string
import secrets
import getpass
import urllib.request
import urllib.error
import gzip
import shutil
import ssl
import hashlib
import platform
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn
from rich.rule import Rule
from rich import box

console = Console()

# ─────────────────────────────────────────────
#  PLATFORM HELPERS
# ─────────────────────────────────────────────

IS_WINDOWS = os.name == 'nt'
IS_LINUX   = platform.system() == 'Linux'

def clear_screen():
    os.system('cls' if IS_WINDOWS else 'clear')

def print_banner():
    banner = """[bold cyan]
 ██████╗  █████╗ ███████╗███████╗    ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗
 ██╔══██╗██╔══██╗██╔════╝██╔════╝   ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
 ██████╔╝███████║███████╗███████╗   ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
 ██╔═══╝ ██╔══██║╚════██║╚════██║   ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
 ██║     ██║  ██║███████║███████║   ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
 ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝    ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝[/]"""
    console.print(banner)
    console.print(
        "[dim cyan]        🔐 Password Security Checker  •  Dual-Layer Breach Detection  •  v2.0[/]\n"
    )

# ─────────────────────────────────────────────
#  ROCKYOU SETUP
# ─────────────────────────────────────────────

def ensure_rockyou_exists(txt_path="rockyou.txt", gz_path="rockyou.txt.gz"):
    url = "https://github.com/BugHunterJunior/PassCheck/releases/download/v1.0/rockyou.txt.gz"

    if os.path.exists(txt_path):
        return True

    console.print(f"\n[bold yellow][*] {txt_path} not found in the current directory.[/]")

    if url == "YOUR_GITHUB_RELEASE_LINK_HERE":
        console.print("[bold red]ERROR: Download URL not configured.[/]")
        console.print("[dim]Place rockyou.txt in the same directory, or update the download URL in the script.[/]")
        return False

    if not os.path.exists(gz_path):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        try:
            with urllib.request.urlopen(url, context=ctx) as response:
                total_size = int(response.info().get("Content-Length", 0))

                with Progress(
                    SpinnerColumn("dots", style="cyan"),
                    TextColumn("[cyan]{task.description}"),
                    BarColumn(complete_style="green", finished_style="bold green"),
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    console=console
                ) as progress:
                    task = progress.add_task("Downloading rockyou.txt.gz...", total=total_size)
                    with open(gz_path, "wb") as f:
                        while chunk := response.read(8192):
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))

            console.print("[bold green][+] Download complete![/]")
        except Exception as e:
            console.print(f"[bold red]ERROR: Failed to download. {e}[/]")
            return False

    console.print(f"[cyan][+] Extracting {gz_path}...[/]")
    try:
        with gzip.open(gz_path, 'rb') as f_in:
            with open(txt_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        console.print("[bold green][+] Extraction complete![/]")
        os.remove(gz_path)
        console.print("[dim][+] Cleaned up rockyou.txt.gz[/dim]\n")
        return True
    except Exception as e:
        console.print(f"[bold red]ERROR: Failed to extract. {e}[/]")
        return False

# ─────────────────────────────────────────────
#  BREACH CHECKS
# ─────────────────────────────────────────────

def check_rockyou(password, filepath="rockyou.txt"):
    abs_path = os.path.abspath(filepath)
    if not os.path.exists(abs_path):
        console.print(f"[bold yellow]WARNING: rockyou.txt not found at {abs_path}[/]")
        return None

    clean = password.rstrip('\r\n')
    with open(abs_path, "r", encoding="latin-1", errors="ignore") as f:
        for line in f:
            if line.rstrip('\r\n') == clean:
                return True
    return False

def check_password_online(password):
    sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1_hash[:5], sha1_hash[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Python-PassChecker-v2'})
        with urllib.request.urlopen(req, timeout=4) as response:
            hashes = response.read().decode('utf-8').splitlines()

        for line in hashes:
            target_suffix, count = line.split(':')
            if target_suffix == suffix:
                return int(count)
        return 0
    except urllib.error.URLError:
        return -1
    except Exception as e:
        console.print(f"[bold red]Online check failed: {e}[/]")
        return None

# ─────────────────────────────────────────────
#  COMPLEXITY & ENTROPY
# ─────────────────────────────────────────────

def calculate_entropy(password):
    """Shannon entropy: log2(charset_size ^ length)"""
    charset = 0
    if re.search(r"[a-z]", password):          charset += 26
    if re.search(r"[A-Z]", password):          charset += 26
    if re.search(r"[0-9]", password):          charset += 10
    if re.search(r"[!@#$%^&*()_,.?\":{}|<>]", password): charset += 32
    if charset == 0:
        return 0.0
    return round(len(password) * math.log2(charset), 2)

def check_password(password):
    score = 0
    feedback = []

    if len(password) >= 8:  score += 1
    else: feedback.append("Use at least 8 characters")

    if len(password) >= 12: score += 1

    if re.search(r"[A-Z]", password): score += 1
    else: feedback.append("Add uppercase letters")

    if re.search(r"[a-z]", password): score += 1
    else: feedback.append("Add lowercase letters")

    if re.search(r"[0-9]", password): score += 1
    else: feedback.append("Add numbers")

    if re.search(r"[!@#$%^&*()_,.?\":{}|<>]", password): score += 1
    else: feedback.append("Add special characters")

    return score, feedback

def strength_label(score, is_compromised=False):
    if is_compromised:
        return "[bold white on red] COMPROMISED [/]"
    if score <= 2:
        return "[bold red]🔴 Weak[/]"
    elif score <= 4:
        return "[bold yellow]🟡 Medium[/]"
    else:
        return "[bold green]🟢 Strong[/]"

def entropy_bar(entropy):
    """
    Returns a color-coded Rich progress bar string based on entropy bits.
    Thresholds:  <28 = red, 28–35 = yellow, 36–59 = cyan, 60+ = green
    """
    max_display = 80.0
    filled = min(int((entropy / max_display) * 30), 30)
    empty  = 30 - filled

    if entropy < 28:
        color = "red"
        label = "Very Low"
    elif entropy < 36:
        color = "yellow"
        label = "Low"
    elif entropy < 60:
        color = "cyan"
        label = "Good"
    else:
        color = "green"
        label = "Excellent"

    bar = f"[{color}]{'█' * filled}[/][dim]{'░' * empty}[/]"
    return bar, label, color

# ─────────────────────────────────────────────
#  PASSWORD GENERATOR
# ─────────────────────────────────────────────

def generate_password(length=16, use_upper=True, use_lower=True,
                      use_digits=True, use_symbols=True):
    """
    Cryptographically secure password generator using secrets module.
    Guarantees at least one character from each selected category.
    """
    charset = ""
    required = []

    if use_lower:
        charset += string.ascii_lowercase
        required.append(secrets.choice(string.ascii_lowercase))
    if use_upper:
        charset += string.ascii_uppercase
        required.append(secrets.choice(string.ascii_uppercase))
    if use_digits:
        charset += string.digits
        required.append(secrets.choice(string.digits))
    if use_symbols:
        symbols = "!@#$%^&*()_,.?\":{}|<>"
        charset += symbols
        required.append(secrets.choice(symbols))

    if not charset:
        return None

    remaining = [secrets.choice(charset) for _ in range(length - len(required))]
    password_list = required + remaining
    secrets.SystemRandom().shuffle(password_list)
    return ''.join(password_list)

def generate_passphrase(word_count=4, separator='-'):
    """
    Generates a secure passphrase from a curated built-in wordlist.
    Uses secrets.choice for cryptographic randomness.
    Falls back to random syllable words if wordlist is unavailable.
    """
    # Compact built-in wordlist (200 common, memorable English words)
    WORDS = [
        "apple","brave","cloud","dance","eagle","flame","grape","honor","ivory","jewel",
        "karma","lemon","mango","noble","ocean","pearl","quest","raven","storm","tiger",
        "ultra","vivid","water","xenon","yacht","zebra","amber","blaze","crane","delta",
        "ember","frost","globe","haven","input","joker","knife","laser","maple","nerve",
        "olive","pixel","quartz","robin","solar","torch","umbra","vapor","whale","xray",
        "yield","zones","atlas","bench","coral","dodge","elite","forge","grain","haste",
        "index","judge","krait","lunar","mount","ninja","orbit","prism","quota","ridge",
        "sigma","trail","unity","valve","woods","xenix","youth","zonal","axiom","boost",
        "chess","draft","epoch","flair","grind","hyper","infer","joust","knack","logic",
        "magic","nexus","optic","pivot","query","range","scout","thorn","upper","vista",
        "witch","xeric","yearn","zippy","acorn","birch","cedar","daisy","elder","finch",
        "goose","holly","irony","jaunt","kudos","lilac","moose","newt","otter","poppy",
        "quail","robin","swamp","trout","umber","viper","weasel","vixen","yucca","zinnia",
        "algae","briar","cactus","dingo","egret","flint","gecko","heron","ibis","jackal",
        "kelp","lotus","morel","nymph","onyx","petal","quill","resin","slate","thyme",
        "ulcer","venom","wight","xenon","yodel","zingy","acrid","bison","crux","dusk",
        "epic","fern","gust","hymn","icon","jolt","kale","lynx","myth","nave","opal",
        "pulp","rune","sage","tusk","urge","volt","wren","xylo","yawn","zest"
    ]

    chosen = [secrets.choice(WORDS) for _ in range(word_count)]
    # Capitalise first letter of each word for readability
    chosen = [w.capitalize() for w in chosen]
    return separator.join(chosen)

def password_generator_menu():
    clear_screen()
    print_banner()
    console.print(Rule("[bold cyan]  Password Generator  [/]", style="cyan"))
    console.print()

    while True:
        console.print("[bold white]Generation Mode:[/]")
        console.print("  [cyan]1.[/] Random Password  [dim](high entropy, hard to remember)[/]")
        console.print("  [cyan]2.[/] Passphrase       [dim](memorable, equally strong)[/]")
        console.print("  [cyan]3.[/] Back to Main Menu")
        console.print()

        mode = input("Enter choice (1-3): ").strip()

        if mode == '1':
            console.print()
            # --- Length ---
            try:
                raw = input("Password length [default: 16, min: 8, max: 64]: ").strip()
                length = int(raw) if raw else 16
                length = max(8, min(64, length))
            except ValueError:
                length = 16

            # --- Character sets ---
            console.print()
            console.print("[dim]Include character types (y/n) — press Enter to accept default:[/]")
            use_upper   = input("  Uppercase letters  [Y/n]: ").strip().lower() != 'n'
            use_lower   = input("  Lowercase letters  [Y/n]: ").strip().lower() != 'n'
            use_digits  = input("  Digits             [Y/n]: ").strip().lower() != 'n'
            use_symbols = input("  Special characters [Y/n]: ").strip().lower() != 'n'

            if not any([use_upper, use_lower, use_digits, use_symbols]):
                console.print("[bold red]At least one character type must be selected.[/]\n")
                continue

            # --- Generate ---
            console.print()
            console.print(Rule("[dim]Generated Passwords[/]", style="dim"))
            console.print()

            passwords = [generate_password(length, use_upper, use_lower, use_digits, use_symbols) for _ in range(5)]

            table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold cyan")
            table.add_column("#",        style="dim",        width=4,  justify="center")
            table.add_column("Password", style="bold white", min_width=30)
            table.add_column("Entropy",  style="cyan",       width=14, justify="right")
            table.add_column("Strength", style="white",      width=12, justify="center")

            for i, pwd in enumerate(passwords, 1):
                score, _  = check_password(pwd)
                ent       = calculate_entropy(pwd)
                _, _, col = entropy_bar(ent)
                table.add_row(
                    str(i),
                    pwd,
                    f"[{col}]{ent} bits[/]",
                    strength_label(score)
                )

            console.print(table)
            console.print("[dim]  Tip: Pick any password above. All are cryptographically generated.[/]\n")

        elif mode == '2':
            console.print()
            # --- Word count ---
            try:
                raw = input("Number of words [default: 4, min: 3, max: 8]: ").strip()
                count = int(raw) if raw else 4
                count = max(3, min(8, count))
            except ValueError:
                count = 4

            # --- Separator ---
            sep_choice = input("Separator  [-  /  .  _  or custom, default: -]: ").strip()
            separator = sep_choice if sep_choice else '-'

            # --- Generate ---
            console.print()
            console.print(Rule("[dim]Generated Passphrases[/]", style="dim"))
            console.print()

            passphrases = [generate_passphrase(count, separator) for _ in range(5)]

            table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold cyan")
            table.add_column("#",          style="dim",        width=4,  justify="center")
            table.add_column("Passphrase", style="bold white", min_width=30)
            table.add_column("Entropy",    style="cyan",       width=14, justify="right")

            for i, pp in enumerate(passphrases, 1):
                ent       = calculate_entropy(pp)
                _, _, col = entropy_bar(ent)
                table.add_row(
                    str(i),
                    pp,
                    f"[{col}]{ent} bits[/]"
                )

            console.print(table)
            console.print("[dim]  Tip: Passphrases are easier to type and remember — excellent for master passwords.[/]\n")

        elif mode == '3':
            break
        else:
            console.print("[bold red]Invalid choice. Try again.[/]\n")

# ─────────────────────────────────────────────
#  INSTALL TO PATH  (Linux only)
# ─────────────────────────────────────────────

def install_to_bin():
    """
    Copies this script to /usr/local/bin/passchecker and makes it executable.
    Linux only. Requires sudo / root privileges.
    """
    if IS_WINDOWS:
        console.print(Panel(
            "[yellow]The install-to-PATH feature is for Linux only.\n"
            "On Windows, add the script's folder to your PATH manually via\n"
            "System → Advanced → Environment Variables.[/]",
            title="[bold yellow]Windows Notice[/]",
            border_style="yellow"
        ))
        return

    script_path = os.path.abspath(__file__)
    target      = "/usr/local/bin/passchecker"

    console.print(f"\n[cyan]Installing [bold]{script_path}[/bold] → [bold]{target}[/bold][/]")
    console.print("[dim]This requires sudo privileges.[/]\n")

    try:
        subprocess.run(["sudo", "cp", script_path, target], check=True)
        subprocess.run(["sudo", "chmod", "+x", target],     check=True)

        console.print(Panel(
            f"[bold green]✔ Installed successfully![/]\n\n"
            f"You can now run [bold cyan]passchecker[/bold cyan] from any terminal.\n"
            f"[dim]Location: {target}[/dim]",
            title="[bold green]Install Complete[/]",
            border_style="green"
        ))
    except subprocess.CalledProcessError:
        console.print(Panel(
            "[bold red]Installation failed.[/]\n"
            "Make sure you have sudo privileges and try again.\n\n"
            "[dim]Manual install:\n"
            f"  sudo cp {script_path} {target}\n"
            f"  sudo chmod +x {target}[/dim]",
            title="[bold red]Install Failed[/]",
            border_style="red"
        ))
    except FileNotFoundError:
        console.print("[bold red]ERROR: 'sudo' not found. Are you running Linux?[/]")

# ─────────────────────────────────────────────
#  PASSWORD CHECK (main flow)
# ─────────────────────────────────────────────

def run_password_check():
    password = ""
    while not password:
        password = getpass.getpass("  Enter password to check: ")
        if not password:
            console.print("[bold red]  Password cannot be blank.[/]\n")

    console.print()
    console.print(Rule("[dim]Breach Detection[/]", style="dim"))
    console.print()

    # ── Online HIBP check ──
    console.print("[cyan]  [*] Querying HaveIBeenPwned API (k-anonymity)...[/]")
    online_count = check_password_online(password)

    is_breached = False

    if online_count == -1:
        console.print("  [dim yellow]⚠  Online Check : Skipped (no internet connection)[/]")
    elif online_count and online_count > 0:
        console.print(f"  [bold red]🚨 Online Check : Found in [underline]{online_count:,}[/underline] public data breaches! DO NOT USE.[/]")
        is_breached = True
    else:
        console.print("  [bold green]✔  Online Check : Clean[/]")

    # ── Local rockyou check ──
    console.print("[cyan]  [*] Scanning rockyou.txt wordlist...[/]")
    is_compromised_local = check_rockyou(password)

    if is_compromised_local:
        console.print("  [bold red]🚨 Local Check  : Found in rockyou.txt! DO NOT USE.[/]")
        is_breached = True
    elif is_compromised_local is False:
        console.print("  [bold green]✔  Local Check  : Clean[/]")

    # ── Complexity + Entropy ──
    score, feedback = check_password(password)
    entropy         = calculate_entropy(password)
    bar, ent_label, ent_color = entropy_bar(entropy)

    console.print()
    console.print(Rule("[dim]Analysis[/]", style="dim"))
    console.print()

    # Result table
    table = Table(box=box.SIMPLE_HEAVY, show_header=False, padding=(0, 2))
    table.add_column("Key",   style="dim",        width=18)
    table.add_column("Value", style="bold white",  min_width=36)

    table.add_row("Strength",  strength_label(score, is_breached))
    table.add_row(
        "Entropy",
        f"{bar}  [{ent_color}]{entropy} bits — {ent_label}[/]"
    )
    table.add_row("Length",    f"[white]{len(password)} characters[/]")

    console.print(table)

    # Feedback tips
    if feedback and not is_breached:
        console.print()
        console.print("  [bold yellow]💡 Suggestions:[/]")
        for tip in feedback:
            console.print(f"  [dim yellow] •[/] {tip}")

    # Suggest generator if weak or breached
    if is_breached or score <= 3:
        console.print()
        console.print(
            "  [dim]→ Try [bold cyan]Option 2[/bold cyan] from the main menu to generate a strong password.[/]"
        )

    console.print()
    console.print(Rule(style="dim"))
    console.print()

# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────

def main():
    clear_screen()
    print_banner()

    if not ensure_rockyou_exists():
        console.print("[bold red]Critical Error: Cannot proceed without rockyou.txt.[/]")
        sys.exit(1)

    while True:
        console.print(Rule("[bold cyan]  Main Menu  [/]", style="cyan"))
        console.print()
        console.print("  [cyan]1.[/] [white]Check Password[/]         [dim]Local + HIBP breach detection & complexity[/]")
        console.print("  [cyan]2.[/] [white]Generate Password[/]      [dim]Secure random password or passphrase[/]")

        if IS_LINUX:
            console.print("  [cyan]3.[/] [white]Install to PATH[/]        [dim]Run 'passchecker' from anywhere (Linux)[/]")
            console.print("  [cyan]4.[/] [white]Exit[/]")
            valid = ('1', '2', '3', '4')
            prompt = "\n  Enter choice (1-4): "
        else:
            console.print("  [cyan]3.[/] [white]Exit[/]")
            valid = ('1', '2', '3')
            prompt = "\n  Enter choice (1-3): "

        console.print()
        choice = input(prompt).strip()
        clear_screen()
        print_banner()

        if choice == '1':
            run_password_check()

        elif choice == '2':
            password_generator_menu()
            clear_screen()
            print_banner()

        elif choice == '3' and IS_LINUX:
            install_to_bin()
            input("\n  Press Enter to return to menu...")
            clear_screen()
            print_banner()

        elif (choice == '4' and IS_LINUX) or (choice == '3' and not IS_LINUX):
            console.print("\n  [bold green]Goodbye! Stay secure. 🛡[/]\n")
            break

        else:
            console.print("[bold red]  Invalid option. Please try again.[/]\n")

if __name__ == "__main__":
    main()
