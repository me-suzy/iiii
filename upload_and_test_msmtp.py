import os
import sys
import paramiko
import time

# Configurare conexiune server
HOST = "95.196.191.92"
USER = "root"
PASS = "bebef_999"
PORT = 22

# Calea locală către binarul msmtp
LOCAL_MSMTP_PATH = r"E:\Downloads\msmtp-linux-static"

# Configurare Gmail
GMAIL_ADDRESS = "bib.acadiasi@gmail.com"
APP_PASSWORD = "ayigwvgouoginhpd"  # fără spații
TEST_RECIPIENT = "larisbirzu@gmail.com"


def ssh_exec(ssh, cmd, show_output=True):
    """Execută comandă pe server și returnează output"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=180)
    out = stdout.read().decode("utf-8", errors="ignore")
    err = stderr.read().decode("utf-8", errors="ignore")
    
    if show_output:
        if out:
            print(out)
        if err:
            print(f"[WARN] {err}")
    
    return out, err


def main():
    print("=" * 70)
    print("   CONFIGURARE MSMTP PE SERVER LINUX - RELAY GMAIL")
    print("=" * 70)
    print()
    
    # Verificare binar local
    if not os.path.exists(LOCAL_MSMTP_PATH):
        print(f"[ERROR] Nu gasesc binarul la: {LOCAL_MSMTP_PATH}")
        print("Te rog verifica calea si incearca din nou.")
        sys.exit(1)
    
    file_size = os.path.getsize(LOCAL_MSMTP_PATH)
    print(f"[OK] Binar gasit: {LOCAL_MSMTP_PATH}")
    print(f"     Dimensiune: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    print()
    
    # Conectare la server
    print(f"[INFO] Conectare la server {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat cu succes!")
        print()
    except Exception as e:
        print(f"[ERROR] Eroare la conectare: {e}")
        sys.exit(1)
    
    try:
        # 1. Upload binar msmtp
        print("=" * 70)
        print("PASUL 1: Upload binar msmtp pe server")
        print("=" * 70)
        
        sftp = ssh.open_sftp()
        remote_path = "/usr/local/bin/msmtp"
        
        print(f"[INFO] Upload in curs la {remote_path}...")
        sftp.put(LOCAL_MSMTP_PATH, remote_path)
        sftp.chmod(remote_path, 0o755)
        sftp.close()
        
        print("[OK] Binar msmtp incarcat si permisiuni setate (755)")
        
        # Verificare binar pe server
        out, _ = ssh_exec(ssh, "file /usr/local/bin/msmtp", show_output=False)
        print(f"[INFO] Tip fisier: {out.strip()}")
        
        out, _ = ssh_exec(ssh, "/usr/local/bin/msmtp --version 2>&1 | head -5", show_output=False)
        if "msmtp" in out.lower():
            print(f"[OK] Versiune msmtp:\n{out}")
        else:
            print(f"[WARN] Output versiune:\n{out}")
        print()
        
        # 2. Configurare msmtprc
        print("=" * 70)
        print("PASUL 2: Configurare /etc/msmtprc")
        print("=" * 70)
        
        msmtprc_content = f"""# Configurare msmtp pentru Gmail
defaults
auth           on
tls            on
tls_starttls   on
tls_trust_file /etc/ssl/certs/ca-bundle.crt
logfile        /var/log/msmtp.log

# Cont Gmail
account        gmail
host           smtp.gmail.com
port           587
from           {GMAIL_ADDRESS}
user           {GMAIL_ADDRESS}
password       {APP_PASSWORD}

# Cont implicit
account default : gmail
"""
        
        cmd = f"cat > /etc/msmtprc <<'EOFMSMTP'\n{msmtprc_content}\nEOFMSMTP"
        ssh_exec(ssh, cmd, show_output=False)
        ssh_exec(ssh, "chmod 600 /etc/msmtprc", show_output=False)
        
        print("[OK] Fisier /etc/msmtprc creat si securizat (chmod 600)")
        
        # Creare fisier log
        ssh_exec(ssh, "touch /var/log/msmtp.log && chmod 666 /var/log/msmtp.log", show_output=False)
        print("[OK] Fisier log creat: /var/log/msmtp.log")
        print()
        
        # 3. Verificare certificat TLS
        print("=" * 70)
        print("PASUL 3: Verificare certificat TLS")
        print("=" * 70)
        
        # Caută bundle-ul de certificate
        cert_paths = [
            "/etc/ssl/certs/ca-bundle.crt",
            "/etc/ssl/certs/ca-certificates.crt",
            "/etc/pki/tls/certs/ca-bundle.crt",
            "/etc/ssl/ca-bundle.pem"
        ]
        
        cert_found = None
        for cert_path in cert_paths:
            out, _ = ssh_exec(ssh, f"[ -f {cert_path} ] && echo EXISTS || echo MISSING", show_output=False)
            if "EXISTS" in out:
                cert_found = cert_path
                print(f"[OK] Certificate gasite: {cert_path}")
                
                # Actualizeaza msmtprc cu calea corecta
                ssh_exec(ssh, f"sed -i 's|tls_trust_file.*|tls_trust_file {cert_path}|' /etc/msmtprc", show_output=False)
                break
        
        if not cert_found:
            print("[WARN] Nu am gasit bundle de certificate CA.")
            print("       Voi incerca fara validare stricta TLS...")
            # Configurare fara validare stricta (mai putin sigur dar functional pe servere vechi)
            ssh_exec(ssh, "sed -i 's|tls_trust_file.*|tls_certcheck off|' /etc/msmtprc", show_output=False)
        print()
        
        # 4. Link catre sendmail (optional, util pentru compatibilitate)
        print("=" * 70)
        print("PASUL 4: Creare link simbolic sendmail -> msmtp")
        print("=" * 70)
        
        ssh_exec(ssh, "ln -sf /usr/local/bin/msmtp /usr/sbin/sendmail", show_output=False)
        ssh_exec(ssh, "ln -sf /usr/local/bin/msmtp /usr/bin/sendmail", show_output=False)
        ssh_exec(ssh, "ln -sf /usr/local/bin/msmtp /usr/lib/sendmail", show_output=False)
        
        print("[OK] Link-uri simbolice create pentru compatibilitate")
        print()
        
        # 5. Test trimitere email
        print("=" * 70)
        print("PASUL 5: TRIMITERE EMAIL DE TEST")
        print("=" * 70)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        test_subject = f"[Test msmtp] Email trimis la {timestamp}"
        test_body = f"""Salut,

Acesta este un email de test trimis prin msmtp de pe serverul Linux.

Configurare:
- msmtp instalat in /usr/local/bin/msmtp
- Configurare Gmail (SMTP relay)
- Cont: {GMAIL_ADDRESS}
- Data si ora: {timestamp}

Daca primesti acest email, configurarea functioneaza perfect!

---
Trimis automat de scriptul Python de configurare msmtp
"""
        
        # Metoda 1: Trimitere directa cu msmtp
        print(f"[INFO] Trimitere email de test catre {TEST_RECIPIENT}...")
        print()
        
        email_message = f"""From: {GMAIL_ADDRESS}
To: {TEST_RECIPIENT}
Subject: {test_subject}

{test_body}
"""
        
        # Escapăm ghilimelele pentru bash
        email_escaped = email_message.replace('"', '\\"').replace('$', '\\$')
        
        cmd = f'echo "{email_escaped}" | /usr/local/bin/msmtp -v -t 2>&1'
        out, err = ssh_exec(ssh, cmd)
        
        print()
        
        # Verificare rezultat
        if "250" in out or "accepted" in out.lower() or "sent" in out.lower():
            print("[OK] >>> EMAIL TRIMIS CU SUCCES! <<<")
        elif "error" in out.lower() or "failed" in out.lower():
            print("[ERROR] XXX Eroare la trimitere:")
            print(out)
            if err:
                print(err)
        else:
            print("[INFO] Output msmtp:")
            print(out)
        
        print()
        
        # 6. Verificare log msmtp
        print("=" * 70)
        print("PASUL 6: Verificare log-uri msmtp")
        print("=" * 70)
        
        time.sleep(2)  # Așteaptă puțin pentru log
        
        out, _ = ssh_exec(ssh, "tail -n 30 /var/log/msmtp.log 2>/dev/null || echo 'Log gol sau inexistent'", show_output=False)
        
        if out.strip() and "Log gol" not in out:
            print("[INFO] Ultimele 30 linii din /var/log/msmtp.log:")
            print("-" * 70)
            for line in out.strip().split('\n'):
                if line.strip():
                    print(f"  {line}")
            print("-" * 70)
        else:
            print("[INFO] Log-ul este gol (normal pentru prima rulare)")
        
        print()
        
        # 7. Sumar final
        print("=" * 70)
        print("   CONFIGURARE COMPLETATA!")
        print("=" * 70)
        print()
        print(">> Verificari finale:")
        print(f"   1. Verifica inbox-ul la {TEST_RECIPIENT}")
        print("   2. Verifica folderul Spam/Junk")
        print("   3. Daca nu apare, verifica log-ul pe server:")
        print(f"      ssh {USER}@{HOST}")
        print("      tail -f /var/log/msmtp.log")
        print()
        print(">> Testare manuala din server:")
        print(f'   echo "Test" | mail -s "Test manual" {TEST_RECIPIENT}')
        print()
        print(">> Configurare:")
        print(f"   Binar: /usr/local/bin/msmtp")
        print(f"   Config: /etc/msmtprc")
        print(f"   Log: /var/log/msmtp.log")
        print()
        
    except Exception as e:
        print(f"[ERROR] Eroare in timpul configurarii: {e}")
        import traceback
        traceback.print_exc()
        ssh.close()
        sys.exit(1)
    
    finally:
        try:
            ssh.close()
            print("[INFO] Conexiune inchisa.")
        except:
            pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN] Script intrerupt de utilizator.")
        sys.exit(130)

