#!/usr/bin/env python
"""
Debug email delivery pentru contact@strusgure.com
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
    print("   DEBUG EMAIL DELIVERY - contact@strusgure.com")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica daca serverul destinatie este accesibil
        print("=" * 70)
        print("1. VERIFICARE CONECTIVITATE LA SERVERUL DESTINATIE")
        print("=" * 70)
        print()
        
        print("[INFO] Testez conectivitatea la mail.strusgure.com...")
        out, _ = ssh_exec(ssh, "telnet mail.strusgure.com 25 2>&1 | head -5", show=False)
        if out:
            print("Telnet la portul 25:")
            print(out)
        
        print("\n[INFO] Testez conectivitatea la mx1.spatiul.ro...")
        out, _ = ssh_exec(ssh, "telnet mx1.spatiul.ro 25 2>&1 | head -5", show=False)
        if out:
            print("Telnet la mx1.spatiul.ro:")
            print(out)
        
        print()
        
        # 2. Verifica DNS pentru serverul de mail
        print("=" * 70)
        print("2. VERIFICARE DNS PENTRU SERVERUL DE MAIL")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "nslookup mail.strusgure.com 2>&1", show=False)
        if out:
            print("DNS pentru mail.strusgure.com:")
            print(out)
        
        print()
        
        # 3. Trimitere email cu headers verbose
        print("=" * 70)
        print("3. TRIMITERE EMAIL CU HEADERS VERBOSE")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Creez un email cu headers verbose pentru debug
        test_msg = f"""From: root@sariasi66.ro
To: {TEST_TO}
Subject: [DEBUG] Test email delivery - {timestamp}
Date: {datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0200')}
Message-ID: <debug-{timestamp.replace(' ', '').replace(':', '').replace('-', '')}@sariasi66.ro>
X-Mailer: Sendmail Debug Test
X-Priority: 3
Content-Type: text/plain; charset=UTF-8

Test email pentru debug delivery.

Timestamp: {timestamp}
Server: sariasi66.ro
From: root@sariasi66.ro
To: {TEST_TO}

Acest email contine headers verbose pentru debug.
Daca primesti acest email, delivery-ul functioneaza.

---
Debug Test
"""
        
        # Salvez mesajul intr-un fisier temporar
        escaped = test_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        # Creez fisierul temporar
        cmd1 = f'cat > /tmp/debug_email.txt << "EOF"\n{escaped}\nEOF'
        ssh_exec(ssh, cmd1, show=False)
        
        # Trimit emailul folosind fisierul
        cmd2 = f'/bin/sendmail -v {TEST_TO} < /tmp/debug_email.txt 2>&1'
        
        print(f"[INFO] Trimitere email cu headers verbose...")
        print(f"[INFO] To: {TEST_TO}")
        print(f"[INFO] From: root@sariasi66.ro")
        print()
        
        out, _ = ssh_exec(ssh, cmd2, show=False, timeout=15)
        
        if out:
            print("Output verbose:")
            print("-" * 70)
            print(out)
            print("-" * 70)
        else:
            print("[OK] Email trimis cu verbose!")
        
        print()
        
        # 4. Asteapta si verifica logs
        print("=" * 70)
        print("4. VERIFICARE LOGS PENTRU EMAILUL DEBUG")
        print("=" * 70)
        print()
        print("[INFO] Astept 5 secunde pentru procesare...")
        time.sleep(5)
        
        out, _ = ssh_exec(ssh, f"tail -n 50 /var/log/maillog 2>/dev/null | grep -E '(debug|{TEST_TO})' | tail -10", show=False)
        
        if out:
            print("Logs pentru emailul debug:")
            print("-" * 70)
            lines = out.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                lw = line.lower()
                if "stat=sent" in lw:
                    print(f"  [SUCCESS] {line}")
                elif "user unknown" in lw or "5.1.1" in lw:
                    print(f"  [ERROR - User unknown] {line}")
                elif "deferred" in lw:
                    print(f"  [DEFERRED] {line}")
                elif "temp" in lw:
                    print(f"  [TEMP_ERROR] {line}")
                else:
                    print(f"        {line}")
            print("-" * 70)
        else:
            print("[INFO] Nu am gasit inca logs pentru emailul debug")
        
        print()
        
        # 5. Verifica daca sunt probleme cu SPF sau alte filtre
        print("=" * 70)
        print("5. VERIFICARE POSIBILE PROBLEME")
        print("=" * 70)
        print()
        
        # Verifica daca domeniul sursa are SPF record
        print("[INFO] Verific SPF record pentru sariasi66.ro...")
        out, _ = ssh_exec(ssh, "host -t TXT sariasi66.ro 2>&1 | grep -i spf", show=False)
        if out:
            print("SPF Record:")
            print(out)
        else:
            print("[WARN] Nu am gasit SPF record pentru sariasi66.ro")
            print("       Asta poate cauza blocarea emailurilor ca spam")
        
        print()
        
        # 6. Test cu o adresa externa pentru comparatie
        print("=" * 70)
        print("6. RECOMANDARE TEST EXTERN")
        print("=" * 70)
        print()
        
        print(">> PENTRU A TESTA DACA PROBLEMA ESTE CU SPATIUL.RO:")
        print("   Testeaza cu o adresa externa (Yahoo, Gmail, Outlook)")
        print()
        print(">> COMENZI PENTRU TEST:")
        print("   echo 'Test extern' | mail -s 'Test' test@yahoo.com")
        print("   echo 'Test extern' | mail -s 'Test' test@gmail.com")
        print()
        print(">> DACA EMAILURILE EXTERNE MERG:")
        print("   - Problema este cu serverul spatiul.ro")
        print("   - Contacteaza suportul spatiul.ro")
        print()
        print(">> DACA EMAILURILE EXTERNE NU MERG:")
        print("   - Problema este cu serverul tau Linux")
        print("   - Trebuie configurat SPF record")
        print()
        
        # 7. Curatare fisier temporar
        ssh_exec(ssh, "rm -f /tmp/debug_email.txt", show=False)
        
        print("=" * 70)
        print("DEBUG COMPLET!")
        print("=" * 70)
        print()
        print("Am trimis un email cu headers verbose pentru debug.")
        print("Verifica inbox-ul in urmatoarele 5-10 minute.")
        print()
        print("Daca inca nu primesti emailuri, problema este probabil:")
        print("1. Emailurile sunt blocate de filtre anti-spam")
        print("2. Serverul spatiul.ro are probleme")
        print("3. Lipseste SPF record pentru domeniul tau")
        print()
        
        ssh.close()
        
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
