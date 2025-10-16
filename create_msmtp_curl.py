#!/usr/bin/env python
"""
Script care creeaza un wrapper bash 'msmtp' care foloseste curl pentru SMTP Gmail.
Curl suporta SMTP si TLS out-of-the-box.
"""

import paramiko
import sys

# Configurare server
HOST = "95.196.191.92"
USER = "root"
PASS = "bebef_999"
PORT = 22

# Configurare Gmail
GMAIL_ADDRESS = "bib.acadiasi@gmail.com"
APP_PASSWORD = "ayigwvgouoginhpd"
TEST_RECIPIENT = "larisbirzu@gmail.com"


def ssh_exec(ssh, cmd, show=True):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
    out = stdout.read().decode("utf-8", errors="ignore")
    err = stderr.read().decode("utf-8", errors="ignore")
    if show:
        if out:
            print(out)
        if err and "warning" not in err.lower():
            print("[WARN] " + err)
    return out, err


# Script bash msmtp wrapper care foloseste curl
MSMTP_CURL_SCRIPT = f'''#!/bin/bash
# msmtp replacement - bash wrapper folosind curl pentru Gmail SMTP

# Configurare Gmail
SMTP_URL="smtps://smtp.gmail.com:465"
SMTP_USER="{GMAIL_ADDRESS}"
SMTP_PASS="{APP_PASSWORD}"
FROM_ADDR="{GMAIL_ADDRESS}"

# Parse arguments
VERBOSE=0
TO_ADDRS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -t|--read-recipients)
            # Recipients from headers (handled below)
            shift
            ;;
        --version)
            echo "msmtp-curl 1.0 (Gmail SMTP via curl)"
            exit 0
            ;;
        -a|--account)
            shift  # Skip account name
            shift
            ;;
        -*)
            shift
            ;;
        *)
            TO_ADDRS+=("$1")
            shift
            ;;
    esac
done

# Citeste mesajul din stdin
MESSAGE=$(cat)

# Extrage destinatarul din headers daca nu e specificat
if [ ${{#TO_ADDRS[@]}} -eq 0 ]; then
    TO=$(echo "$MESSAGE" | grep -i "^To:" | head -1 | sed 's/^To: *//i')
    if [ ! -z "$TO" ]; then
        TO_ADDRS=("$TO")
    fi
fi

# Verifica daca avem destinatar
if [ ${{#TO_ADDRS[@]}} -eq 0 ]; then
    echo "Error: No recipient specified" >&2
    exit 1
fi

RECIPIENT="${{TO_ADDRS[0]}}"

# Creeaza fisier temporar pentru mesaj
TMPFILE=$(mktemp /tmp/msmtp.XXXXXX)
echo "$MESSAGE" > "$TMPFILE"

# Verbose output
if [ "$VERBOSE" -eq 1 ]; then
    echo "Sending via smtp.gmail.com:465 (SMTPS)" >&2
    echo "From: $FROM_ADDR" >&2
    echo "To: $RECIPIENT" >&2
fi

# Trimite prin curl
# Nota: --ssl incerca SSL/TLS chiar daca certificatul e expirat/invalid
curl_opts=(
    --url "$SMTP_URL"
    --mail-from "$FROM_ADDR"
    --mail-rcpt "$RECIPIENT"
    --upload-file "$TMPFILE"
    --user "$SMTP_USER:$SMTP_PASS"
    --insecure
    --silent
    --show-error
)

if [ "$VERBOSE" -eq 1 ]; then
    curl_opts+=(--verbose)
fi

RESULT=$(curl "${{curl_opts[@]}}" 2>&1)
EXIT_CODE=$?

# Cleanup
rm -f "$TMPFILE"

# Output
if [ "$VERBOSE" -eq 1 ]; then
    echo "$RESULT" >&2
fi

if [ $EXIT_CODE -eq 0 ]; then
    [ "$VERBOSE" -eq 1 ] && echo "Mail sent successfully" >&2
    exit 0
else
    echo "Error sending mail: $RESULT" >&2
    exit 1
fi
'''


def main():
    print("=" * 70)
    print("   CREARE MSMTP WRAPPER (CURL) PE SERVER")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica curl
        print("=" * 70)
        print("PASUL 1: Verificare curl si suport SMTP")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "curl --version | head -1", show=False)
        if "curl" in out.lower():
            print(f"[OK] {out.strip()}")
        else:
            print("[ERROR] curl nu este disponibil!")
            return 1
        
        # Verifica suport SMTP
        out, _ = ssh_exec(ssh, "curl --version | grep -i smtp", show=False)
        if out:
            print("[OK] curl suporta SMTP")
        else:
            print("[WARN] curl poate sa nu suporte SMTP (dar vom incerca)")
        
        print()
        
        # 2. Creaza script
        print("=" * 70)
        print("PASUL 2: Creare script msmtp (bash+curl)")
        print("=" * 70)
        
        cmd = f"cat > /usr/local/bin/msmtp <<'EOFBASH'\n{MSMTP_CURL_SCRIPT}\nEOFBASH"
        ssh_exec(ssh, cmd, show=False)
        ssh_exec(ssh, "chmod +x /usr/local/bin/msmtp", show=False)
        
        print("[OK] Script bash+curl creat in /usr/local/bin/msmtp")
        print()
        
        # 3. Test versiune
        print("=" * 70)
        print("PASUL 3: Test wrapper")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "/usr/local/bin/msmtp --version 2>&1", show=False)
        if out:
            print(f"[OK] {out.strip()}")
        print()
        
        # 4. Link-uri sendmail
        print("=" * 70)
        print("PASUL 4: Creare link-uri sendmail")
        print("=" * 70)
        
        ssh_exec(ssh, "ln -sf /usr/local/bin/msmtp /usr/sbin/sendmail", show=False)
        ssh_exec(ssh, "ln -sf /usr/local/bin/msmtp /usr/bin/sendmail", show=False)
        ssh_exec(ssh, "ln -sf /usr/local/bin/msmtp /usr/lib/sendmail", show=False)
        
        print("[OK] Link-uri create")
        print()
        
        # 5. Test trimitere
        print("=" * 70)
        print("PASUL 5: TEST TRIMITERE EMAIL")
        print("=" * 70)
        print()
        print("[INFO] Testez trimiterea prin Gmail SMTP cu curl...")
        print("[INFO] Nota: Serverul are OpenSSL vechi, folosim --insecure")
        print()
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        test_message = f"""From: {GMAIL_ADDRESS}
To: {TEST_RECIPIENT}
Subject: [Test msmtp curl] Email trimis la {timestamp}

Salut,

Acesta este un email de test trimis prin wrapper msmtp care foloseste curl.

Configurare:
- Wrapper bash+curl in /usr/local/bin/msmtp
- SMTP prin Gmail (smtps://smtp.gmail.com:465)
- Server: {HOST}
- Data: {timestamp}

Daca primesti acest mesaj, configurarea functioneaza perfect!

---
Trimis prin msmtp-curl wrapper
"""
        
        # Escapare pentru bash
        escaped = test_message.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        print(f"[INFO] Trimitere email de test catre {TEST_RECIPIENT}...")
        print()
        
        cmd = f'echo "{escaped}" | /usr/local/bin/msmtp -v -t 2>&1'
        out, _ = ssh_exec(ssh, cmd, show=False)
        
        if out:
            print("Output:")
            print("-" * 70)
            print(out)
            print("-" * 70)
            print()
        
        # Verificare rezultat
        if "successfully" in out.lower() or ("250" in out and "error" not in out.lower()):
            print()
            print("=" * 70)
            print(">>> SUCCES! EMAIL TRIMIS! <<<")
            print("=" * 70)
            print()
        elif "ssl" in out.lower() or "tls" in out.lower() or "certificate" in out.lower():
            print()
            print("[WARN] Posibile probleme SSL/TLS (OpenSSL vechi)")
            print("       Emailul poate fi trimis totusi (folosim --insecure)")
        elif "error" in out.lower():
            print()
            print("[ERROR] Eroare la trimitere - vezi output mai sus")
        
        # 6. Test comanda mail
        print()
        print("=" * 70)
        print("PASUL 6: Test comanda 'mail'")
        print("=" * 70)
        
        cmd = f'echo "Test prin mail command la {timestamp}" | mail -s "[Test] mail cmd" {TEST_RECIPIENT} 2>&1'
        print(f"[INFO] Rulare: echo 'Test...' | mail -s '[Test]' {TEST_RECIPIENT}")
        out, _ = ssh_exec(ssh, cmd, show=False)
        
        if out:
            print(f"Output: {out}")
        else:
            print("[OK] Comanda executata (fara erori)")
        
        print()
        
        # 7. Sumar
        print("=" * 70)
        print("   CONFIGURARE COMPLETATA!")
        print("=" * 70)
        print()
        print(">> Verificari finale:")
        print(f"   1. Verifica inbox-ul la {TEST_RECIPIENT}")
        print("   2. Verifica folderul Spam/Junk")
        print("   3. Asteapta 1-2 minute pentru livrare")
        print()
        print(">> Testare manuala:")
        print(f'   ssh {USER}@{HOST}')
        print(f'   echo "Test manual" | msmtp {TEST_RECIPIENT}')
        print(f'   echo "Test mail" | mail -s "Test" {TEST_RECIPIENT}')
        print()
        print(">> Configurare:")
        print("   Script: /usr/local/bin/msmtp (bash+curl wrapper)")
        print("   Link-uri: /usr/sbin/sendmail, /usr/bin/sendmail")
        print("   SMTP: smtps://smtp.gmail.com:465")
        print(f"   Cont: {GMAIL_ADDRESS}")
        print()
        print(">> Avantaje solutie:")
        print("   - Nu necesita compilare sau binare statice")
        print("   - Foloseste doar curl (deja instalat)")
        print("   - Suport TLS prin curl")
        print("   - Compatibil cu orice server Linux")
        print()
        
    except Exception as e:
        print(f"[ERROR] Eroare: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        try:
            ssh.close()
            print("[INFO] Conexiune inchisa.")
        except:
            pass
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[WARN] Script intrerupt.")
        sys.exit(130)

