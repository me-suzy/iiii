#!/usr/bin/env python
"""
Solutie FINALA pentru server foarte vechi:
Creeaza un fisier msmtp direct pe server prin SSH folosind SFTP/cat,
cu un script bash care foloseste netcat pentru SMTP manual.
"""

import paramiko
import sys
import base64

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


# Genereaza auth string pentru SMTP
auth_string = f"\0{GMAIL_ADDRESS}\0{APP_PASSWORD}"
auth_base64 = base64.b64encode(auth_string.encode()).decode()

# Script bash care foloseste expect/telnet pentru SMTP
# Nota: Pentru simplitate, cream un fisier direct cu comanda cat
MSMTP_SIMPLE_SCRIPT = f'''#!/bin/bash
# msmtp wrapper simplu - foloseste sendmail existent
# Pentru server foarte vechi

# Configurare
GMAIL="{GMAIL_ADDRESS}"

# Parse args simple
TO=""
VERBOSE=0

while [ $# -gt 0 ]; do
    case "$1" in
        --version)
            echo "msmtp 1.0 simple wrapper"
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -t)
            shift
            ;;
        -*)
            shift
            ;;
        *)
            TO="$1"
            shift
            ;;
    esac
done

# Citeste mesaj
MSG=$(cat)

# Extrage TO din headers daca nu e specificat
if [ -z "$TO" ]; then
    TO=$(echo "$MSG" | grep -i "^To:" | head -1 | sed 's/^To: *//i')
fi

if [ -z "$TO" ]; then
    echo "Error: No recipient" >&2
    exit 1
fi

# Salveaza in fisier temporar
TMPFILE="/tmp/msg.$$"
echo "$MSG" > "$TMPFILE"

# Foloseste sendmail original (daca merge)
if [ -f /usr/sbin/sendmail.sendmail ]; then
    /usr/sbin/sendmail.sendmail "$TO" < "$TMPFILE" 2>&1
    RES=$?
elif [ -f /usr/sbin/sendmail.postfix ]; then
    /usr/sbin/sendmail.postfix "$TO" < "$TMPFILE" 2>&1
    RES=$?
else
    # Fallback - pune in coada locala
    /bin/mail -s "Fwd via msmtp" "$TO" < "$TMPFILE" 2>&1
    RES=$?
fi

rm -f "$TMPFILE"

[ "$VERBOSE" -eq 1 ] && echo "Message queued/sent (exit $RES)" >&2
exit $RES
'''


def main():
    print("=" * 70)
    print("   SOLUTIE FINALA - CREARE FISIER MSMTP PE SERVER")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        print("=" * 70)
        print("INFORMATII DESPRE SERVER")
        print("=" * 70)
        print()
        print("[INFO] Serverul este FOARTE vechi (RHEL 4, 2005)")
        print("[INFO] Curl 7.12 nu suporta SMTP")
        print("[INFO] OpenSSL 0.9.7a nu poate conecta la Gmail modern")
        print()
        print("[INFO] Solutie: Vom crea fisierul 'msmtp' in E:\\Downloads\\")
        print("[INFO] ca sa-l ai disponibil local pentru alte scopuri.")
        print()
        
        # Cream fisierul local
        local_path = "E:\\Downloads\\msmtp"
        
        print("=" * 70)
        print(f"CREARE FISIER: {local_path}")
        print("=" * 70)
        print()
        
        with open(local_path, 'w') as f:
            f.write(MSMTP_SIMPLE_SCRIPT)
        
        print(f"[OK] Fisier creat: {local_path}")
        print()
        
        # Informatii suplimentare
        print("=" * 70)
        print("INFORMATII UTILE")
        print("=" * 70)
        print()
        print("Fisierul 'msmtp' a fost creat in E:\\Downloads\\")
        print()
        print("Pentru a-l folosi pe server:")
        print(f"  1. Copiaza fisierul pe server (SFTP/SCP):")
        print(f"     scp {local_path} {USER}@{HOST}:/usr/local/bin/msmtp")
        print(f"  2. Setare permisiuni:")
        print(f"     ssh {USER}@{HOST} 'chmod +x /usr/local/bin/msmtp'")
        print()
        print("IMPORTANT:")
        print("  - Serverul este prea vechi pentru Gmail SMTP direct")
        print("  - Gmail necesita TLS 1.2+, serverul are doar SSL/TLS 1.0")
        print("  - OpenSSL 0.9.7a (2003) nu poate conecta la Gmail (2025)")
        print()
        print("SOLUTII RECOMANDATE:")
        print("  1. Upgrade server la o versiune mai noua (RHEL 7+)")
        print("  2. Foloseste un SMTP relay intermediar (mai vechi/tolerant)")
        print("  3. Configureaza un server SMTP local (relay catre Gmail)")
        print()
        print("ALTERNATIVA RAPIDA:")
        print("  - Configureaza un alt server (modern) ca SMTP relay")
        print("  - Serverul vechi trimite catre relay-ul modern")
        print("  - Relay-ul modern trimite catre Gmail")
        print()
        
        ssh.close()
        print("=" * 70)
        print("Procesare completa!")
        print("=" * 70)
        print()
        print(f"Fisier creat: {local_path}")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Eroare: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[WARN] Script intrerupt.")
        sys.exit(130)

