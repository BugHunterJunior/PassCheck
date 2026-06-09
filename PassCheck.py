#!/usr/bin/env python3
import re
import os
import sys
import math
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
        "[dim cyan]        🔐 Password Security Checker  •  Dual-Layer Breach Detection[/]\n"
    )

# ─────────────────────────────────────────────
#  AUTO INSTALL TO PATH  (Linux only)
# ─────────────────────────────────────────────

INSTALL_TARGET = "/usr/local/bin/passchecker"
INSTALL_FLAG   = os.path.expanduser("~/.passchecker_installed")

def auto_install():
    """
    On first run (Linux only), automatically installs the script to
    /usr/local/bin/passchecker so it can be run from anywhere.
    Skips silently on Windows or if already installed.
    """
    if IS_WINDOWS:
        return
    if os.path.exists(INSTALL_FLAG):
        return

    script_path = os.path.abspath(__file__)

    # Already running from the install target — nothing to do
    if script_path == INSTALL_TARGET:
        open(INSTALL_FLAG, 'w').close()
        return

    console.print(Panel(
        "[cyan]First run detected — installing PassCheck to PATH...[/]\n"
        "[dim]This allows you to run [bold]passchecker[/bold] from any terminal.[/dim]",
        title="[bold cyan]Auto Install[/]",
        border_style="cyan"
    ))

    try:
        subprocess.run(["sudo", "cp", script_path, INSTALL_TARGET], check=True)
        subprocess.run(["sudo", "chmod", "+x", INSTALL_TARGET],     check=True)
        open(INSTALL_FLAG, 'w').close()
        console.print(Panel(
            "[bold green]✔ Installed successfully![/]\n\n"
            "You can now run [bold cyan]passchecker[/bold cyan] from any terminal.\n"
            f"[dim]Location: {INSTALL_TARGET}[/dim]",
            title="[bold green]Install Complete[/]",
            border_style="green"
        ))
    except subprocess.CalledProcessError:
        console.print(Panel(
            "[bold red]Auto-install failed.[/] Sudo privileges required.\n\n"
            "[dim]Manual install:\n"
            f"  sudo cp {script_path} {INSTALL_TARGET}\n"
            f"  sudo chmod +x {INSTALL_TARGET}[/dim]",
            title="[bold yellow]Install Skipped[/]",
            border_style="yellow"
        ))
    except FileNotFoundError:
        pass  # sudo not found — skip silently

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
        req = urllib.request.Request(url, headers={'User-Agent': 'Python-PassChecker'})
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
    charset = 0
    if re.search(r"[a-z]", password):                    charset += 26
    if re.search(r"[A-Z]", password):                    charset += 26
    if re.search(r"[0-9]", password):                    charset += 10
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
    max_display = 80.0
    filled = min(int((entropy / max_display) * 30), 30)
    empty  = 30 - filled

    if entropy < 28:
        color, label = "red",   "Very Low"
    elif entropy < 36:
        color, label = "yellow","Low"
    elif entropy < 60:
        color, label = "cyan",  "Good"
    else:
        color, label = "green", "Excellent"

    bar = f"[{color}]{'█' * filled}[/][dim]{'░' * empty}[/]"
    return bar, label, color

# ─────────────────────────────────────────────
#  PASSWORD CHECK
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

    # Online HIBP check
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

    # Local rockyou check
    console.print("[cyan]  [*] Scanning rockyou.txt wordlist...[/]")
    is_compromised_local = check_rockyou(password)

    if is_compromised_local:
        console.print("  [bold red]🚨 Local Check  : Found in rockyou.txt! DO NOT USE.[/]")
        is_breached = True
    elif is_compromised_local is False:
        console.print("  [bold green]✔  Local Check  : Clean[/]")

    # Complexity + Entropy
    score, feedback         = check_password(password)
    entropy                 = calculate_entropy(password)
    bar, ent_label, ent_color = entropy_bar(entropy)

    console.print()
    console.print(Rule("[dim]Analysis[/]", style="dim"))
    console.print()

    table = Table(box=box.SIMPLE_HEAVY, show_header=False, padding=(0, 2))
    table.add_column("Key",   style="dim",       width=18)
    table.add_column("Value", style="bold white", min_width=36)

    table.add_row("Strength", strength_label(score, is_breached))
    table.add_row("Entropy",  f"{bar}  [{ent_color}]{entropy} bits — {ent_label}[/]")
    table.add_row("Length",   f"[white]{len(password)} characters[/]")

    console.print(table)

    if feedback and not is_breached:
        console.print()
        console.print("  [bold yellow]💡 Suggestions:[/]")
        for tip in feedback:
            console.print(f"  [dim yellow] •[/] {tip}")

    console.print()
    console.print(Rule(style="dim"))
    console.print()

# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────

def main():
    clear_screen()
    print_banner()
    auto_install()

    if not ensure_rockyou_exists():
        console.print("[bold red]Critical Error: Cannot proceed without rockyou.txt.[/]")
        sys.exit(1)

    while True:
        console.print(Rule("[bold cyan]  Main Menu  [/]", style="cyan"))
        console.print()
        console.print("  [cyan]1.[/] [white]Check Password[/]    [dim]Local + HIBP breach detection & complexity[/]")
        console.print("  [cyan]2.[/] [white]Exit[/]")
        console.print()

        choice = input("  Enter choice (1-2): ").strip()
        clear_screen()
        print_banner()

        if choice == '1':
            run_password_check()
        elif choice == '2':
            console.print("\n  [bold green]Goodbye! Stay secure. 🛡[/]\n")
            break
        else:
            console.print("[bold red]  Invalid option. Please try again.[/]\n")

if __name__ == "__main__":
    main()
