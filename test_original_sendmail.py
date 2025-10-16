#!/usr/bin/env python
"""
Restaureaza sendmail-ul original si testeaza trimiterea de email.
"""

import paramiko
import sys
from datetime import datetime

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
    print("   RESTAURARE SI TEST SENDMAIL ORIGINAL")
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
        
        # 1. Sterge link-urile noastre
        print("=" * 70)
        print("PASUL 1: Restaurare sendmail original")
        print("=" * 70)
        
        print("[INFO] Sterg link-urile create de noi...")
        ssh_exec(ssh, "rm -f /usr/local/bin/msmtp", show=False)
        ssh_exec(ssh, "rm -f /usr/sbin/sendmail", show=False)
        ssh_exec(ssh, "rm -f /usr/bin/sendmail", show=False)
        ssh_exec(ssh, "rm -f /usr/lib/sendmail", show=False)
        
        print("[OK] Link-uri sterse")
        print()
        
        # 2. Cauta sendmail original
        print("=" * 70)
        print("PASUL 2: Cautare sendmail original")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "find /usr -name 'sendmail*' -type f 2>/dev/null | head -10", show=False)
        
        if out:
            print("[OK] Fisiere sendmail gasite:")
            print(out)
            
            # Gaseste cel mai probabil candidat
            lines = out.strip().split('\n')
            sendmail_bin = None
            
            for line in lines:
                if '/usr/sbin/' in line and '.cf' not in line and 'sendmail.sendmail' not in line:
                    sendmail_bin = line.strip()
                    break
            
            if not sendmail_bin and lines:
                sendmail_bin = lines[0].strip()
            
            if sendmail_bin:
                print(f"\n[OK] Voi folosi: {sendmail_bin}")
            else:
                print("[ERROR] Nu am gasit binar sendmail valid")
                return 1
        else:
            print("[WARN] Nu am gasit sendmail, caut alternative...")
            sendmail_bin = "/usr/sbin/sendmail.sendmail"
        
        print()
        
        # 3. Porneste serviciul sendmail daca nu ruleaza
        print("=" * 70)
        print("PASUL 3: Pornire serviciu sendmail")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "service sendmail status 2>&1 | head -3", show=False)
        print(f"Status: {out.strip()}")
        
        if "running" not in out.lower() and "pid" not in out.lower():
            print("[INFO] Pornesc sendmail...")
            ssh_exec(ssh, "service sendmail start 2>&1", show=False)
            import time
            time.sleep(2)
            print("[OK] Sendmail pornit")
        else:
            print("[OK] Sendmail deja ruleaza")
        
        print()
        
        # 4. TEST 1: Mail command simplu
        print("=" * 70)
        print("TEST 1: Comanda 'mail' (cea mai simpla)")
        print("=" * 70)
        print()
        
        test_msg = f"""Test email {timestamp}

Acesta este un test de trimitere email prin sendmail ORIGINAL.

Metoda: mail command
Server: sariasi66.ro
Data: {timestamp}

Daca primesti acest email, configurarea de baza functioneaza!
"""
        
        escaped = test_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        cmd = f'echo "{escaped}" | /bin/mail -s "[Test Original] Email la {timestamp}" {TEST_TO} 2>&1'
        print(f"[INFO] Trimitere catre {TEST_TO}...")
        print(f"[CMD] /bin/mail -s 'Subject' {TEST_TO}")
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
        
        # 5. Verifica coada mailuri
        print("=" * 70)
        print("VERIFICARE COADA MAILURI")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "mailq 2>&1 | head -15", show=False, timeout=10)
        if out:
            if "empty" in out.lower() or "mail queue is empty" in out.lower():
                print("[OK] Coada goala (mailurile au fost trimise!)")
            else:
                print("Coada actuala:")
                print(out)
        print()
        
        # 6. Verifica logs
        print("=" * 70)
        print("LOGS SENDMAIL (ultimele 40 linii)")
        print("=" * 70)
        print()
        
        import time
        print("[INFO] Astept 2 secunde pentru logs...")
        time.sleep(2)
        
        out, _ = ssh_exec(ssh, "tail -n 40 /var/log/maillog 2>/dev/null", show=False)
        
        if out:
            print("Logs recente:")
            print("-" * 70)
            lines = out.strip().split('\n')
            for line in lines[-20:]:  # Ultimele 20 linii
                if not line.strip():
                    continue
                lw = line.lower()
                if "error" in lw or "failed" in lw or "refused" in lw or "deferred" in lw:
                    print(f"  [ERR] {line}")
                elif "stat=sent" in lw or "message accepted" in lw:
                    print(f"  [OK]  {line}")
                elif "to=" + TEST_TO in lw or TEST_TO in line:
                    print(f"  [>>>] {line}")
                elif "from=" in lw or "to=" in lw:
                    print(f"  [MSG] {line}")
            print("-" * 70)
        else:
            print("[WARN] Nu am gasit logs")
        
        print()
        
        # 7. Informatii finale
        print("=" * 70)
        print("URMATOARELE PASI")
        print("=" * 70)
        print()
        print(f">> Email trimis catre: {TEST_TO}")
        print()
        print(">> Verifica:")
        print(f"   1. Inbox la {TEST_TO}")
        print("   2. Folder Spam/Junk")
        print("   3. Asteapta 2-10 minute")
        print()
        print(">> Daca NU primesti emailul:")
        print("   - Verifica logs-urile de mai sus")
        print("   - Cauta 'stat=Sent' in logs = success local")
        print("   - Cauta 'Deferred' sau 'refused' = probleme livrare")
        print()
        print(">> Pentru trimitere manuala:")
        print(f"   ssh {USER}@{HOST}")
        print(f"   echo 'Mesaj test' | mail -s 'Subject' {TEST_TO}")
        print()
        print(">> Debugging:")
        print("   tail -f /var/log/maillog  # Vezi logs in timp real")
        print("   mailq                     # Vezi coada de mailuri")
        print("   service sendmail status   # Verifica daca ruleaza")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("TEST COMPLET!")
        print("=" * 70)
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

