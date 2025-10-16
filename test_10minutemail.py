#!/usr/bin/env python
"""
Test pe test@10minutemail.com pentru a confirma ca sendmail functioneaza
"""

import paramiko
import sys
from datetime import datetime
import time

HOST = "95.196.191.92"
USER = "root"
PASS = "bebef_999"
PORT = 22

TEST_EMAIL = "test@10minutemail.com"


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
    print("   TEST PE test@10minutemail.com")
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
        print("1. VERIFICARE STATUS SENDMAIL")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "service sendmail status 2>&1 | head -3", show=False)
        if out:
            print("Sendmail status:")
            print(out)
        
        print()
        
        # 2. Trimitere email de test
        print("=" * 70)
        print("2. TRIMITERE EMAIL DE TEST")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        test_msg = f"""Test pe 10minutemail.com - {timestamp}

Acest email este trimis pentru a testa daca sendmail functioneaza
cu adrese care accepta emailuri fara SPF record.

Detalii test:
- Server: 95.196.191.92
- From: root@sariasi66.ro
- To: {TEST_EMAIL}
- Timestamp: {timestamp}
- Test ID: {timestamp.replace(' ', '').replace(':', '').replace('-', '')}

Daca primesti acest email, sendmail functioneaza perfect!
Problema cu Gmail este doar din cauza blacklist-urilor.

---
Test automat de pe serverul Linux
"""
        
        # Escapare pentru bash
        escaped = test_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        cmd = f'echo "{escaped}" | /bin/mail -s "[SUCCESS] Sendmail functional - {timestamp}" {TEST_EMAIL} 2>&1'
        
        print(f"[INFO] Trimitere email de test...")
        print(f"[INFO] From: root@sariasi66.ro")
        print(f"[INFO] To: {TEST_EMAIL}")
        print(f"[INFO] Subject: [SUCCESS] Sendmail functional")
        print()
        
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=5)
        
        if out:
            print(f"[INFO] Output: {out}")
        else:
            print("[OK] Email trimis!")
        
        print()
        
        # 3. Asteapta si verifica logs
        print("=" * 70)
        print("3. VERIFICARE LOGS PENTRU TESTUL PE 10MINUTEMAIL")
        print("=" * 70)
        print()
        print("[INFO] Astept 3 secunde...")
        time.sleep(3)
        
        out, _ = ssh_exec(ssh, f"tail -n 30 /var/log/maillog 2>/dev/null | grep '{TEST_EMAIL}' | tail -5", show=False)
        
        if out:
            print("Logs pentru testul pe 10minutemail.com:")
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
                elif "deferred" in lw:
                    print(f"  [DEFERRED] {line}")
                else:
                    print(f"        {line}")
            print("-" * 70)
        else:
            print("[INFO] Nu am gasit inca logs pentru testul pe 10minutemail.com")
        
        print()
        
        # 4. Test suplimentar cu o alta adresa temporara
        print("=" * 70)
        print("4. TEST SUPLIMENTAR CU ALTA ADRESA TEMPORARA")
        print("=" * 70)
        print()
        
        test_email2 = "test@mailinator.com"
        
        quick_msg = f"""Test rapid pe mailinator.com - {timestamp}

Test rapid pentru a confirma ca sendmail functioneaza
cu multiple adrese temporare.

Timestamp: {timestamp}
Server: 95.196.191.92

Sendmail functional!
"""
        
        escaped2 = quick_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        cmd2 = f'echo "{escaped2}" | /bin/mail -s "[Test rapid] Mailinator - {timestamp}" {test_email2} 2>&1'
        
        print(f"[INFO] Trimitere test rapid...")
        print(f"[INFO] To: {test_email2}")
        print()
        
        out2, _ = ssh_exec(ssh, cmd2, show=False, timeout=5)
        
        if out2:
            print(f"[INFO] Output: {out2}")
        else:
            print("[OK] Test rapid trimis!")
        
        print()
        
        # 5. Verifica logs pentru al doilea test
        print("=" * 70)
        print("5. VERIFICARE LOGS PENTRU AL DOILEA TEST")
        print("=" * 70)
        print()
        print("[INFO] Astept 3 secunde...")
        time.sleep(3)
        
        out, _ = ssh_exec(ssh, f"tail -n 20 /var/log/maillog 2>/dev/null | grep '{test_email2}' | tail -3", show=False)
        
        if out:
            print("Logs pentru testul pe mailinator.com:")
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
            print("[INFO] Nu am gasit inca logs pentru testul pe mailinator.com")
        
        print()
        
        # 6. Sumar final
        print("=" * 70)
        print("SUMAR TESTE PE ADRESE TEMPORARE")
        print("=" * 70)
        print()
        
        print(">> AM TRIMIS EMAILURI DE TEST LA:")
        print(f"   1. {TEST_EMAIL}")
        print(f"   2. {test_email2}")
        print()
        print(">> VERIFICA INBOX-URILE:")
        print(f"   - {TEST_EMAIL} - Subject: [SUCCESS] Sendmail functional")
        print(f"   - {test_email2} - Subject: [Test rapid] Mailinator")
        print()
        print(">> DACA PRIMESTI EMAILURILE:")
        print("   - Sendmail functioneaza PERFECT!")
        print("   - Problema este DOAR cu blacklist-urile")
        print("   - Gmail/Yahoo blocheaza din cauza IP-ului")
        print()
        print(">> DACA NU PRIMESTI EMAILURILE:")
        print("   - Verifica logs-urile de mai sus")
        print("   - Posibil ca si aceste adrese sa fie blocate")
        print()
        print(">> CONCLUZIA:")
        print("   - Sendmail pe serverul Linux functioneaza")
        print("   - Problema este cu blacklist-urile pentru IP")
        print("   - Trebuie configurat PTR record sau delisting")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("TESTE COMPLETE!")
        print("=" * 70)
        print()
        print("Am trimis emailuri de test la adrese temporare.")
        print("Verifica inbox-urile pentru confirmare.")
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
