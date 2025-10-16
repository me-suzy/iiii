#!/usr/bin/env python
"""
Script care creeaza pe server un wrapper Python pentru msmtp compatibil cu Python 2.x
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


# Script Python 2 compatible msmtp wrapper
MSMTP_PYTHON_SCRIPT = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
msmtp replacement - Python SMTP client pentru Gmail (Python 2 compatible)
"""

import sys
import smtplib
from email.mime.text import MIMEText
from email import utils as email_utils

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
            sys.stderr.write("Error: No recipient specified\\n")
            return False
        
        # Creeaza mesaj
        msg = MIMEText(body.encode('utf-8'), 'plain', 'utf-8')
        msg['To'] = to
        msg['From'] = from_addr
        msg['Subject'] = subject or '(no subject)'
        msg['Date'] = email_utils.formatdate(localtime=True)
        
        # Trimite prin Gmail
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
        server.set_debuglevel(0)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(from_addr, [to], msg.as_string())
        server.quit()
        
        return True
        
    except Exception as e:
        sys.stderr.write("Error: " + str(e) + "\\n")
        return False


def main():
    """Main function - compatibil cu msmtp CLI"""
    # Parse simple command line arguments (fara argparse pentru Python 2)
    verbose = False
    read_recipients = False
    recipients = []
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ['-v', '--verbose']:
            verbose = True
        elif arg in ['-t', '--read-recipients']:
            read_recipients = True
        elif arg == '--version':
            print("msmtp-python 1.0 (Gmail SMTP wrapper, Python 2 compatible)")
            return 0
        elif arg in ['-a', '--account']:
            i += 1  # Skip next arg (account name)
        elif not arg.startswith('-'):
            recipients.append(arg)
        i += 1
    
    # Citeste mesajul din stdin
    message_text = sys.stdin.read()
    
    if verbose:
        sys.stderr.write("Sending via " + SMTP_HOST + ":" + str(SMTP_PORT) + "\\n")
        sys.stderr.write("From: " + FROM_ADDR + "\\n")
        if recipients:
            sys.stderr.write("To: " + ", ".join(recipients) + "\\n")
    
    # Trimite email
    success = send_email(recipients, message_text)
    
    if verbose:
        if success:
            sys.stderr.write("Mail sent successfully\\n")
        else:
            sys.stderr.write("Failed to send mail\\n")
    
    return 0 if success else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.stderr.write("\\nInterrupted\\n")
        sys.exit(130)
    except Exception as e:
        sys.stderr.write("Fatal error: " + str(e) + "\\n")
        sys.exit(1)
'''


def main():
    print("=" * 70)
    print("   CREARE MSMTP WRAPPER PYTHON 2 PE SERVER")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica Python pe server
        print("=" * 70)
        print("PASUL 1: Verificare Python pe server")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "python --version 2>&1 || python3 --version 2>&1 || python2 --version 2>&1 || echo 'NO PYTHON'", show=False)
        
        if "Python" in out:
            print(f"[OK] Gasit: {out.strip()}")
            python_cmd = "python"
            if "Python 3" in out:
                python_cmd = "python3"
            elif "Python 2" in out:
                python_cmd = "python"
        else:
            print("[ERROR] Python nu este disponibil pe server!")
            print("Te rog instaleaza Python mai intai.")
            return 1
        
        print()
        
        # 2. Creaza scriptul Python pe server
        print("=" * 70)
        print("PASUL 2: Creare script msmtp Python pe server")
        print("=" * 70)
        
        cmd = f"cat > /usr/local/bin/msmtp <<'EOFPYTHON'\n{MSMTP_PYTHON_SCRIPT}\nEOFPYTHON"
        ssh_exec(ssh, cmd, show=False)
        ssh_exec(ssh, f"sed -i '1s|.*|#!{python_cmd}|' /usr/local/bin/msmtp", show=False)
        ssh_exec(ssh, "chmod +x /usr/local/bin/msmtp", show=False)
        
        print("[OK] Script Python msmtp creat in /usr/local/bin/msmtp")
        print()
        
        # 3. Test versiune msmtp
        print("=" * 70)
        print("PASUL 3: Test wrapper msmtp")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "/usr/local/bin/msmtp --version 2>&1", show=False)
        if "msmtp-python" in out:
            print(f"[OK] {out.strip()}")
        else:
            print(f"[WARN] Output: {out.strip()}")
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
Trimis automat prin msmtp-python wrapper (Python 2 compatible)
"""
        
        # Escapare pentru bash
        escaped_msg = test_message.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        print(f"[INFO] Trimitere email de test catre {TEST_RECIPIENT}...")
        print()
        
        cmd = f'echo "{escaped_msg}" | /usr/local/bin/msmtp -v -t 2>&1'
        out, err = ssh_exec(ssh, cmd, show=False)
        
        # Afiseaza output
        if out:
            print("Output:")
            print(out)
        
        # Verificare rezultat
        if "successfully" in out.lower() or "sent" in out.lower() or "250" in out:
            print()
            print("[OK] >>> EMAIL TRIMIS CU SUCCES! <<<")
        elif "error" in out.lower() or "failed" in out.lower() or "traceback" in out.lower():
            print()
            print("[ERROR] Eroare la trimitere - vezi output mai sus")
        
        print()
        
        # 6. Test cu comanda mail
        print("=" * 70)
        print("PASUL 6: Test comanda 'mail'")
        print("=" * 70)
        
        cmd = f'echo "Test mail command la {timestamp}" | mail -s "[Test] mail command" {TEST_RECIPIENT} 2>&1'
        print(f"[INFO] Rulare: echo 'Test...' | mail -s '[Test] mail command' {TEST_RECIPIENT}")
        out, _ = ssh_exec(ssh, cmd, show=False)
        
        if out and ("error" in out.lower() or "failed" in out.lower()):
            print(f"[WARN] Output: {out}")
        else:
            print("[OK] Comanda 'mail' executata")
        
        print()
        
        # 7. Sumar
        print("=" * 70)
        print("   CONFIGURARE COMPLETATA!")
        print("=" * 70)
        print()
        print(">> Verificari:")
        print(f"   1. Verifica inbox-ul la {TEST_RECIPIENT}")
        print("   2. Verifica folderul Spam/Junk")
        print("   3. Asteapta 1-2 minute pentru livrare")
        print()
        print(">> Testare manuala:")
        print(f'   ssh {USER}@{HOST}')
        print(f'   echo "Test manual" | mail -s "Test" {TEST_RECIPIENT}')
        print()
        print(">> Configurare:")
        print("   Script: /usr/local/bin/msmtp (Python wrapper)")
        print("   Link-uri: /usr/sbin/sendmail, /usr/bin/sendmail")
        print(f"   Python: {python_cmd}")
        print()
        print(">> Nota: Wrapper-ul trimite direct prin Gmail SMTP")
        print("   fara binare statice sau biblioteci externe.")
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

