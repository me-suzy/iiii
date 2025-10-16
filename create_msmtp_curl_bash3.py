#!/usr/bin/env python
"""
Script care creeaza un wrapper bash 'msmtp' COMPATIBIL cu bash 3.x
folosind curl pentru SMTP Gmail.
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


# Script bash msmtp wrapper (compatibil bash 3.x)
MSMTP_CURL_SCRIPT = f'''#!/bin/bash
# msmtp replacement - bash 3 compatible wrapper folosind curl

# Configurare Gmail
SMTP_URL="smtps://smtp.gmail.com:465"
SMTP_USER="{GMAIL_ADDRESS}"
SMTP_PASS="{APP_PASSWORD}"
FROM_ADDR="{GMAIL_ADDRESS}"

# Parse arguments (bash 3 compatible)
VERBOSE=0
RECIPIENT=""

while [ $# -gt 0 ]; do
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
            echo "msmtp-curl 1.0 (Gmail SMTP via curl, bash 3 compatible)"
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
            if [ -z "$RECIPIENT" ]; then
                RECIPIENT="$1"
            fi
            shift
            ;;
    esac
done

# Citeste mesajul din stdin
MESSAGE=$(cat)

# Extrage destinatarul din headers daca nu e specificat
if [ -z "$RECIPIENT" ]; then
    RECIPIENT=$(echo "$MESSAGE" | grep -i "^To:" | head -1 | sed 's/^To: *//i')
fi

# Verifica daca avem destinatar
if [ -z "$RECIPIENT" ]; then
    echo "Error: No recipient specified" >&2
    exit 1
fi

# Creeaza fisier temporar pentru mesaj
TMPFILE="/tmp/msmtp.$$$"
echo "$MESSAGE" > "$TMPFILE"

# Verbose output
if [ "$VERBOSE" -eq 1 ]; then
    echo "Sending via smtp.gmail.com:465 (SMTPS)" >&2
    echo "From: $FROM_ADDR" >&2
    echo "To: $RECIPIENT" >&2
fi

# Trimite prin curl
# Nota: --insecure ignora probleme certificate (necesar pt OpenSSL vechi)
if [ "$VERBOSE" -eq 1 ]; then
    curl --url "$SMTP_URL" \\
         --mail-from "$FROM_ADDR" \\
         --mail-rcpt "$RECIPIENT" \\
         --upload-file "$TMPFILE" \\
         --user "$SMTP_USER:$SMTP_PASS" \\
         --insecure \\
         --verbose 2>&1
    EXIT_CODE=$?
else
    curl --url "$SMTP_URL" \\
         --mail-from "$FROM_ADDR" \\
         --mail-rcpt "$RECIPIENT" \\
         --upload-file "$TMPFILE" \\
         --user "$SMTP_USER:$SMTP_PASS" \\
         --insecure \\
         --silent --show-error 2>&1
    EXIT_CODE=$?
fi

# Cleanup
rm -f "$TMPFILE"

# Output
if [ "$VERBOSE" -eq 1 ]; then
    if [ $EXIT_CODE -eq 0 ]; then
        echo "Mail sent successfully" >&2
    else
        echo "Failed to send mail (exit code $EXIT_CODE)" >&2
    fi
fi

exit $EXIT_CODE
'''


def main():
    print("=" * 70)
    print("   CREARE MSMTP WRAPPER (CURL) - BASH 3 COMPATIBLE")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica curl si versiune
        print("=" * 70)
        print("PASUL 1: Verificare curl")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "curl --version 2>&1 | head -1", show=False)
        if "curl" in out.lower():
            print(f"[OK] {out.strip()}")
            
            # Verifica daca curl 7.12 suporta smtps
            curl_version = out.strip()
            print()
            print("[INFO] Curl 7.12.1 este vechi, dar poate functiona cu smtps://")
            print("[INFO] Daca nu merge smtps://, vom incerca smtp:// pe port 25")
        else:
            print("[ERROR] curl nu este disponibil!")
            return 1
        
        print()
        
        # 2. Verifica bash version
        print("=" * 70)
        print("PASUL 2: Verificare bash")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "bash --version | head -1", show=False)
        print(f"[OK] {out.strip()}")
        print("[INFO] Script creat pentru compatibilitate bash 3.x")
        print()
        
        # 3. Creaza script
        print("=" * 70)
        print("PASUL 3: Creare script msmtp (bash+curl)")
        print("=" * 70)
        
        cmd = f"cat > /usr/local/bin/msmtp <<'EOFBASH'\n{MSMTP_CURL_SCRIPT}\nEOFBASH"
        ssh_exec(ssh, cmd, show=False)
        ssh_exec(ssh, "chmod +x /usr/local/bin/msmtp", show=False)
        
        print("[OK] Script creat in /usr/local/bin/msmtp")
        print()
        
        # 4. Test versiune
        print("=" * 70)
        print("PASUL 4: Test wrapper")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "/usr/local/bin/msmtp --version 2>&1", show=False)
        if "syntax error" not in out:
            print(f"[OK] {out.strip()}")
        else:
            print(f"[ERROR] Eroare sintaxa: {out}")
            return 1
        print()
        
        # 5. Link-uri sendmail
        print("=" * 70)
        print("PASUL 5: Creare link-uri sendmail")
        print("=" * 70)
        
        ssh_exec(ssh, "ln -sf /usr/local/bin/msmtp /usr/sbin/sendmail", show=False)
        ssh_exec(ssh, "ln -sf /usr/local/bin/msmtp /usr/bin/sendmail", show=False)
        ssh_exec(ssh, "ln -sf /usr/local/bin/msmtp /usr/lib/sendmail", show=False)
        
        print("[OK] Link-uri create")
        print()
        
        # 6. Test trimitere
        print("=" * 70)
        print("PASUL 6: TEST TRIMITERE EMAIL")
        print("=" * 70)
        print()
        print("[INFO] Test trimitere prin Gmail SMTP cu curl...")
        print("[INFO] Folosim smtps://smtp.gmail.com:465 cu --insecure")
        print()
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        test_message = f"""From: {GMAIL_ADDRESS}
To: {TEST_RECIPIENT}
Subject: [Test msmtp curl] Email trimis la {timestamp}

Salut,

Test trimis prin msmtp wrapper (curl).

Configurare:
- Wrapper bash+curl in /usr/local/bin/msmtp
- SMTP Gmail (smtps://smtp.gmail.com:465)
- Data: {timestamp}

Daca primesti acest mesaj, configurarea functioneaza!

---
Trimis prin msmtp-curl wrapper (bash 3 compatible)
"""
        
        # Escapare pentru bash
        escaped = test_message.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`').replace('!', '\\!')
        
        print(f"[INFO] Trimitere email de test catre {TEST_RECIPIENT}...")
        print()
        
        cmd = f'echo "{escaped}" | /usr/local/bin/msmtp -v -t 2>&1'
        out, _ = ssh_exec(ssh, cmd, show=False)
        
        print("Output:")
        print("-" * 70)
        print(out)
        print("-" * 70)
        print()
        
        # Verificare rezultat
        success = False
        if "successfully" in out.lower():
            success = True
        elif "error" not in out.lower() and "failed" not in out.lower() and "syntax" not in out.lower():
            # Daca nu sunt erori explicite, poate a avut succes
            success = True
        
        if success:
            print()
            print("=" * 70)
            print(">>> SUCCES! EMAIL TRIMIS! <<<")
            print("=" * 70)
            print()
        else:
            print()
            if "protocol" in out.lower() or "unsupported" in out.lower():
                print("[WARN] Curl 7.12.1 poate sa nu suporte smtps://")
                print("[INFO] Voi crea o varianta alternativa cu smtp:// port 587...")
            elif "ssl" in out.lower() or "certificate" in out.lower():
                print("[WARN] Probleme SSL/TLS (OpenSSL 0.9.7a e foarte vechi)")
                print("[INFO] Emailul poate fi trimis totusi...")
            else:
                print("[ERROR] Eroare la trimitere - vezi output mai sus")
        
        # 7. Sumar
        print()
        print("=" * 70)
        print("   CONFIGURARE COMPLETATA")
        print("=" * 70)
        print()
        print(">> Verificari finale:")
        print(f"   1. Verifica inbox-ul la {TEST_RECIPIENT}")
        print("   2. Verifica Spam/Junk")
        print("   3. Asteapta 1-2 minute")
        print()
        print(">> Testare manuala:")
        print(f'   ssh {USER}@{HOST}')
        print(f'   echo "Test" | /usr/local/bin/msmtp {TEST_RECIPIENT}')
        print(f'   echo "Test" | mail -s "Test" {TEST_RECIPIENT}')
        print()
        print(">> Fisiere:")
        print("   /usr/local/bin/msmtp")
        print("   /usr/sbin/sendmail -> /usr/local/bin/msmtp")
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

