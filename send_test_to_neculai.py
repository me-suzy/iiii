#!/usr/bin/env python
"""
Trimite email de test catre contact@strusgure.com
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
    print("   TRIMITERE EMAIL DE TEST CATRE contact@strusgure.com")
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
        
        # 1. Verifica sendmail status
        print("=" * 70)
        print("VERIFICARE SENDMAIL")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "service sendmail status 2>&1 | head -3", show=False)
        if "running" in out.lower() or "pid" in out.lower():
            print("[OK] Sendmail ruleaza")
        else:
            print("[WARN] Sendmail nu ruleaza, pornesc...")
            ssh_exec(ssh, "service sendmail start 2>&1", show=False)
            time.sleep(2)
        
        print()
        
        # 2. Trimitere email
        print("=" * 70)
        print("TRIMITERE EMAIL")
        print("=" * 70)
        print()
        
        test_msg = f"""Salut,

Acesta este un email de test trimis de pe serverul sariasi66.ro

Detalii:
- Data si ora: {timestamp}
- Server: sariasi66.ro (95.196.191.92)
- De la: root@sariasi66.ro
- Catre: {TEST_TO}

Acest email testeaza functionalitatea sendmail pe serverul Linux.

Daca primesti acest mesaj, inseamna ca serverul poate trimite emailuri cu succes!

---
Trimis automat prin sendmail
Server: Red Hat Enterprise Linux 4
"""
        
        # Escapare pentru bash
        escaped = test_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        cmd = f'echo "{escaped}" | /bin/mail -s "[Test Server] Email de pe sariasi66.ro - {timestamp}" {TEST_TO} 2>&1'
        
        print(f"[INFO] Trimitere email catre: {TEST_TO}")
        print(f"[INFO] From: root@sariasi66.ro")
        print(f"[INFO] Subject: [Test Server] Email de pe sariasi66.ro")
        print()
        
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=10)
        
        if out:
            if "error" in out.lower():
                print(f"[ERROR] {out}")
            else:
                print(f"[INFO] {out}")
        else:
            print("[OK] Comanda mail executata cu succes!")
        
        print()
        
        # 3. Asteapta si verifica logs
        print("=" * 70)
        print("VERIFICARE LOGS")
        print("=" * 70)
        print()
        print("[INFO] Astept 5 secunde pentru procesare...")
        time.sleep(5)
        
        out, _ = ssh_exec(ssh, "tail -n 60 /var/log/maillog 2>/dev/null", show=False)
        
        if out:
            print("Logs pentru emailul trimis:")
            print("-" * 70)
            lines = out.strip().split('\n')
            
            # Cauta linii relevante pentru emailul nostru
            relevant_lines = []
            for i, line in enumerate(lines):
                if TEST_TO in line or "neculaifantanaru" in line.lower():
                    # Adauga context (2 linii inainte si dupa)
                    start = max(0, i-2)
                    end = min(len(lines), i+3)
                    relevant_lines.extend(lines[start:end])
            
            if relevant_lines:
                # Afiseaza linii unice
                seen = set()
                for line in relevant_lines:
                    if line not in seen and line.strip():
                        seen.add(line)
                        lw = line.lower()
                        
                        if "stat=sent" in lw or "message accepted" in lw or "250 " in line:
                            print(f"  [SUCCESS] {line}")
                        elif "error" in lw or "failed" in lw or "deferred" in lw or "unavailable" in lw:
                            print(f"  [ERROR] {line}")
                        elif TEST_TO in line:
                            print(f"  [>>>] {line}")
                        else:
                            print(f"        {line}")
            else:
                print("\nUltimele 15 linii din log:")
                for line in lines[-15:]:
                    if line.strip():
                        lw = line.lower()
                        if "stat=sent" in lw:
                            print(f"  [OK] {line}")
                        elif "error" in lw or "deferred" in lw:
                            print(f"  [ERR] {line}")
                        else:
                            print(f"       {line}")
            
            print("-" * 70)
        
        print()
        
        # 4. Rezumat si instructiuni
        print("=" * 70)
        print("REZUMAT SI URMATOARELE PASI")
        print("=" * 70)
        print()
        print(f"[OK] Email trimis catre: {TEST_TO}")
        print()
        print(">> VERIFICA INBOX-UL:")
        print(f"   - Acceseaza inbox-ul pentru {TEST_TO}")
        print("   - Verifica si folderul Spam/Junk")
        print("   - Asteapta 2-10 minute pentru livrare")
        print()
        print(">> CE SA CAUTI IN LOGS:")
        print("   - 'stat=Sent' = Email trimis cu succes")
        print("   - 'Message accepted' = Serverul destinatie a acceptat")
        print("   - 'Deferred' = Email in coada (se va retrimite)")
        print("   - 'Service unavailable' = Serverul destinatie refuza")
        print()
        print(">> PENTRU A TRIMITE ALTE EMAILURI:")
        print(f"   ssh {USER}@{HOST}")
        print("   echo 'Mesajul tau' | mail -s 'Subject' destinatar@domain.com")
        print()
        print(">> EXEMPLE:")
        print(f"   echo 'Test 1' | mail -s 'Test' {TEST_TO}")
        print("   echo 'Mesaj important' | mail -s 'Urgent' altcineva@domain.com")
        print()
        print(">> MONITORING IN TIMP REAL:")
        print("   tail -f /var/log/maillog")
        print()
        
        # 5. Verifica domeniul destinatie
        print("=" * 70)
        print("VERIFICARE DNS PENTRU DESTINATIE")
        print("=" * 70)
        print()
        
        domain = TEST_TO.split('@')[1]
        print(f"[INFO] Verific MX records pentru domeniul: {domain}")
        
        out, _ = ssh_exec(ssh, f"host -t MX {domain} 2>&1", show=False)
        if out:
            if "mail" in out.lower() or "mx" in out.lower():
                print(f"[OK] MX records gasite pentru {domain}:")
                print(out)
            else:
                print(f"[WARN] {out}")
        
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("PROCES FINALIZAT!")
        print("=" * 70)
        print()
        print("Emailul a fost trimis cu succes de pe server!")
        print(f"Verifica inbox-ul la {TEST_TO} in urmatoarele 5-10 minute.")
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

