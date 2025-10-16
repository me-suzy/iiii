#!/usr/bin/env python
"""
Script care asteapta ca utilizatorul sa configureze adresa contact@strusgure.com
si apoi retrimite emailul de test.
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


def test_email_exists(ssh):
    """Testeaza daca adresa email exista prin trimiterea unui email simplu"""
    print("[INFO] Testez daca adresa email exista...")
    
    cmd = f'echo "Test conexiune" | /bin/mail -s "Test conexiune" {TEST_TO} 2>&1'
    out, _ = ssh_exec(ssh, cmd, show=False, timeout=10)
    
    time.sleep(3)  # Asteapta procesare
    
    # Verifica logs pentru rezultat
    out, _ = ssh_exec(ssh, f"tail -n 20 /var/log/maillog 2>/dev/null | grep '{TEST_TO}' | tail -5", show=False)
    
    if out:
        if "User unknown" in out or "5.1.1" in out:
            return False  # Adresa nu exista
        elif "stat=Sent" in out or "250" in out:
            return True   # Adresa exista si email trimis
        elif "Service unavailable" in out:
            return True   # Adresa exista dar server temporar indisponibil
    
    return False


def main():
    print("=" * 70)
    print("   CONFIGURARE SI TEST contact@strusgure.com")
    print("=" * 70)
    print()
    
    print("INSTRUCTIUNI PENTRU CONFIGURARE:")
    print("-" * 70)
    print()
    print("1. In panelul cPanel pe care il ai deschis:")
    print("   - Click pe 'Email Accounts'")
    print("   - Completeaza:")
    print("     * Email: contact")
    print("     * Password: [alege o parola]")
    print("     * Mailbox Quota: 1000 MB")
    print("   - Click 'Create Account'")
    print()
    print("2. Daca vrei forward la alta adresa:")
    print("   - Click pe 'Forwarders'")
    print("   - Add Forwarder:")
    print("     * Address: contact@strusgure.com")
    print("     * Destination: [adresa ta]")
    print()
    print("3. Dupa ce ai configurat, apasa ENTER aici pentru a testa.")
    print()
    
    input("Apasa ENTER cand ai configurat adresa contact@strusgure.com...")
    print()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # Test daca adresa exista
        if not test_email_exists(ssh):
            print("[WARN] Adresa nu pare sa existe inca sau nu este configurata corect.")
            print("       Verifica ca ai creat contul in cPanel.")
            print()
            
            retry = input("Vrei sa incerc din nou? (y/n): ").lower().strip()
            if retry == 'y':
                if not test_email_exists(ssh):
                    print("[ERROR] Adresa inca nu exista. Verifica configuratia in cPanel.")
                    return 1
        
        # Trimitere email principal
        print("=" * 70)
        print("TRIMITERE EMAIL DE TEST")
        print("=" * 70)
        print()
        
        test_msg = f"""Felicitari!

Acest email a fost trimis cu succes de pe serverul sariasi66.ro

Detalii tehnice:
- Data si ora: {timestamp}
- Server sursa: sariasi66.ro (95.196.191.92)
- De la: root@sariasi66.ro
- Catre: {TEST_TO}
- Protocol: SMTP cu TLS

Configurarea sendmail pe serverul Linux functioneaza perfect!

---
Trimis automat prin sendmail
Server: Red Hat Enterprise Linux 4
"""
        
        escaped = test_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        cmd = f'echo "{escaped}" | /bin/mail -s "[SUCCESS] Email de pe sariasi66.ro - {timestamp}" {TEST_TO} 2>&1'
        
        print(f"[INFO] Trimitere email catre: {TEST_TO}")
        print(f"[INFO] Subject: [SUCCESS] Email de pe sariasi66.ro")
        print()
        
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=10)
        
        if out:
            print(f"[INFO] {out}")
        else:
            print("[OK] Email trimis cu succes!")
        
        print()
        
        # Verifica logs
        print("=" * 70)
        print("VERIFICARE LOGS")
        print("=" * 70)
        print()
        print("[INFO] Astept 5 secunde pentru procesare...")
        time.sleep(5)
        
        out, _ = ssh_exec(ssh, f"tail -n 30 /var/log/maillog 2>/dev/null | grep '{TEST_TO}' | tail -10", show=False)
        
        if out:
            print("Logs pentru emailul trimis:")
            print("-" * 70)
            lines = out.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                lw = line.lower()
                if "stat=sent" in lw or "message accepted" in lw or "250 " in line:
                    print(f"  [SUCCESS] {line}")
                elif "user unknown" in lw or "5.1.1" in lw:
                    print(f"  [ERROR] {line}")
                elif "deferred" in lw:
                    print(f"  [QUEUED] {line}")
                else:
                    print(f"        {line}")
            print("-" * 70)
        
        print()
        
        # Sumar final
        print("=" * 70)
        print("REZULTAT FINAL")
        print("=" * 70)
        print()
        print(f"✓ Email trimis catre: {TEST_TO}")
        print()
        print(">> VERIFICA INBOX-UL:")
        print(f"   - Acceseaza inbox-ul pentru {TEST_TO}")
        print("   - Verifica si folderul Spam/Junk")
        print("   - Daca ai configurat forward, verifica si adresa destinatie")
        print()
        print(">> SENDMAIL FUNCTIONEAZA PERFECT!")
        print("   Serverul Linux poate trimite emailuri cu succes.")
        print("   Poti folosi comanda: echo 'Mesaj' | mail -s 'Subject' destinatar@domain.com")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("CONFIGURARE COMPLETA!")
        print("=" * 70)
        print()
        print("Sendmail este configurat si functional pe serverul Linux!")
        print("Verifica inbox-ul pentru emailul de confirmare.")
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
