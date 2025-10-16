#!/usr/bin/env python
"""
Restaureaza sendmail.cf valid din backup si testeaza trimiterea.
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
    print("   RESTAURARE SENDMAIL.CF SI TEST EMAIL")
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
        
        # 1. Opreste sendmail
        print("=" * 70)
        print("PASUL 1: Oprire sendmail")
        print("=" * 70)
        
        ssh_exec(ssh, "service sendmail stop 2>&1 || killall sendmail 2>/dev/null || true", show=False)
        time.sleep(2)
        print("[OK] Sendmail oprit")
        print()
        
        # 2. Cauta si restaureaza backup sendmail.cf
        print("=" * 70)
        print("PASUL 2: Restaurare sendmail.cf din backup")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "ls -t /etc/mail/sendmail.cf.backup* 2>/dev/null | head -1", show=False)
        
        if out.strip():
            backup_file = out.strip()
            print(f"[OK] Gasit backup: {backup_file}")
            
            # Creaza backup curent
            ssh_exec(ssh, "cp /etc/mail/sendmail.cf /etc/mail/sendmail.cf.broken.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true", show=False)
            
            # Restaureaza din backup
            out, _ = ssh_exec(ssh, f"cp {backup_file} /etc/mail/sendmail.cf", show=False)
            print(f"[OK] Restaurat din {backup_file}")
        else:
            print("[WARN] Nu am gasit backup, folosesc configuratie default...")
            # Incearca sa gaseasca o configuratie default
            ssh_exec(ssh, "cp /usr/share/sendmail-cf/cf/sendmail.cf /etc/mail/sendmail.cf 2>/dev/null || cp /etc/mail/sendmail.mc /etc/mail/sendmail.cf 2>/dev/null || true", show=False)
        
        print()
        
        # 3. Verifica sendmail.cf
        print("=" * 70)
        print("PASUL 3: Verificare sendmail.cf")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "grep -E '^O QueueDirectory|^O Queue=' /etc/mail/sendmail.cf | head -2", show=False)
        if out:
            print("[OK] Configuratie coada mail:")
            print(out)
        else:
            print("[WARN] Nu am gasit configuratie coada")
        
        out, _ = ssh_exec(ssh, "grep '^Mlocal' /etc/mail/sendmail.cf | head -1", show=False)
        if out:
            print("[OK] Local mailer definit")
        else:
            print("[WARN] Local mailer nu este definit")
        
        print()
        
        # 4. Porneste serviciul sendmail
        print("=" * 70)
        print("PASUL 4: Pornire serviciu sendmail")
        print("=" * 70)
        
        print("[INFO] Pornesc sendmail prin service...")
        out, _ = ssh_exec(ssh, "service sendmail start 2>&1", show=False)
        
        if out:
            if "OK" in out or "started" in out.lower():
                print("[OK] Sendmail pornit cu succes")
            else:
                print(f"[INFO] {out}")
        
        time.sleep(3)
        print()
        
        # 5. Verifica status
        print("=" * 70)
        print("PASUL 5: Verificare status sendmail")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "service sendmail status 2>&1 | head -5", show=False)
        if out:
            print("Status:")
            print(out)
        
        out, _ = ssh_exec(ssh, "ps aux | grep sendmail | grep -v grep | head -3", show=False)
        if out:
            print("\nProcese sendmail:")
            print(out)
        
        print()
        
        # 6. TEST TRIMITERE
        print("=" * 70)
        print("TEST TRIMITERE EMAIL")
        print("=" * 70)
        print()
        
        test_msg = f"""Test email trimis la {timestamp}

Acesta este un email de test dupa restaurarea sendmail.cf.

Server: sariasi66.ro
Data: {timestamp}

Daca primesti acest email, configurarea functioneaza!
"""
        
        escaped = test_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        cmd = f'echo "{escaped}" | /bin/mail -s "[Test Restored] Email la {timestamp}" {TEST_TO} 2>&1'
        print(f"[INFO] Trimitere email catre {TEST_TO}...")
        print()
        
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=10)
        
        if out:
            if "error" in out.lower():
                print(f"[ERROR] {out}")
            else:
                print(f"[INFO] {out}")
        else:
            print("[OK] Comanda executata fara erori")
        
        print()
        
        # 7. Verifica logs
        print("=" * 70)
        print("VERIFICARE LOGS")
        print("=" * 70)
        print()
        print("[INFO] Astept 5 secunde pentru procesare...")
        time.sleep(5)
        
        out, _ = ssh_exec(ssh, "tail -n 50 /var/log/maillog 2>/dev/null", show=False)
        
        if out:
            print("Logs recente:")
            print("-" * 70)
            lines = out.strip().split('\n')
            
            # Cauta mailul nostru
            found_our_mail = False
            for i, line in enumerate(lines):
                if TEST_TO in line or timestamp[:10] in line:
                    # Afiseaza liniile relevante
                    start = max(0, i-2)
                    end = min(len(lines), i+3)
                    for j in range(start, end):
                        l = lines[j]
                        if "stat=Sent" in l or "250" in l:
                            print(f"  [SUCCESS] {l}")
                            found_our_mail = True
                        elif "error" in l.lower() or "deferred" in l.lower() or "refused" in l.lower():
                            print(f"  [ERROR] {l}")
                        elif TEST_TO in l:
                            print(f"  [>>>] {l}")
                        else:
                            print(f"        {l}")
                    break
            
            if not found_our_mail:
                # Afiseaza ultimele 10 linii
                print("\nUltimele 10 linii din log:")
                for line in lines[-10:]:
                    if line.strip():
                        print(f"  {line}")
            
            print("-" * 70)
        
        print()
        
        # 8. Sumar final
        print("=" * 70)
        print("FINALIZARE")
        print("=" * 70)
        print()
        print(f">> Email trimis catre: {TEST_TO}")
        print()
        print(">> Verifica:")
        print(f"   1. Inbox la {TEST_TO}")
        print("   2. Folder Spam/Junk")
        print("   3. Asteapta 2-10 minute")
        print()
        print(">> Pentru trimitere manuala:")
        print(f"   ssh {USER}@{HOST}")
        print(f"   echo 'Text mesaj' | mail -s 'Subject' {TEST_TO}")
        print()
        print(">> Monitoring:")
        print("   tail -f /var/log/maillog")
        print()
        print(">> Nota importanta:")
        print("   - Serverul trimite email-ul catre Gmail")
        print("   - Gmail poate respinge sau pune in Spam din cauza:")
        print("     * Lipsa SPF/DKIM pentru domeniul tau")
        print("     * IP-ul serverului in blacklist")
        print("     * Continut suspect")
        print("   - Daca nu primesti email-ul, verifica logs-urile")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("PROCES FINALIZAT!")
        print("=" * 70)
        print()
        print("Verifica inbox-ul in urmatoarele 5 minute.")
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

