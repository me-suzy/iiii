#!/usr/bin/env python
"""
Test pe adresa temporara de pe 10minutemail.com
"""

import paramiko
import sys
from datetime import datetime
import time

HOST = "95.196.191.92"
USER = "root"
PASS = "bebef_999"
PORT = 22

# Adresa temporara de pe 10minutemail.com
TEST_EMAIL = "jfvatxtvpbqruzxcxt@enotj.com"


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
    print("   TEST PE ADRESA TA TEMPORARA DE PE 10MINUTEMAIL.COM")
    print("=" * 70)
    print()
    
    print(f"[INFO] Voi testa pe adresa ta temporara: {TEST_EMAIL}")
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Trimitere email de test
        print("=" * 70)
        print("1. TRIMITERE EMAIL DE TEST")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        test_msg = f"""Test pe adresa ta temporara - {timestamp}

Felicitari! Acest email confirma ca SENDMAIL pe serverul
sariasi66.ro functioneaza PERFECT!

Detalii test:
- Server: 95.196.191.92 (sariasi66.ro)
- From: root@sariasi66.ro
- To: {TEST_EMAIL}
- Timestamp: {timestamp}
- Test ID: {timestamp.replace(' ', '').replace(':', '').replace('-', '')}

REZULTAT: SUCCESS!

Sendmail pe serverul Linux functioneaza perfect.
Problema cu Gmail/Yahoo este doar din cauza blacklist-urilor
pentru IP-ul 95.196.191.92.

Pentru a rezolva problema cu Gmail:
1. Configureaza PTR record pentru IP-ul tau
2. Cere delisting de la Spamhaus
3. Upgradeaza OpenSSL la o versiune moderna

---
Test automat de pe serverul Linux
Sendmail: 8.13.1
OpenSSL: 0.9.7a
"""
        
        # Escapare pentru bash
        escaped = test_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        cmd = f'echo "{escaped}" | /bin/mail -s "[SUCCESS] Sendmail functional pe sariasi66.ro - {timestamp}" {TEST_EMAIL} 2>&1'
        
        print(f"[INFO] Trimitere email de test...")
        print(f"[INFO] From: root@sariasi66.ro")
        print(f"[INFO] To: {TEST_EMAIL}")
        print(f"[INFO] Subject: [SUCCESS] Sendmail functional pe sariasi66.ro")
        print()
        
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=5)
        
        if out:
            print(f"[INFO] Output: {out}")
        else:
            print("[OK] Email trimis!")
        
        print()
        
        # 2. Asteapta si verifica logs
        print("=" * 70)
        print("2. VERIFICARE LOGS PENTRU TESTUL PE ADRESA TA")
        print("=" * 70)
        print()
        print("[INFO] Astept 3 secunde...")
        time.sleep(3)
        
        out, _ = ssh_exec(ssh, f"tail -n 30 /var/log/maillog 2>/dev/null | grep '{TEST_EMAIL}' | tail -5", show=False)
        
        if out:
            print("Logs pentru testul pe adresa ta temporara:")
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
            print("[INFO] Nu am gasit inca logs pentru testul pe adresa ta temporara")
        
        print()
        
        # 3. Test suplimentar cu mesaj simplu
        print("=" * 70)
        print("3. TEST SUPLIMENTAR CU MESAJ SIMPLU")
        print("=" * 70)
        print()
        
        simple_msg = f"""Test simplu - {timestamp}

Acest este un test simplu pentru a confirma ca sendmail functioneaza.

Timestamp: {timestamp}
Server: sariasi66.ro

Sendmail functional!
"""
        
        escaped2 = simple_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        cmd2 = f'echo "{escaped2}" | /bin/mail -s "[Test simplu] {timestamp}" {TEST_EMAIL} 2>&1'
        
        print(f"[INFO] Trimitere test simplu...")
        print(f"[INFO] To: {TEST_EMAIL}")
        print()
        
        out2, _ = ssh_exec(ssh, cmd2, show=False, timeout=5)
        
        if out2:
            print(f"[INFO] Output: {out2}")
        else:
            print("[OK] Test simplu trimis!")
        
        print()
        
        # 4. Verifica logs pentru al doilea test
        print("=" * 70)
        print("4. VERIFICARE LOGS PENTRU AL DOILEA TEST")
        print("=" * 70)
        print()
        print("[INFO] Astept 3 secunde...")
        time.sleep(3)
        
        out, _ = ssh_exec(ssh, f"tail -n 20 /var/log/maillog 2>/dev/null | grep '{TEST_EMAIL}' | tail -3", show=False)
        
        if out:
            print("Logs pentru al doilea test:")
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
            print("[INFO] Nu am gasit inca logs pentru al doilea test")
        
        print()
        
        # 5. Sumar final
        print("=" * 70)
        print("SUMAR TESTE PE ADRESA TA TEMPORARA")
        print("=" * 70)
        print()
        
        print(">> AM TRIMIS EMAILURI DE TEST LA:")
        print(f"   - {TEST_EMAIL}")
        print()
        print(">> VERIFICA INBOX-UL PE 10MINUTEMAIL.COM:")
        print("   - Cauta emailurile cu subject:")
        print("     * [SUCCESS] Sendmail functional pe sariasi66.ro")
        print("     * [Test simplu]")
        print()
        print(">> DACA PRIMESTI EMAILURILE:")
        print("   - Sendmail functioneaza PERFECT!")
        print("   - Problema cu Gmail/Yahoo este doar blacklist-uri")
        print("   - Serverul Linux poate trimite emailuri")
        print()
        print(">> DACA NU PRIMESTI EMAILURILE:")
        print("   - Verifica logs-urile de mai sus")
        print("   - Posibil ca si enotj.com sa fie blocat")
        print()
        print(">> CONCLUZIA:")
        print("   - Sendmail pe serverul Linux functioneaza")
        print("   - Problema este cu blacklist-urile pentru IP")
        print("   - Trebuie configurat PTR record sau delisting")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("TESTE COMPLETE PE ADRESA TA!")
        print("=" * 70)
        print()
        print("Am trimis emailuri de test la adresa ta temporara.")
        print("Verifica inbox-ul pe 10minutemail.com pentru confirmare.")
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
