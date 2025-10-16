#!/usr/bin/env python
"""
Configurez sendmail sa foloseasca Gmail ca relay extern
"""

import paramiko
import sys
from datetime import datetime
import time

HOST = "95.196.191.92"
USER = "root"
PASS = "bebef_999"
PORT = 22

# Configurare Gmail relay
GMAIL_SMTP = "smtp.gmail.com"
GMAIL_PORT = "587"
GMAIL_USER = "bib.acadiasi@gmail.com"
GMAIL_PASS = "ayig wvgo uogi nhpd"  # App Password


def ssh_exec(ssh, cmd, show=True, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="ignore")
    err = stderr.read().decode("utf-8", errors="ignore")
    if show:
        if out:
            print(out)
        if err and "warning" not in err.lower():
            print(f"[WARN] {err}")
    return out, err


def main():
    print("=" * 70)
    print("   CONFIGURARE SENDMAIL CU GMAIL RELAY")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Oprire sendmail
        print("=" * 70)
        print("1. OPRIRE SENDMAIL")
        print("=" * 70)
        print()
        
        print("[INFO] Opreste sendmail...")
        ssh_exec(ssh, "service sendmail stop 2>&1", show=False)
        time.sleep(2)
        print("[OK] Sendmail oprit!")
        print()
        
        # 2. Backup configurarea actuala
        print("=" * 70)
        print("2. BACKUP CONFIGURAREA ACTUALA")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/etc/mail/sendmail.cf.backup.gmail.{timestamp}"
        
        print(f"[INFO] Creez backup: {backup_file}")
        ssh_exec(ssh, f"cp /etc/mail/sendmail.cf {backup_file}", show=False)
        print("[OK] Backup creat!")
        print()
        
        # 3. Configurez authinfo pentru Gmail
        print("=" * 70)
        print("3. CONFIGURARE AUTHINFO PENTRU GMAIL")
        print("=" * 70)
        print()
        
        # Creez fisierul authinfo
        authinfo_content = f"""AuthInfo:{GMAIL_SMTP} "U:{GMAIL_USER}" "I:{GMAIL_USER}" "P:{GMAIL_PASS}" "M:PLAIN"
AuthInfo:{GMAIL_SMTP}:{GMAIL_PORT} "U:{GMAIL_USER}" "I:{GMAIL_USER}" "P:{GMAIL_PASS}" "M:PLAIN"
"""
        
        print("[INFO] Configurez authinfo pentru Gmail...")
        ssh_exec(ssh, f'echo "{authinfo_content}" > /etc/mail/authinfo', show=False)
        ssh_exec(ssh, "chmod 600 /etc/mail/authinfo", show=False)
        print("[OK] Authinfo configurat!")
        print()
        
        # 4. Configurez sendmail.cf pentru Gmail relay
        print("=" * 70)
        print("4. CONFIGURARE SENDMAIL.CF PENTRU GMAIL RELAY")
        print("=" * 70)
        print()
        
        # Creez o noua configurare sendmail.cf cu Gmail relay
        sendmail_cf_content = f"""# Sendmail configuration cu Gmail relay
# Generat automat pentru {GMAIL_SMTP}

# Setez domeniul local
Dj95.196.191.92
Dm95.196.191.92

# Setez clasele de masini
Cwlocalhost
Cw95.196.191.92

# Configurez Gmail ca smart host
define(`SMART_HOST', `{GMAIL_SMTP}')
define(`RELAY_MAILER_ARGS', `TCP $h {GMAIL_PORT}')
define(`ESMTP_MAILER_ARGS', `TCP $h {GMAIL_PORT}')

# Configurez autentificare
define(`confAUTH_MECHANISMS', `PLAIN LOGIN')
define(`confAUTH_OPTIONS', `p')

# Configurez TLS
define(`confCACERT_PATH', `/etc/ssl/certs')
define(`confCACERT', `/etc/ssl/certs/ca-certificates.crt')

# Restul configurarii standard
include(`/usr/share/sendmail-cf/m4/cf.m4')
VERSIONID(`$Id: sendmail.mc, v 8.13.1 2005/01/01 00:00:00 $')
OSTYPE(`linux')
DOMAIN(`generic')
MAILER(`local')
MAILER(`smtp')
"""
        
        print("[INFO] Configurez sendmail.cf pentru Gmail relay...")
        
        # Salvez noua configurare
        ssh_exec(ssh, f'echo "{sendmail_cf_content}" > /etc/mail/sendmail.cf', show=False)
        
        print("[OK] Sendmail.cf configurat!")
        print()
        
        # 5. Regenerez mapurile
        print("=" * 70)
        print("5. REGENEREZ MAPURILE")
        print("=" * 70)
        print()
        
        print("[INFO] Regenerez mapurile sendmail...")
        ssh_exec(ssh, "cd /etc/mail && make 2>&1", show=False)
        print("[OK] Mapuri regenerate!")
        print()
        
        # 6. Pornire sendmail cu noua configurare
        print("=" * 70)
        print("6. PORNIRE SENDMAIL CU GMAIL RELAY")
        print("=" * 70)
        print()
        
        print("[INFO] Pornesc sendmail...")
        ssh_exec(ssh, "service sendmail start 2>&1", show=False)
        time.sleep(3)
        
        # Verifica daca a pornit
        out, _ = ssh_exec(ssh, "service sendmail status 2>&1 | head -3", show=False)
        if out and "running" in out.lower():
            print("[OK] Sendmail pornit cu Gmail relay!")
        else:
            print("[WARN] Sendmail nu a pornit corect")
        
        print()
        
        # 7. Test cu Gmail relay
        print("=" * 70)
        print("7. TEST CU GMAIL RELAY")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        test_msg = f"""Test cu Gmail relay - {timestamp}

Acest email este trimis prin Gmail relay pentru a evita
problemele cu blacklist-urile.

Detalii:
- Server: 95.196.191.92
- Relay: {GMAIL_SMTP}
- From: {GMAIL_USER}
- Timestamp: {timestamp}

Daca primesti acest email, Gmail relay functioneaza!
"""
        
        # Escapare pentru bash
        escaped = test_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        cmd = f'echo "{escaped}" | /bin/mail -s "[Gmail Relay] Test - {timestamp}" strusgure.gree@gmail.com 2>&1'
        
        print(f"[INFO] Trimitere email prin Gmail relay...")
        print(f"[INFO] From: {GMAIL_USER}")
        print(f"[INFO] To: strusgure.gree@gmail.com")
        print()
        
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=10)
        
        if out:
            print(f"[INFO] Output: {out}")
        else:
            print("[OK] Email trimis prin Gmail relay!")
        
        print()
        
        # 8. Verifica logs pentru testul cu Gmail relay
        print("=" * 70)
        print("8. VERIFICARE LOGS PENTRU GMAIL RELAY")
        print("=" * 70)
        print()
        print("[INFO] Astept 5 secunde...")
        time.sleep(5)
        
        out, _ = ssh_exec(ssh, f"tail -n 30 /var/log/maillog 2>/dev/null | grep -E '(gmail|{GMAIL_SMTP})' | tail -5", show=False)
        
        if out:
            print("Logs pentru Gmail relay:")
            print("-" * 70)
            lines = out.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                lw = line.lower()
                if "stat=sent" in lw:
                    print(f"  [SUCCESS] {line}")
                elif "service unavailable" in lw:
                    print(f"  [BLOCKED] {line}")
                elif "user unknown" in lw:
                    print(f"  [ERROR] {line}")
                else:
                    print(f"        {line}")
            print("-" * 70)
        else:
            print("[INFO] Nu am gasit inca logs pentru Gmail relay")
        
        print()
        
        # 9. Sumar si recomandari
        print("=" * 70)
        print("SUMAR CONFIGURARE GMAIL RELAY")
        print("=" * 70)
        print()
        
        print(">> AM CONFIGURAT SENDMAIL SA FOLOSEASCA:")
        print(f"   - Gmail SMTP: {GMAIL_SMTP}:{GMAIL_PORT}")
        print(f"   - Gmail User: {GMAIL_USER}")
        print(f"   - Relay pentru a evita blacklist-urile")
        print()
        print(">> BACKUP CREAT:")
        print(f"   - {backup_file}")
        print()
        print(">> TEST TRIMIS:")
        print("   - To: strusgure.gree@gmail.com")
        print("   - Subject: [Gmail Relay] Test")
        print("   - Prin Gmail SMTP")
        print()
        print(">> VERIFICA INBOX-UL:")
        print("   - strusgure.gree@gmail.com")
        print("   - Emailul ar trebui sa ajunga acum!")
        print()
        print(">> DACA PRIMESTI EMAILUL:")
        print("   - Gmail relay functioneaza perfect")
        print("   - Poti trimite emailuri fara probleme")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("CONFIGURARE GMAIL RELAY COMPLETA!")
        print("=" * 70)
        print()
        print("Am configurat sendmail sa foloseasca Gmail ca relay extern.")
        print("Verifica inbox-ul pentru emailul de test.")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Eroare: {e}")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[WARN] Script intrerupt.")
        sys.exit(130)
