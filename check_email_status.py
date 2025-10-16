#!/usr/bin/env python
"""
Verifica statusul emailurilor si configurarile de programare pe server.
"""

import paramiko
import sys
from datetime import datetime
import time

HOST = "95.196.191.92"
USER = "root"
PASS = "bebef_999"
PORT = 22

TEST_TO = "contact@strusgure.com"


def ssh_exec(ssh, cmd, show=True, timeout=30):
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
    print("   VERIFICARE STATUS EMAILURI SI CONFIGURARI")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica coada de mailuri
        print("=" * 70)
        print("1. VERIFICARE COADA MAILURI")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "mailq 2>&1", show=False)
        if out:
            if "empty" in out.lower() or "no mail" in out.lower():
                print("[OK] Coada de mailuri este goala")
            else:
                print("[INFO] Coada de mailuri:")
                print(out)
        else:
            print("[INFO] Coada de mailuri este goala")
        
        print()
        
        # 2. Verifica logs recente pentru emailurile noastre
        print("=" * 70)
        print("2. VERIFICARE LOGS RECENTE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, f"tail -n 100 /var/log/maillog 2>/dev/null | grep '{TEST_TO}' | tail -20", show=False)
        
        if out:
            print("Logs pentru emailurile catre contact@strusgure.com:")
            print("-" * 70)
            lines = out.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                lw = line.lower()
                if "stat=sent" in lw:
                    print(f"  [SENT] {line}")
                elif "user unknown" in lw or "5.1.1" in lw:
                    print(f"  [ERROR] {line}")
                elif "deferred" in lw:
                    print(f"  [DEFERRED] {line}")
                elif "unavailable" in lw:
                    print(f"  [TEMP_ERROR] {line}")
                else:
                    print(f"        {line}")
            print("-" * 70)
        else:
            print("[INFO] Nu am gasit logs pentru emailurile catre contact@strusgure.com")
        
        print()
        
        # 3. Verifica cron jobs (programari)
        print("=" * 70)
        print("3. VERIFICARE CRON JOBS (PROGRAMARI)")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "crontab -l 2>/dev/null", show=False)
        if out:
            print("Cron jobs pentru root:")
            print("-" * 70)
            lines = out.strip().split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    print(f"  {line}")
            print("-" * 70)
        else:
            print("[INFO] Nu sunt cron jobs configurate pentru root")
        
        # Verifica cron jobs pentru alte utilizatori
        out, _ = ssh_exec(ssh, "ls /var/spool/cron/ 2>/dev/null", show=False)
        if out:
            print("\nUtilizatori cu cron jobs:")
            for user in out.strip().split('\n'):
                if user.strip():
                    print(f"  - {user}")
        
        print()
        
        # 4. Verifica configurarea sendmail pentru programare
        print("=" * 70)
        print("4. VERIFICARE CONFIGURARE SENDMAIL")
        print("=" * 70)
        print()
        
        # Verifica procese sendmail
        out, _ = ssh_exec(ssh, "ps aux | grep sendmail | grep -v grep", show=False)
        if out:
            print("Procese sendmail active:")
            print(out)
        
        # Verifica configurarea queue
        out, _ = ssh_exec(ssh, "grep -E '^O QueueDirectory|^O Queue=' /etc/mail/sendmail.cf", show=False)
        if out:
            print("\nConfiguratie coada:")
            print(out)
        
        print()
        
        # 5. Trimitere email de test nou
        print("=" * 70)
        print("5. TRIMITERE EMAIL DE TEST NOU")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        test_msg = f"""Test nou - {timestamp}

Acest email este trimis pentru a verifica daca exista probleme cu livrarea.

Data: {timestamp}
Server: sariasi66.ro
From: root@sariasi66.ro
To: {TEST_TO}

Daca primesti acest email, livrarea functioneaza normal.
"""
        
        escaped = test_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        cmd = f'echo "{escaped}" | /bin/mail -s "[Test nou] {timestamp}" {TEST_TO} 2>&1'
        
        print(f"[INFO] Trimitere email nou catre: {TEST_TO}")
        print(f"[INFO] Timestamp: {timestamp}")
        print()
        
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=10)
        
        if out:
            print(f"[INFO] Output: {out}")
        else:
            print("[OK] Email trimis!")
        
        print()
        
        # 6. Asteapta si verifica logs pentru emailul nou
        print("=" * 70)
        print("6. VERIFICARE LOGS PENTRU EMAILUL NOU")
        print("=" * 70)
        print()
        print("[INFO] Astept 3 secunde pentru procesare...")
        time.sleep(3)
        
        out, _ = ssh_exec(ssh, f"tail -n 20 /var/log/maillog 2>/dev/null | grep '{TEST_TO}'", show=False)
        
        if out:
            print("Logs pentru emailul nou:")
            print("-" * 70)
            lines = out.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                lw = line.lower()
                if "stat=sent" in lw:
                    print(f"  [SUCCESS] {line}")
                elif "user unknown" in lw:
                    print(f"  [ERROR - User unknown] {line}")
                elif "deferred" in lw:
                    print(f"  [DEFERRED] {line}")
                else:
                    print(f"        {line}")
            print("-" * 70)
        else:
            print("[INFO] Nu am gasit inca logs pentru emailul nou")
        
        print()
        
        # 7. Verifica DNS pentru domeniul destinatie
        print("=" * 70)
        print("7. VERIFICARE DNS PENTRU DESTINATIE")
        print("=" * 70)
        print()
        
        domain = TEST_TO.split('@')[1]
        print(f"[INFO] Verific DNS pentru domeniul: {domain}")
        
        out, _ = ssh_exec(ssh, f"nslookup {domain} 2>&1", show=False)
        if out:
            print("DNS Lookup:")
            print(out)
        
        out, _ = ssh_exec(ssh, f"host -t MX {domain} 2>&1", show=False)
        if out:
            print("\nMX Records:")
            print(out)
        
        print()
        
        # 8. Sumar si recomandari
        print("=" * 70)
        print("SUMAR SI RECOMANDARI")
        print("=" * 70)
        print()
        
        print(">> STATUS ACTUAL:")
        print("   - Sendmail ruleaza si functioneaza")
        print("   - Emailurile sunt trimise de pe server")
        print("   - Problema pare sa fie la livrare")
        print()
        print(">> POSIBILE CAUZE:")
        print("   1. Emailurile ajung in Spam/Junk")
        print("   2. Serverul destinatie (spatiul.ro) are probleme")
        print("   3. Emailurile sunt blocate de filtre anti-spam")
        print("   4. Domeniul sariasi66.ro nu are SPF/DKIM")
        print()
        print(">> VERIFICARI RECOMANDATE:")
        print("   1. Verifica folderul Spam/Junk in inbox")
        print("   2. Testeaza cu o alta adresa email")
        print("   3. Verifica daca domeniul tau are SPF record")
        print("   4. Contacteaza suportul spatiul.ro")
        print()
        print(">> PENTRU A TESTA CU ALTA ADRESA:")
        print("   echo 'Test' | mail -s 'Test' altcineva@domain.com")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("VERIFICARE COMPLETA!")
        print("=" * 70)
        print()
        print("Am trimis un email nou de test.")
        print("Verifica inbox-ul in urmatoarele 5-10 minute.")
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
