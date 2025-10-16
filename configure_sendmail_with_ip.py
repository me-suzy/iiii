#!/usr/bin/env python
"""
Configurez sendmail sa foloseasca IP-ul in loc de domeniul inexistent
"""

import paramiko
import sys
from datetime import datetime
import time

HOST = "95.196.191.92"
USER = "root"
PASS = "bebef_999"
PORT = 22

SERVER_IP = "95.196.191.92"


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
    print("   CONFIGURARE SENDMAIL CU IP IN LOC DE DOMENIU")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Oprire sendmail pentru configurare
        print("=" * 70)
        print("1. OPRIRE SENDMAIL PENTRU CONFIGURARE")
        print("=" * 70)
        print()
        
        print("[INFO] Opreste sendmail...")
        ssh_exec(ssh, "service sendmail stop 2>&1", show=False)
        time.sleep(2)
        
        print("[OK] Sendmail oprit!")
        print()
        
        # 2. Backup configurarea actuala
        print("=" * 70)
        print("2. BACKUP CONFIGURAREA ACTUALA")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/etc/mail/sendmail.cf.backup.{timestamp}"
        
        print(f"[INFO] Creez backup: {backup_file}")
        ssh_exec(ssh, f"cp /etc/mail/sendmail.cf {backup_file}", show=False)
        print("[OK] Backup creat!")
        print()
        
        # 3. Verifica configurarea actuala
        print("=" * 70)
        print("3. VERIFICARE CONFIGURARE ACTUALA")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -E '^Dj|^Dm|^Cw' /etc/mail/sendmail.cf", show=False)
        if out:
            print("Configurari actuale:")
            print(out)
        
        print()
        
        # 4. Configurez sendmail sa foloseasca IP-ul
        print("=" * 70)
        print("4. CONFIGURARE SENDMAIL CU IP")
        print("=" * 70)
        print()
        
        # Creez o noua configurare cu IP-ul
        new_config = f"""# Configurare sendmail cu IP-ul serverului
# Generat automat pentru {SERVER_IP}

# Setez domeniul la IP-ul serverului
Dj{SERVER_IP}

# Setez masina locala
Dm{SERVER_IP}

# Setez clasele de masini
Cwlocalhost
Cw{SERVER_IP}

# Restul configurarii ramane la fel
"""
        
        print("[INFO] Configurez sendmail sa foloseasca IP-ul...")
        
        # Modific configurarea
        ssh_exec(ssh, f"sed -i 's/^Dj.*/Dj{SERVER_IP}/' /etc/mail/sendmail.cf", show=False)
        ssh_exec(ssh, f"sed -i 's/^Dm.*/Dm{SERVER_IP}/' /etc/mail/sendmail.cf", show=False)
        
        # Adaug IP-ul la clasele de masini daca nu exista
        out, _ = ssh_exec(ssh, f"grep 'Cw{SERVER_IP}' /etc/mail/sendmail.cf", show=False)
        if not out:
            ssh_exec(ssh, f"echo 'Cw{SERVER_IP}' >> /etc/mail/sendmail.cf", show=False)
        
        print("[OK] Configurare actualizata!")
        print()
        
        # 5. Verifica noua configurare
        print("=" * 70)
        print("5. VERIFICARE NOUA CONFIGURARE")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -E '^Dj|^Dm|^Cw' /etc/mail/sendmail.cf", show=False)
        if out:
            print("Noua configurare:")
            print(out)
        
        print()
        
        # 6. Pornire sendmail cu noua configurare
        print("=" * 70)
        print("6. PORNIRE SENDMAIL CU NOUA CONFIGURARE")
        print("=" * 70)
        print()
        
        print("[INFO] Pornesc sendmail...")
        ssh_exec(ssh, "service sendmail start 2>&1", show=False)
        time.sleep(3)
        
        # Verifica daca a pornit
        out, _ = ssh_exec(ssh, "service sendmail status 2>&1 | head -3", show=False)
        if out and "running" in out.lower():
            print("[OK] Sendmail pornit cu noua configurare!")
        else:
            print("[WARN] Sendmail nu a pornit corect")
        
        print()
        
        # 7. Test cu noua configurare
        print("=" * 70)
        print("7. TEST CU NOUA CONFIGURARE")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        test_msg = f"""Test cu IP-ul serverului - {timestamp}

Acest email este trimis cu noua configurare sendmail
care foloseste IP-ul serverului in loc de domeniu.

Detalii:
- Server IP: {SERVER_IP}
- From: root@{SERVER_IP}
- Timestamp: {timestamp}

Daca primesti acest email, configurarea cu IP functioneaza!
"""
        
        # Escapare pentru bash
        escaped = test_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        cmd = f'echo "{escaped}" | /bin/mail -s "[Test IP] Sendmail cu IP - {timestamp}" strusgure.gree@gmail.com 2>&1'
        
        print(f"[INFO] Trimitere email de test...")
        print(f"[INFO] From: root@{SERVER_IP}")
        print(f"[INFO] To: strusgure.gree@gmail.com")
        print()
        
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=5)
        
        if out:
            print(f"[INFO] Output: {out}")
        else:
            print("[OK] Email trimis!")
        
        print()
        
        # 8. Verifica logs pentru testul nou
        print("=" * 70)
        print("8. VERIFICARE LOGS PENTRU TESTUL NOU")
        print("=" * 70)
        print()
        print("[INFO] Astept 3 secunde...")
        time.sleep(3)
        
        out, _ = ssh_exec(ssh, f"tail -n 20 /var/log/maillog 2>/dev/null | grep 'strusgure.gree' | tail -3", show=False)
        
        if out:
            print("Logs pentru testul nou:")
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
            print("[INFO] Nu am gasit inca logs pentru testul nou")
        
        print()
        
        # 9. Sumar si recomandari
        print("=" * 70)
        print("SUMAR CONFIGURARE CU IP")
        print("=" * 70)
        print()
        
        print(">> AM CONFIGURAT SENDMAIL SA FOLOSEASCA:")
        print(f"   - IP-ul serverului: {SERVER_IP}")
        print(f"   - From: root@{SERVER_IP}")
        print(f"   - In loc de: root@sariasi66.ro")
        print()
        print(">> BACKUP CREAT:")
        print(f"   - {backup_file}")
        print()
        print(">> TEST TRIMIS:")
        print("   - To: strusgure.gree@gmail.com")
        print("   - Subject: [Test IP] Sendmail cu IP")
        print()
        print(">> VERIFICA INBOX-UL:")
        print("   - strusgure.gree@gmail.com")
        print("   - Verifica si folderul Spam/Junk")
        print()
        print(">> DACA NU PRIMESTI EMAILUL:")
        print("   - IP-ul poate fi pe blacklist")
        print("   - Verifica: https://mxtoolbox.com/blacklists.aspx")
        print("   - Considera folosirea unui relay extern")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("CONFIGURARE COMPLETA!")
        print("=" * 70)
        print()
        print("Am configurat sendmail sa foloseasca IP-ul serverului.")
        print("Verifica inbox-ul pentru emailul de test.")
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
