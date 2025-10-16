#!/usr/bin/env python3
"""
Script care creeaza pe server un wrapper Python pentru msmtp care trimite direct prin Gmail SMTP.
Aceasta este o alternativa la binarul msmtp static care evita problemele de compatibilitate.
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
            print(f"[WARN] {err}")
    return out, err


# Script Python msmtp wrapper care va fi instalat pe server
MSMTP_PYTHON_SCRIPT = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
msmtp replacement - Python SMTP client pentru Gmail
Compatibil cu interfata msmtp standard
"""

import sys
import smtplib
import email.utils
from email.mime.text import MIMEText
import re

# Configurare Gmail
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "{GMAIL_ADDRESS}"
SMTP_PASS = "{APP_PASSWORD}"
FROM_ADDR = "{GMAIL_ADDRESS}"

def send_email(recipients, message_text):
    """Trimite email prin Gmail SMTP"""
    try:
        # Parse email message
        lines = message_text.strip().split('\\n')
        
        # Extrage headers
        to = None
        subject = None
        from_addr = FROM_ADDR
        headers_end = 0
        
        for i, line in enumerate(lines):
            if line.strip() == '':
                headers_end = i
                break
            if line.lower().startswith('to:'):
                to = line[3:].strip()
            elif line.lower().startswith('subject:'):
                subject = line[8:].strip()
            elif line.lower().startswith('from:'):
                from_addr = line[5:].strip()
        
        # Body este tot dupa linia goala
        body = '\\n'.join(lines[headers_end+1:])
        
        # Daca nu avem destinatar din headers, folosim recipients
        if not to and recipients:
            to = recipients[0]
        
        if not to:
            print("Error: No recipient specified", file=sys.stderr)
            return False
        
        # Creeaza mesaj
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['To'] = to
        msg['From'] = from_addr
        msg['Subject'] = subject or '(no subject)'
        msg['Date'] = email.utils.formatdate(localtime=True)
        
        # Trimite prin Gmail
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
        server.set_debuglevel(0)  # 1 pentru debug
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error: {{e}}", file=sys.stderr)
        return False


def main():
    """Main function - compatibil cu msmtp CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='msmtp-compatible Python SMTP client')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-t', '--read-recipients', action='store_true', 
                        help='Read recipients from message headers')
    parser.add_argument('--version', action='store_true', help='Show version')
    parser.add_argument('-a', '--account', help='Account name (ignored)')
    parser.add_argument('recipients', nargs='*', help='Recipient email addresses')
    
    args = parser.parse_args()
    
    if args.version:
        print("msmtp-python 1.0 (Gmail SMTP wrapper)")
        return 0
    
    # Citeste mesajul din stdin
    message_text = sys.stdin.read()
    
    # Daca -t este specificat, extrage destinatarii din headers
    recipients = args.recipients
    
    if args.verbose:
        print(f"Sending via {{SMTP_HOST}}:{{SMTP_PORT}}", file=sys.stderr)
        print(f"From: {{FROM_ADDR}}", file=sys.stderr)
        if recipients:
            print(f"To: {{', '.join(recipients)}}", file=sys.stderr)
    
    # Trimite email
    success = send_email(recipients, message_text)
    
    if args.verbose:
        if success:
            print("Mail sent successfully", file=sys.stderr)
        else:
            print("Failed to send mail", file=sys.stderr)
    
    return 0 if success else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\\nInterrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {{e}}", file=sys.stderr)
        sys.exit(1)
'''


def main():
    print("=" * 70)
    print("   CREARE MSMTP WRAPPER PYTHON PE SERVER")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Creaza scriptul Python pe server
        print("=" * 70)
        print("PASUL 1: Creare script msmtp Python pe server")
        print("=" * 70)
        
        cmd = f"cat > /usr/local/bin/msmtp <<'EOFPYTHON'\n{MSMTP_PYTHON_SCRIPT}\nEOFPYTHON"
        ssh_exec(ssh, cmd, show=False)
        ssh_exec(ssh, "chmod +x /usr/local/bin/msmtp", show=False)
        
        print("[OK] Script Python msmtp creat in /usr/local/bin/msmtp")
        print()
        
        # 2. Verifica Python pe server
        print("=" * 70)
        print("PASUL 2: Verificare Python pe server")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "python --version 2>&1 || python3 --version 2>&1 || python2 --version 2>&1", show=False)
        
        if "Python" in out:
            print(f"[OK] {out.strip()}")
            
            # Actualizeaza shebang daca e nevoie
            if "Python 3" in out:
                ssh_exec(ssh, "sed -i '1s|.*|#!/usr/bin/env python3|' /usr/local/bin/msmtp", show=False)
            elif "Python 2" in out:
                ssh_exec(ssh, "sed -i '1s|.*|#!/usr/bin/env python|' /usr/local/bin/msmtp", show=False)
        else:
            print("[WARN] Python nu pare disponibil. Voi incerca totusi...")
        
        print()
        
        # 3. Test versiune msmtp
        print("=" * 70)
        print("PASUL 3: Test wrapper msmtp")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "/usr/local/bin/msmtp --version", show=False)
        if out:
            print(f"[OK] {out.strip()}")
        print()
        
        # 4. Creare link-uri sendmail
        print("=" * 70)
        print("PASUL 4: Creare link-uri sendmail")
        print("=" * 70)
        
        ssh_exec(ssh, "ln -sf /usr/local/bin/msmtp /usr/sbin/sendmail", show=False)
        ssh_exec(ssh, "ln -sf /usr/local/bin/msmtp /usr/bin/sendmail", show=False)
        ssh_exec(ssh, "ln -sf /usr/local/bin/msmtp /usr/lib/sendmail", show=False)
        
        print("[OK] Link-uri create")
        print()
        
        # 5. Test trimitere email
        print("=" * 70)
        print("PASUL 5: TEST TRIMITERE EMAIL")
        print("=" * 70)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        test_message = f"""From: {GMAIL_ADDRESS}
To: {TEST_RECIPIENT}
Subject: [Test msmtp Python] Email trimis la {timestamp}

Salut,

Acesta este un email de test trimis prin wrapper-ul Python msmtp.

Configurare:
- Wrapper Python in /usr/local/bin/msmtp
- SMTP direct prin Gmail (port 587, STARTTLS)
- Cont: {GMAIL_ADDRESS}
- Data: {timestamp}

Daca primesti acest email, configurarea functioneaza perfect!

---
Trimis automat prin msmtp-python wrapper
"""
        
        # Escapare pentru bash
        escaped_msg = test_message.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        print(f"[INFO] Trimitere email de test catre {TEST_RECIPIENT}...")
        print()
        
        cmd = f'echo "{escaped_msg}" | /usr/local/bin/msmtp -v -t'
        out, err = ssh_exec(ssh, cmd)
        
        print()
        
        # Verificare rezultat
        if "successfully" in out.lower() or "sent" in out.lower():
            print("[OK] >>> EMAIL TRIMIS CU SUCCES! <<<")
        elif "error" in out.lower() or "failed" in out.lower():
            print("[ERROR] Eroare la trimitere")
        else:
            print("[INFO] Output:")
            print(out)
        
        print()
        
        # 6. Test cu comanda mail
        print("=" * 70)
        print("PASUL 6: Test comanda 'mail'")
        print("=" * 70)
        
        cmd = f'echo "Test mail command la {timestamp}" | mail -s "[Test] mail command" {TEST_RECIPIENT}'
        print(f"[INFO] Rulare: {cmd}")
        out, _ = ssh_exec(ssh, cmd, show=False)
        
        print("[OK] Comanda 'mail' executata (verifica inbox-ul)")
        print()
        
        # 7. Sumar
        print("=" * 70)
        print("   CONFIGURARE COMPLETATA!")
        print("=" * 70)
        print()
        print(">> Verificari:")
        print(f"   1. Verifica inbox-ul la {TEST_RECIPIENT}")
        print("   2. Verifica folderul Spam/Junk")
        print()
        print(">> Testare manuala:")
        print(f'   ssh {USER}@{HOST}')
        print(f'   echo "Test" | mail -s "Test manual" {TEST_RECIPIENT}')
        print()
        print(">> Configurare:")
        print("   Script: /usr/local/bin/msmtp (Python wrapper)")
        print("   Link-uri: /usr/sbin/sendmail, /usr/bin/sendmail")
        print()
        print(">> Nota: Acest wrapper trimite direct prin Gmail SMTP")
        print("   fara a avea nevoie de binare statice sau biblioteci.")
        print()
        
    except Exception as e:
        print(f"[ERROR] Eroare: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        try:
            ssh.close()
            print("[INFO] Conexiune inchisa.")
        except:
            pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[WARN] Script intrerupt.")
        sys.exit(130)

