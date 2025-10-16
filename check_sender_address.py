#!/usr/bin/env python
"""
Verifica adresa de la care sunt trimise emailurile
"""

import paramiko
import sys
from datetime import datetime

HOST = "95.196.191.92"
USER = "root"
PASS = "bebef_999"
PORT = 22


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
    print("   VERIFICARE ADRESA EXPEDITOR")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica hostname server
        print("=" * 70)
        print("1. HOSTNAME SERVER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "hostname", show=False)
        if out:
            hostname = out.strip()
            print(f"Hostname server: {hostname}")
        
        out, _ = ssh_exec(ssh, "hostname -f", show=False)
        if out:
            fqdn = out.strip()
            print(f"FQDN server: {fqdn}")
        
        print()
        
        # 2. Verifica configurarea sendmail pentru adresa expeditor
        print("=" * 70)
        print("2. CONFIGURARE SENDMAIL - ADRESA EXPEDITOR")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -E '^Cw|^Dj|^Dm' /etc/mail/sendmail.cf", show=False)
        if out:
            print("Configurari sendmail pentru adresa expeditor:")
            print(out)
        
        print()
        
        # 3. Verifica variabilele de mediu pentru mail
        print("=" * 70)
        print("3. VARIABILE MEDIU PENTRU MAIL")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "echo $USER && echo $HOSTNAME && echo $MAIL", show=False)
        if out:
            print("Variabile mediu:")
            print(out)
        
        print()
        
        # 4. Trimitere email de test cu headers verbose
        print("=" * 70)
        print("4. EMAIL DE TEST CU HEADERS VERBOSE")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Creez email cu headers complete
        test_msg = f"""From: root@sariasi66.ro
To: strusgure.gree@gmail.com
Subject: [INFO] Adresa expeditor - {timestamp}
Date: {datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0200')}
Message-ID: <sender-test-{timestamp.replace(' ', '').replace(':', '').replace('-', '')}@sariasi66.ro>
X-Mailer: Sendmail Sender Test
X-Priority: 3
Content-Type: text/plain; charset=UTF-8

INFORMATII ADRESA EXPEDITOR:

Acest email contine informatiile complete despre adresa de la care
sunt trimise emailurile de pe serverul Linux.

Detalii server:
- Hostname: {hostname if 'hostname' in locals() else 'necunoscut'}
- FQDN: {fqdn if 'fqdn' in locals() else 'necunoscut'}
- IP: 95.196.191.92
- From: root@sariasi66.ro

Timestamp: {timestamp}

Daca primesti acest email, vezi exact de la ce adresa vine.

---
Test adresa expeditor
"""
        
        # Salvez in fisier temporar
        escaped = test_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        cmd1 = f'cat > /tmp/sender_test.txt << "EOF"\n{escaped}\nEOF'
        ssh_exec(ssh, cmd1, show=False)
        
        # Trimit emailul
        cmd2 = f'/bin/sendmail -v strusgure.gree@gmail.com < /tmp/sender_test.txt 2>&1'
        
        print(f"[INFO] Trimitere email cu informatiile despre adresa expeditor...")
        print(f"[INFO] To: strusgure.gree@gmail.com")
        print(f"[INFO] Subject: [INFO] Adresa expeditor")
        print()
        
        out, _ = ssh_exec(ssh, cmd2, show=False, timeout=15)
        
        if out:
            print("Output verbose:")
            print("-" * 70)
            print(out)
            print("-" * 70)
        else:
            print("[OK] Email trimis cu succes!")
        
        print()
        
        # 5. Verifica logs pentru emailul de test
        print("=" * 70)
        print("5. VERIFICARE LOGS PENTRU EMAILUL DE TEST")
        print("=" * 70)
        print()
        print("[INFO] Astept 3 secunde...")
        import time
        time.sleep(3)
        
        out, _ = ssh_exec(ssh, f"tail -n 20 /var/log/maillog 2>/dev/null | grep 'strusgure.gree@gmail.com' | tail -3", show=False)
        
        if out:
            print("Logs pentru emailul de test:")
            print("-" * 70)
            print(out)
            print("-" * 70)
        else:
            print("[INFO] Nu am gasit inca logs pentru emailul de test")
        
        print()
        
        # 6. Curatare fisier temporar
        ssh_exec(ssh, "rm -f /tmp/sender_test.txt", show=False)
        
        # 7. Sumar
        print("=" * 70)
        print("SUMAR ADRESA EXPEDITOR")
        print("=" * 70)
        print()
        print(">> ADRESA DE LA CARE PRIMESTI EMAILURILE:")
        print("   root@sariasi66.ro")
        print()
        print(">> VERIFICA INBOX-UL PENTRU:")
        print("   - strusgure.gree@gmail.com")
        print("   - Subject: [INFO] Adresa expeditor")
        print("   - From: root@sariasi66.ro")
        print()
        print(">> DACA NU VEI PRIMI EMAILUL:")
        print("   - Verifica folderul Spam/Junk")
        print("   - Gmail poate bloca emailurile fara SPF record")
        print("   - Configureaza SPF record pentru sariasi66.ro")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("VERIFICARE COMPLETA!")
        print("=" * 70)
        print()
        print("Am trimis un email cu informatiile complete despre adresa expeditor.")
        print("Verifica inbox-ul pentru strusgure.gree@gmail.com")
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
