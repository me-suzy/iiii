#!/usr/bin/env python
"""
Test cu adresa externa pentru a confirma ca sendmail functioneaza
"""

import paramiko
import sys
from datetime import datetime
import time

HOST = "95.196.191.92"
USER = "root"
PASS = "bebef_999"
PORT = 22

# Test cu o adresa externa
TEST_EXTERNAL = "strusgure.gree@gmail.com"  # Adresa Gmail pentru test


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
    print("   TEST CU ADRESA EXTERNA")
    print("=" * 70)
    print()
    
    print(f"[INFO] Voi testa cu adresa externa: {TEST_EXTERNAL}")
    print("[INFO] Daca vrei sa testezi cu alta adresa, modifica TEST_EXTERNAL in script")
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # Trimitere email extern
        print("=" * 70)
        print("TRIMITERE EMAIL EXTERN")
        print("=" * 70)
        print()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        external_msg = f"""Test cu adresa externa - {timestamp}

Acest email este trimis pentru a testa daca sendmail functioneaza
cu adrese externe (Yahoo, Gmail, etc.).

Data: {timestamp}
Server: sariasi66.ro
From: root@sariasi66.ro

Daca primesti acest email, sendmail functioneaza perfect
si problema este doar cu serverul spatiul.ro!
"""
        
        # Escapare pentru bash
        escaped = external_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        cmd = f'echo "{escaped}" | /bin/mail -s "[Test extern] Sendmail functional - {timestamp}" {TEST_EXTERNAL} 2>&1'
        
        print(f"[INFO] Trimitere email extern...")
        print(f"[INFO] To: {TEST_EXTERNAL}")
        print(f"[INFO] Subject: [Test extern] Sendmail functional")
        print()
        
        out, _ = ssh_exec(ssh, cmd, show=False, timeout=5)
        
        if out:
            print(f"[INFO] Output: {out}")
        else:
            print("[OK] Email extern trimis!")
        
        print()
        
        # Asteapta si verifica logs
        print("=" * 70)
        print("VERIFICARE LOGS PENTRU EMAILUL EXTERN")
        print("=" * 70)
        print()
        print("[INFO] Astept 3 secunde...")
        time.sleep(3)
        
        domain = TEST_EXTERNAL.split('@')[1]
        out, _ = ssh_exec(ssh, f"tail -n 30 /var/log/maillog 2>/dev/null | grep '{domain}' | tail -5", show=False)
        
        if out:
            print("Logs pentru emailul extern:")
            print("-" * 70)
            lines = out.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                lw = line.lower()
                if "stat=sent" in lw:
                    print(f"  [SUCCESS] {line}")
                elif "user unknown" in lw:
                    print(f"  [ERROR] {line}")
                elif "deferred" in lw:
                    print(f"  [DEFERRED] {line}")
                else:
                    print(f"        {line}")
            print("-" * 70)
        else:
            print("[INFO] Nu am gasit inca logs pentru emailul extern")
        
        print()
        
        # Sumar
        print("=" * 70)
        print("SUMAR TEST EXTERN")
        print("=" * 70)
        print()
        print(">> AM TRIMIS EMAIL EXTERN:")
        print(f"   - Catre: {TEST_EXTERNAL}")
        print("   - Pentru a testa daca sendmail functioneaza cu adrese externe")
        print()
        print(">> REZULTATUL VA ARATA:")
        print("   - DACA PRIMESTI EMAILUL EXTERN:")
        print("     -> Sendmail functioneaza perfect")
        print("     -> Problema este DOAR cu serverul spatiul.ro")
        print("   - DACA NU PRIMESTI EMAILUL EXTERN:")
        print("     -> Sendmail are probleme generale")
        print("     -> Trebuie configurat SPF record")
        print()
        print(">> VERIFICA INBOX-UL PENTRU:")
        print(f"   - {TEST_EXTERNAL}")
        print("   - Subject: [Test extern] Sendmail functional")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("TEST EXTERN COMPLET!")
        print("=" * 70)
        print()
        print("Am trimis un email extern de test.")
        print("Verifica inbox-ul in urmatoarele 5-10 minute.")
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
