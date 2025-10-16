#!/usr/bin/env python
"""
Verifica cine gestioneaza DNS-ul pentru domeniul sariasi66.ro
"""

import paramiko
import sys
from datetime import datetime

HOST = "95.196.191.92"
USER = "root"
PASS = "bebef_999"
PORT = 22

DOMAIN = "sariasi66.ro"


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
    print("   VERIFICARE DNS MANAGEMENT PENTRU SPF RECORD")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica nameserver-ele pentru domeniu
        print("=" * 70)
        print("1. VERIFICARE NAMESERVER-E")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, f"host -t NS {DOMAIN} 2>&1", show=False)
        if out:
            print(f"Nameserver-e pentru {DOMAIN}:")
            print(out)
        
        print()
        
        # 2. Verifica daca exista deja SPF record
        print("=" * 70)
        print("2. VERIFICARE SPF RECORD EXISTENT")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, f"host -t TXT {DOMAIN} 2>&1", show=False)
        if out:
            print(f"Record-uri TXT pentru {DOMAIN}:")
            print(out)
            
            if "spf" in out.lower():
                print("\n[INFO] Exista deja un SPF record!")
            else:
                print("\n[WARN] NU exista SPF record!")
        else:
            print("[WARN] Nu am gasit record-uri TXT")
        
        print()
        
        # 3. Verifica daca serverul poate sa-si configureze DNS-ul
        print("=" * 70)
        print("3. VERIFICARE CONFIGURARE DNS LOCAL")
        print("=" * 70)
        print()
        
        # Verifica daca exista bind sau alte servicii DNS
        out, _ = ssh_exec(ssh, "ps aux | grep -E '(named|bind|dns)' | grep -v grep", show=False)
        if out:
            print("Servicii DNS active pe server:")
            print(out)
        else:
            print("[INFO] Nu sunt servicii DNS active pe server")
        
        # Verifica daca exista fisiere de configurare DNS
        out, _ = ssh_exec(ssh, "ls -la /etc/named* /var/named* 2>/dev/null", show=False)
        if out:
            print("\nFisiere de configurare DNS:")
            print(out)
        else:
            print("\n[INFO] Nu am gasit fisiere de configurare DNS locale")
        
        print()
        
        # 4. Verifica IP-ul serverului
        print("=" * 70)
        print("4. VERIFICARE IP SERVER")
        print("=" * 70)
        print()
        
        out, _ = ssh_exec(ssh, "hostname -i", show=False)
        if out:
            server_ip = out.strip()
            print(f"IP server: {server_ip}")
        
        out, _ = ssh_exec(ssh, "curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo 'Nu pot determina IP extern'", show=False)
        if out:
            external_ip = out.strip()
            print(f"IP extern: {external_ip}")
        
        print()
        
        # 5. Instrucțiuni pentru configurare SPF
        print("=" * 70)
        print("5. INSTRUCTIUNI PENTRU CONFIGURARE SPF")
        print("=" * 70)
        print()
        
        print(">> SPF RECORD NECESAR:")
        print("   v=spf1 ip4:95.196.191.92 ~all")
        print()
        print(">> UNDE SA CONFIGUREZI:")
        print("   1. Cauta cine gestioneaza DNS-ul pentru sariasi66.ro")
        print("   2. Nameserver-ele de mai sus iti arata unde sa cauti")
        print("   3. Intră în contul de la providerul de DNS")
        print()
        print(">> CUM SA CONFIGUREZI:")
        print("   - Host/Name: @ (sau sariasi66.ro)")
        print("   - Type: TXT")
        print("   - Value: v=spf1 ip4:95.196.191.92 ~all")
        print("   - TTL: 3600 (1 ora)")
        print()
        print(">> DUPĂ CONFIGURARE:")
        print("   - Așteaptă 24-48 ore pentru propagare")
        print("   - Testează din nou emailurile")
        print("   - Verifică cu: host -t TXT sariasi66.ro")
        print()
        
        # 6. Verificare alternativa - test cu o adresa care accepta emailuri fara SPF
        print("=" * 70)
        print("6. TEST ALTERNATIV")
        print("=" * 70)
        print()
        
        print(">> PENTRU A TESTA DACA SENDMAIL FUNCTIONEAZA:")
        print("   Testează cu o adresa care accepta emailuri fara SPF:")
        print("   - 10minutemail.com")
        print("   - mailinator.com")
        print("   - temp-mail.org")
        print()
        print(">> COMENDA PENTRU TEST:")
        print("   echo 'Test fara SPF' | mail -s 'Test' test@10minutemail.com")
        print()
        
        ssh.close()
        
        print("=" * 70)
        print("VERIFICARE COMPLETA!")
        print("=" * 70)
        print()
        print("Am verificat configuratia DNS pentru domeniul tau.")
        print("Urmareste instructiunile de mai sus pentru configurarea SPF record.")
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
