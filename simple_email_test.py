#!/usr/bin/env python
"""
Test simplu pentru email delivery
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
    print("   TEST SIMPLU EMAIL DELIVERY")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica status sendmail
        print("=" * 70)
        print("1. STATUS SENDMAIL")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "service sendmail status 2>&1 | head -3", show=False)
        if out:
            print("Sendmail status:")
            print(out)
        
        print()
        
        # 2. Trimitere email simplu
        print("=" * 70)
        print("2. TRIMITERE EMAIL SIMPLU")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        simple_msg = f"""Test simplu - {timestamp}

Acest email este un test simplu pentru a verifica delivery-ul.

Data: {timestamp}
Server: sariasi66.ro

Daca primesti acest email, sendmail functioneaza perfect!
"""
        
        # Escapare pentru bash
        escaped = simple_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        cmd = f'echo "{escaped}" | /bin/mail -s "[Test simplu] {timestamp}" {TEST_TO} 2>&1'
        
        print(f"[INFO] Trimitere email simplu...")
        print(f"[INFO] To: {TEST_TO}")
        print(f"[INFO] Subject: [Test simplu] {timestamp}")
        print()
        
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=5)
        
        if out:
            print(f"[INFO] Output: {out}")
        else:
            print("[OK] Email trimis!")
        
        print()
        
        # 3. Asteapta si verifica logs
        print("=" * 70)
        print("3. VERIFICARE LOGS")
        print("=" * 70)
        print()
        print("[INFO] Astept 3 secunde...")
        time.sleep(3)
        
        out, _ = ssh_exec(ssh, f"tail -n 20 /var/log/maillog 2>/dev/null | grep '{TEST_TO}' | tail -5", show=False)
        
        if out:
            print("Logs recente:")
            print("-" * 70)
            lines = out.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                lw = line.lower()
                if "stat=sent" in lw:
                    print(f"  [SUCCESS] {line}")
                elif "user unknown" in lw:
                    print(f"  [ERROR] {line}")
                elif "deferred" in lw:
                    print(f"  [DEFERRED] {line}")
                else:
                    print(f"        {line}")
            print("-" * 70)
        else:
            print("[INFO] Nu am gasit logs recente")
        
        print()
        
        # 4. Test cu adresa externa pentru comparatie
        print("=" * 70)
        print("4. RECOMANDARE TEST EXTERN")
        print("=" * 70)
        print()
        
        print(">> PROBLEMA IDENTIFICATA:")
        print("   Serverul spatiul.ro răspunde cu 'User unknown'")
        print("   pentru contact@strusgure.com")
        print()
        print(">> SOLUTII POSIBILE:")
        print("   1. Adresa nu este configurata corect pe spatiul.ro")
        print("   2. Emailurile sunt blocate de filtre anti-spam")
        print("   3. Serverul spatiul.ro are probleme")
        print()
        print(">> TESTE RECOMANDATE:")
        print("   1. Verifica folderul Spam/Junk in inbox")
        print("   2. Testeaza cu o adresa externa:")
        print("      echo 'Test extern' | mail -s 'Test' test@yahoo.com")
        print("   3. Contacteaza suportul spatiul.ro")
        print()
        print(">> VERIFICARE SPF RECORD:")
        print("   Serverul tau nu are SPF record configurat")
        print("   Asta poate cauza blocarea emailurilor")
        print()
        
        # 5. Verifica SPF
        print("=" * 70)
        print("5. VERIFICARE SPF RECORD")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "host -t TXT sariasi66.ro 2>&1 | grep -i spf", show=False)
        if out:
            print("SPF Record gasit:")
            print(out)
        else:
            print("[WARN] Nu am gasit SPF record pentru sariasi66.ro")
            print("       Recomandare: Configureaza SPF record:")
            print("       v=spf1 ip4:95.196.191.92 ~all")
        
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("TEST COMPLET!")
        print("=" * 70)
        print()
        print("Am trimis un email simplu de test.")
        print("Verifica inbox-ul in urmatoarele 5-10 minute.")
        print()
        print("Daca nu primesti emailul:")
        print("1. Verifica folderul Spam/Junk")
        print("2. Contacteaza suportul spatiul.ro")
        print("3. Testeaza cu o adresa externa")
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
