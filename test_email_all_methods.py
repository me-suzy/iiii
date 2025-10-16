#!/usr/bin/env python
"""
Script care testeaza TOATE metodele posibile de trimitere email pe serverul vechi.
Gaseste ce functioneaza si trimite un email de test.
"""

import paramiko
import sys
from datetime import datetime

# Configurare server
HOST = "95.196.191.92"
USER = "root"
PASS = "bebef_999"
PORT = 22

# Email test
TEST_FROM = "root@sariasi66.ro"
TEST_TO = "larisbirzu@gmail.com"


def ssh_exec(ssh, cmd, show=True, timeout=60):
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
    print("   TEST TRIMITERE EMAIL - TOATE METODELE")
    print("=" * 70)
    print()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica ce servicii SMTP ruleaza
        print("=" * 70)
        print("TEST 1: Verificare servicii email")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "ps aux | grep -E 'sendmail|postfix|exim' | grep -v grep", show=False)
        if out:
            print("[OK] Servicii gasite:")
            print(out)
        else:
            print("[WARN] Nu ruleaza servicii email standard")
        print()
        
        # 2. Verifica sendmail
        out, _ = ssh_exec(ssh, "which sendmail", show=False)
        if out.strip():
            print(f"[OK] Sendmail gasit: {out.strip()}")
        print()
        
        # 3. Test 1: Mail command (cel mai simplu)
        print("=" * 70)
        print("TEST 2: Trimitere cu comanda 'mail'")
        print("=" * 70)
        print()
        
        test_msg = f"""Test email trimis la {timestamp}

Acesta este un test automat pentru a verifica daca serverul poate trimite emailuri.

Test Method: mail command
From: {TEST_FROM}
To: {TEST_TO}

Daca primesti acest email, inseamna ca metoda functioneaza!
"""
        
        # Escapare
        escaped = test_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        cmd = f'echo "{escaped}" | mail -s "[Test 1] Mail command - {timestamp}" {TEST_TO} 2>&1'
        print(f"[INFO] Trimitere catre {TEST_TO} cu 'mail'...")
        out, _ = ssh_exec(ssh, cmd, show=False)
        
        if out:
            if "error" in out.lower() or "cannot" in out.lower():
                print(f"[ERROR] {out}")
            else:
                print(f"[INFO] Output: {out}")
        else:
            print("[OK] Comanda executata fara erori!")
        print()
        
        # 4. Test 2: Sendmail direct
        print("=" * 70)
        print("TEST 3: Trimitere cu sendmail direct")
        print("=" * 70)
        print()
        
        email_raw = f"""From: {TEST_FROM}
To: {TEST_TO}
Subject: [Test 2] Sendmail direct - {timestamp}

{test_msg}
"""
        
        escaped2 = email_raw.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        cmd = f'echo "{escaped2}" | /usr/sbin/sendmail -v {TEST_TO} 2>&1'
        print(f"[INFO] Trimitere cu /usr/sbin/sendmail...")
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=30)
        
        if out:
            print("Output sendmail:")
            print("-" * 70)
            print(out[:500])  # Primele 500 caractere
            print("-" * 70)
        print()
        
        # 5. Verifica coada de mail
        print("=" * 70)
        print("TEST 4: Verificare coada mailuri")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "mailq 2>&1 | head -20", show=False)
        if out:
            print("Coada mail:")
            print(out)
        print()
        
        # 6. Verifica logs recente
        print("=" * 70)
        print("TEST 5: Verificare logs email (ultimele 30 linii)")
        print("=" * 70)
        
        import time
        print("[INFO] Astept 3 secunde pentru logs...")
        time.sleep(3)
        
        out, _ = ssh_exec(ssh, "tail -n 30 /var/log/maillog 2>/dev/null || tail -n 30 /var/log/mail.log 2>/dev/null || echo 'Nu am gasit logs'", show=False)
        
        if out and "Nu am gasit" not in out:
            print("Logs recente:")
            print("-" * 70)
            lines = out.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                lw = line.lower()
                if "error" in lw or "failed" in lw or "refused" in lw:
                    print(f"  [ERR] {line}")
                elif "sent" in lw or "stat=sent" in lw:
                    print(f"  [OK]  {line}")
                elif "to=" in lw or "from=" in lw:
                    print(f"  [>>>] {line}")
                else:
                    print(f"       {line}")
            print("-" * 70)
        else:
            print("[WARN] Nu am gasit fisiere de log sau sunt goale")
        print()
        
        # 7. Test localhost SMTP
        print("=" * 70)
        print("TEST 6: Verificare SMTP localhost")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "netstat -tln | grep ':25' || ss -tln | grep ':25'", show=False)
        if out:
            print("[OK] SMTP server asculta pe portul 25:")
            print(out)
        else:
            print("[WARN] Nu am gasit SMTP server pe portul 25")
        print()
        
        # 8. Informatii utile
        print("=" * 70)
        print("INFORMATII SI RECOMANDARI")
        print("=" * 70)
        print()
        print(f"Am trimis 2 emailuri de test catre: {TEST_TO}")
        print()
        print(">> Verifica urmatoarele:")
        print(f"   1. Inbox-ul la {TEST_TO}")
        print("   2. Folder-ul Spam/Junk")
        print("   3. Asteapta 2-5 minute pentru livrare")
        print()
        print(">> Daca NU primesti emailurile:")
        print("   - Verifica logs-urile mai sus pentru erori")
        print("   - Serverul poate trimite local dar Gmail poate respinge")
        print("   - Motivele posibile:")
        print("     * Domeniu fara SPF/DKIM configurat")
        print("     * IP-ul serverului in blacklist")
        print("     * TLS prea vechi pentru Gmail")
        print()
        print(">> Daca PRIMESTI emailurile:")
        print("   - Foloseste comanda: echo 'Text' | mail -s 'Subject' email@domain.com")
        print("   - Sau: echo 'Text' | sendmail email@domain.com")
        print()
        print(">> Pentru debugging:")
        print(f"   ssh {USER}@{HOST}")
        print("   tail -f /var/log/maillog")
        print("   mailq  # vezi coada de mailuri")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("TEST COMPLET!")
        print("=" * 70)
        print()
        print("Verifica inbox-ul in 2-5 minute.")
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

