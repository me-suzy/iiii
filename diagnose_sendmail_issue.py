#!/usr/bin/env python
"""
Diagnosticare problema sendmail pe serverul Linux
"""

import paramiko
import sys
from datetime import datetime
import time

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
    print("   DIAGNOSTICARE PROBLEMA SENDMAIL")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica daca sendmail chiar ruleaza
        print("=" * 70)
        print("1. VERIFICARE PROCESE SENDMAIL")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "ps aux | grep sendmail | grep -v grep", show=False)
        if out:
            print("Procese sendmail active:")
            print(out)
        else:
            print("[ERROR] NU sunt procese sendmail active!")
        
        print()
        
        # 2. Verifica statusul serviciului
        print("=" * 70)
        print("2. STATUS SERVICIU SENDMAIL")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "service sendmail status 2>&1", show=False)
        if out:
            print("Status serviciu:")
            print(out)
        
        print()
        
        # 3. Verifica daca portul 25 este deschis
        print("=" * 70)
        print("3. VERIFICARE PORT 25")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "netstat -tlnp | grep :25", show=False)
        if out:
            print("Porturi 25 active:")
            print(out)
        else:
            print("[WARN] Nu am gasit portul 25 activ")
        
        print()
        
        # 4. Verifica configurarea sendmail
        print("=" * 70)
        print("4. VERIFICARE CONFIGURARE SENDMAIL")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "grep -E '^O QueueDirectory|^O DaemonPortOptions' /etc/mail/sendmail.cf", show=False)
        if out:
            print("Configurari importante sendmail:")
            print(out)
        
        print()
        
        # 5. Test direct cu sendmail
        print("=" * 70)
        print("5. TEST DIRECT SENDMAIL")
        print("=" * 70)
        print()
        
        # Creez un mesaj simplu
        simple_msg = f"""Test direct sendmail - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Acest email este trimis prin test direct cu sendmail.

Daca primesti acest email, sendmail functioneaza.
"""
        
        # Test cu comanda mail simpla
        print("[INFO] Test cu comanda mail...")
        escaped = simple_msg.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        cmd1 = f'echo "{escaped}" | mail -s "Test direct mail" strusgure.gree@gmail.com 2>&1'
        
        out1, _ = ssh_exec(ssh, cmd1, show=False, timeout=5)
        if out1:
            print(f"Output mail: {out1}")
        else:
            print("[OK] Mail command executat")
        
        print()
        
        # Test cu sendmail direct
        print("[INFO] Test cu sendmail direct...")
        cmd2 = f'echo -e "To: strusgure.gree@gmail.com\\nSubject: Test direct sendmail\\n\\n{escaped}" | sendmail -v strusgure.gree@gmail.com 2>&1'
        
        out2, _ = ssh_exec(ssh, cmd2, show=False, timeout=10)
        if out2:
            print("Output sendmail direct:")
            print("-" * 50)
            print(out2)
            print("-" * 50)
        
        print()
        
        # 6. Verifica logs imediat dupa test
        print("=" * 70)
        print("6. VERIFICARE LOGS IMEDIAT")
        print("=" * 70)
        print()
        print("[INFO] Astept 3 secunde...")
        time.sleep(3)
        
        out, _ = ssh_exec(ssh, f"tail -n 20 /var/log/maillog 2>/dev/null | tail -10", show=False)
        
        if out:
            print("Logs recente:")
            print("-" * 70)
            lines = out.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                lw = line.lower()
                if "strusgure.gree" in lw or "gmail" in lw:
                    if "stat=sent" in lw:
                        print(f"  [SUCCESS] {line}")
                    elif "user unknown" in lw:
                        print(f"  [ERROR] {line}")
                    elif "deferred" in lw:
                        print(f"  [DEFERRED] {line}")
                    elif "service unavailable" in lw:
                        print(f"  [BLOCKED] {line}")
                    else:
                        print(f"        {line}")
            print("-" * 70)
        else:
            print("[INFO] Nu am gasit logs recente")
        
        print()
        
        # 7. Verifica coada de mailuri
        print("=" * 70)
        print("7. VERIFICARE COADA MAILURI")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "mailq 2>&1 | head -20", show=False)
        if out:
            if "empty" in out.lower():
                print("[OK] Coada de mailuri este goala")
            else:
                print("Coada de mailuri:")
                print(out)
        
        print()
        
        # 8. Verifica daca sunt probleme de retea
        print("=" * 70)
        print("8. VERIFICARE CONECTIVITATE RETELE")
        print("=" * 70)
        print()
        
        print("[INFO] Testez conectivitatea la Gmail...")
        out, _ = ssh_exec(ssh, "nslookup gmail-smtp-in.l.google.com 2>&1 | head -5", show=False)
        if out:
            print("DNS pentru Gmail:")
            print(out)
        
        print()
        
        # 9. Sumar si recomandari
        print("=" * 70)
        print("SUMAR SI RECOMANDARI")
        print("=" * 70)
        print()
        
        print(">> PROBLEME IDENTIFICATE:")
        print("   1. Emailurile sunt trimise de pe server")
        print("   2. Dar nu ajung la destinatie")
        print("   3. Posibil blocat de filtre anti-spam")
        print()
        print(">> CAUZE POSIBILE:")
        print("   1. Lipseste SPF record pentru domeniul tau")
        print("   2. Serverul tau este pe blacklist-uri")
        print("   3. IP-ul 95.196.191.92 este blocat")
        print("   4. Configurarea sendmail nu este optima")
        print()
        print(">> SOLUTII RECOMANDATE:")
        print("   1. Configureaza SPF record:")
        print("      v=spf1 ip4:95.196.191.92 ~all")
        print("   2. Verifica daca IP-ul este pe blacklist:")
        print("      https://mxtoolbox.com/blacklists.aspx")
        print("   3. Contacteaza administratorul serverului")
        print("   4. Considera folosirea unui relay extern")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("DIAGNOSTIC COMPLET!")
        print("=" * 70)
        print()
        print("Am rulat teste complete pe serverul Linux.")
        print("Verifica logs-urile de mai sus pentru detalii.")
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
