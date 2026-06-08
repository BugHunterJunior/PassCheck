<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:000000,100:222222&height=180&section=header&text=Password%20Checker&fontSize=50&fontColor=00FF00&animation=fadeIn&desc=Cyber%20Security&descSize=20&descAlignY=75&descAlign=50" />

<b>🔐 Password Complexity Checker</b>

<img src="https://img.shields.io/badge/CyberSecurity-0A66C2?style=for-the-badge&logo=hackthebox&logoColor=white" />
<img src="https://img.shields.io/badge/Version-2.0-brightgreen?style=for-the-badge" />
<img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python" />
<img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey?style=for-the-badge&logo=gnubash" />
<img src="https://img.shields.io/badge/HaveIBeenPwned-API-red?style=for-the-badge" />
</div>

---

## Overview

A cross-platform CLI security utility offering **dual-layer breach detection**, **cryptographically secure password generation**, **passphrase support**, and **entropy analysis** — all in a clean, colorized terminal interface powered by `rich`.

---

## Tech Stack

| Component | Detail |
|---|---|
| Language | Python 3.x 🐍 |
| External Library | `rich` 🎨 |
| Standard Libraries | `secrets`, `hashlib`, `math`, `getpass`, `subprocess`, `urllib`, `platform` ⚙️ |
| Online API | HaveIBeenPwned Pwned Passwords v3 (k-anonymity) 🌐 |
| Local Dataset | `rockyou.txt` (~14M passwords) 📂 |

---

## Features

- **Dual-Layer Breach Detection** — Cross-references passwords against both the HaveIBeenPwned API (k-anonymity, zero plaintext exposure) and the local `rockyou.txt` wordlist (~14M entries).

- **Password Generator** — Generates 5 cryptographically secure candidates via Python's `secrets` module. Configurable length (8–64) and toggleable character sets (uppercase, lowercase, digits, symbols), with strength and entropy displayed per result.

- **Passphrase Generator** — Produces memorable multi-word passphrases from a curated 200-word list. Configurable word count (3–8) and custom separator. Ideal for master passwords.

- **Entropy Analysis** — Calculates Shannon entropy (bits) for every password checked or generated, displayed as a color-coded bar ranging from Very Low to Excellent.

- **Complexity Scoring** — Evaluates passwords across 6 criteria with actionable feedback on what to improve.

- **Smart Offline Handling** — HIBP check is gracefully skipped when offline; local wordlist check always runs independently.

- **Install to PATH** *(Linux)* — Installs the tool to `/usr/local/bin/passchecker` so it can be run from any terminal as a system command.

- **Secure Input** — Password input is masked via `getpass`, preventing terminal history exposure and shoulder surfing.

---

## 👨‍💻 Author
### Your password vs brute force — tested here. 🛡️
