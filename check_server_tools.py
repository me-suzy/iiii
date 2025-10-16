#!/usr/bin/env python
"""Verifica ce limbaje si utilitare sunt disponibile pe server"""

import paramiko

HOST = "95.196.191.92"
USER = "root"
PASS = "bebef_999"
PORT = 22

def ssh_exec(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    out = stdout.read().decode("utf-8", errors="ignore")
    return out.strip()

print("Verificare limbaje si utilitare disponibile pe server...")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, PORT, USER, PASS, timeout=15)

# Check limbaje
tools = {
    "Python": "python --version 2>&1 || python3 --version 2>&1 || python2 --version 2>&1",
    "Perl": "perl --version | head -2",
    "PHP": "php --version | head -1",
    "Ruby": "ruby --version",
    "Bash": "bash --version | head -1",
    "Telnet": "which telnet",
    "NC (netcat)": "which nc",
    "Curl": "curl --version | head -1",
    "Wget": "wget --version | head -1",
    "OpenSSL": "openssl version",
    "Sendmail": "which sendmail",
    "Mail": "which mail",
}

print("\nLimbaje si utilitare disponibile:\n")

for name, cmd in tools.items():
    out = ssh_exec(ssh, cmd)
    if out and "not found" not in out.lower() and "no such" not in out.lower():
        print(f"[OK] {name:15} : {out[:60]}")
    else:
        print(f"[--] {name:15} : Nu este disponibil")

# Check sistem si versiune
print("\n" + "=" * 70)
print("\nInformatii sistem:\n")

print("OS:", ssh_exec(ssh, "cat /etc/*release 2>/dev/null | head -3 || uname -a"))
print("\nKernel:", ssh_exec(ssh, "uname -r"))
print("\nArchitectura:", ssh_exec(ssh, "uname -m"))

ssh.close()

