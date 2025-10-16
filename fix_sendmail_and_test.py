#!/usr/bin/env python
"""
Porneste corect daemon-ul sendmail MTA si trimite email de test.
"""

import paramiko
import sys
from datetime import datetime
import time

HOST = "95.196.191.92"
USER = "root"
PASS = "bebef_999"
PORT = 22

TEST_TO = "larisbirzu@gmail.com"


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
    print("   PORNIRE SENDMAIL MTA SI TEST EMAIL")
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
        
        # 1. Opreste toate procesele sendmail
        print("=" * 70)
        print("PASUL 1: Oprire sendmail curent")
        print("=" * 70)
        
        ssh_exec(ssh, "killall sendmail 2>/dev/null || true", show=False)
        ssh_exec(ssh, "service sendmail stop 2>&1", show=False)
        time.sleep(2)
        
        print("[OK] Sendmail oprit")
        print()
        
        # 2. Porneste daemon MTA sendmail
        print("=" * 70)
        print("PASUL 2: Pornire daemon MTA sendmail")
        print("=" * 70)
        
        print("[INFO] Pornesc sendmail MTA daemon...")
        
        # Porneste daemon-ul MTA (ascult pe portul 25)
        out, _ = ssh_exec(ssh, "/usr/sbin/sendmail.sendmail -bd -q15m 2>&1", show=False)
        
        if out and "error" in out.lower():
            print(f"[WARN] {out}")
        else:
            print("[OK] Daemon MTA pornit")
        
        time.sleep(2)
        print()
        
        # 3. Verifica daca asculta pe portul 25
        print("=" * 70)
        print("PASUL 3: Verificare daemon pe portul 25")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "netstat -tln 2>/dev/null | grep ':25 ' || ss -tln 2>/dev/null | grep ':25 '", show=False)
        
        if out:
            print("[OK] Sendmail asculta pe portul 25:")
            print(out)
        else:
            print("[WARN] Nu vad sendmail pe portul 25")
            print("[INFO] Verific procese sendmail...")
            out, _ = ssh_exec(ssh, "ps aux | grep sendmail | grep -v grep", show=False)
            if out:
                print(out)
        
        print()
        
        # 4. Creaza link /usr/sbin/sendmail
        print("=" * 70)
        print("PASUL 4: Creare link sendmail")
        print("=" * 70)
        
        ssh_exec(ssh, "ln -sf /usr/sbin/sendmail.sendmail /usr/sbin/sendmail", show=False)
        print("[OK] Link creat: /usr/sbin/sendmail -> /usr/sbin/sendmail.sendmail")
        print()
        
        # 5. Test trimitere email
        print("=" * 70)
        print("TEST TRIMITERE EMAIL")
        print("=" * 70)
        print()
        
        test_msg = f"""Test email trimis la {timestamp}

Acesta este un test de trimitere prin sendmail MTA daemon.

Server: sariasi66.ro
Data: {timestamp}
Metoda: sendmail MTA daemon (port 25)

Daca primesti acest email, MTA-ul functioneaza corect!
"""
        
        escaped = test_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        cmd = f'echo "{escaped}" | /bin/mail -s "[Test MTA] Email la {timestamp}" {TEST_TO} 2>&1'
        print(f"[INFO] Trimitere email catre {TEST_TO}...")
        print()
        
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=10)
        
        if out:
            if "error" in out.lower():
                print(f"[ERROR] {out}")
            else:
                print(f"[INFO] {out}")
        else:
            print("[OK] Comanda executata! Mail trimis in coada.")
        
        print()
        
        # 6. Asteapta si verifica logs
        print("=" * 70)
        print("VERIFICARE LOGS (timp real)")
        print("=" * 70)
        print()
        print("[INFO] Astept 5 secunde pentru procesare...")
        time.sleep(5)
        
        out, _ = ssh_exec(ssh, "tail -n 50 /var/log/maillog 2>/dev/null | grep -A 2 -B 2 'larisbirzu@gmail.com' | tail -20", show=False)
        
        if out:
            print("Logs pentru emailul nostru:")
            print("-" * 70)
            lines = out.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                lw = line.lower()
                if "stat=sent" in lw or "message accepted" in lw or "250 " in line:
                    print(f"  [SUCCESS] {line}")
                elif "error" in lw or "failed" in lw or "refused" in lw or "deferred" in lw:
                    print(f"  [ERROR] {line}")
                elif TEST_TO in line:
                    print(f"  [>>>] {line}")
                else:
                    print(f"        {line}")
            print("-" * 70)
        else:
            print("[INFO] Nu am gasit inca logs pentru acest email")
        
        print()
        
        # 7. Verifica starea finala
        print("=" * 70)
        print("STATUS FINAL")
        print("=" * 70)
        print()
        
        # Verifica daca email-ul a fost trimis sau e in coada
        out, _ = ssh_exec(ssh, "tail -n 10 /var/log/maillog 2>/dev/null | grep 'stat='", show=False)
        
        if out:
            if "stat=Sent" in out:
                print("✓ [SUCCESS] Emailul a fost TRIMIS!")
                print()
                print("Verifica inbox-ul in 1-5 minute.")
            elif "Deferred" in out:
                print("! [ATENTIE] Emailul este in coada (Deferred)")
                print()
                print("Posibile cauze:")
                print("  - Server destinatie temporar indisponibil")
                print("  - Probleme DNS")
                print("  - Emailul va fi retrimis automat")
            elif "refused" in out.lower():
                print("X [EROARE] Conexiune refuzata")
                print()
                print("Problema: Serverul destinatie refuza conexiunea")
        
        print()
        print("=" * 70)
        print("INFORMATII UTILE")
        print("=" * 70)
        print()
        print(f">> Email trimis catre: {TEST_TO}")
        print()
        print(">> Pentru a trimite email manual:")
        print(f"   ssh {USER}@{HOST}")
        print(f"   echo 'Mesaj' | mail -s 'Subject' {TEST_TO}")
        print()
        print(">> Monitoring in timp real:")
        print("   tail -f /var/log/maillog")
        print()
        print(">> Verificare daemon:")
        print("   netstat -tln | grep :25")
        print("   ps aux | grep sendmail")
        print()
        print(">> Daca emailul nu ajunge:")
        print("   - Poate fi blocat de Gmail (IP blacklist, spam)")
        print("   - Poate fi in Spam/Junk")
        print("   - Domeniul nu are SPF/DKIM configurat")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("PROCES FINALIZAT!")
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

