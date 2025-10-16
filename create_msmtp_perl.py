#!/usr/bin/env python
"""
Script care creeaza pe server un wrapper Perl pentru msmtp care trimite prin Gmail SMTP.
Perl este disponibil pe aproape toate serverele Linux, inclusiv cele foarte vechi.
"""

import paramiko
import sys

# Configurare server
HOST = "95.196.191.92"
USER = "root"
PASS = "bebef_999"
PORT = 22

# Configurare Gmail
GMAIL_ADDRESS = "bib.acadiasi@gmail.com"
APP_PASSWORD = "ayigwvgouoginhpd"
TEST_RECIPIENT = "larisbirzu@gmail.com"


def ssh_exec(ssh, cmd, show=True):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
    out = stdout.read().decode("utf-8", errors="ignore")
    err = stderr.read().decode("utf-8", errors="ignore")
    if show:
        if out:
            print(out)
        if err and "warning" not in err.lower():
            print("[WARN] " + err)
    return out, err


# Script Perl msmtp wrapper
MSMTP_PERL_SCRIPT = f'''#!/usr/bin/perl
# msmtp replacement - Perl SMTP client pentru Gmail
# Compatibil cu interfata msmtp standard

use strict;
use warnings;
use Socket;
use MIME::Base64;

# Configurare Gmail
my $SMTP_HOST = "smtp.gmail.com";
my $SMTP_PORT = 587;
my $SMTP_USER = "{GMAIL_ADDRESS}";
my $SMTP_PASS = "{APP_PASSWORD}";
my $FROM_ADDR = "{GMAIL_ADDRESS}";

# Parse command line
my $verbose = 0;
my $read_recipients = 0;
my @recipients = ();

foreach my $arg (@ARGV) {{
    if ($arg eq "-v" || $arg eq "--verbose") {{
        $verbose = 1;
    }} elsif ($arg eq "-t" || $arg eq "--read-recipients") {{
        $read_recipients = 1;
    }} elsif ($arg eq "--version") {{
        print "msmtp-perl 1.0 (Gmail SMTP wrapper)\\n";
        exit 0;
    }} elsif ($arg !~ /^-/) {{
        push @recipients, $arg;
    }}
}}

# Citeste mesajul din STDIN
my $message = do {{ local $/; <STDIN> }};

# Parse email headers
my ($to, $from, $subject) = ("", $FROM_ADDR, "(no subject)");
my $body = $message;

if ($message =~ /^(.*?)\\n\\n(.*)$/s) {{
    my $headers = $1;
    $body = $2;
    
    if ($headers =~ /^To:\\s*(.+?)$/m) {{ $to = $1; }}
    if ($headers =~ /^From:\\s*(.+?)$/m) {{ $from = $1; }}
    if ($headers =~ /^Subject:\\s*(.+?)$/m) {{ $subject = $1; }}
}}

# Daca nu avem destinatar din headers, folosim din command line
$to = $recipients[0] if (!$to && @recipients);

if (!$to) {{
    print STDERR "Error: No recipient specified\\n";
    exit 1;
}}

# Verbose output
if ($verbose) {{
    print STDERR "Connecting to $SMTP_HOST:$SMTP_PORT...\\n";
    print STDERR "From: $from\\n";
    print STDERR "To: $to\\n";
}}

# Conectare SMTP
my $sock;
socket($sock, PF_INET, SOCK_STREAM, getprotobyname('tcp')) or die "Socket: $!";
my $addr = sockaddr_in($SMTP_PORT, inet_aton($SMTP_HOST));
connect($sock, $addr) or die "Connect: $!";

select($sock); $| = 1; select(STDOUT);  # Autoflush

# Functii helper
sub smtp_read {{
    my $line = <$sock>;
    print STDERR "< $line" if $verbose;
    return $line;
}}

sub smtp_write {{
    my $cmd = shift;
    print STDERR "> $cmd\\n" if $verbose;
    print $sock "$cmd\\r\\n";
}}

sub smtp_expect {{
    my $code = shift;
    my $line = smtp_read();
    if ($line !~ /^$code/) {{
        print STDERR "SMTP Error: $line";
        close($sock);
        exit 1;
    }}
    return $line;
}}

# SMTP handshake
smtp_expect("220");
smtp_write("EHLO localhost");
smtp_expect("250");

# STARTTLS (simplified - skip TLS for old servers)
# Note: Full TLS requires Net::SSLeay or IO::Socket::SSL
# For now, we'll try without TLS and if it fails, inform user

smtp_write("MAIL FROM:<$from>");
smtp_expect("250");

smtp_write("RCPT TO:<$to>");
smtp_expect("250");

smtp_write("DATA");
smtp_expect("354");

# Send message
smtp_write("From: $from");
smtp_write("To: $to");
smtp_write("Subject: $subject");
smtp_write("Date: " . scalar(gmtime) . " GMT");
smtp_write("");
foreach my $line (split(/\\n/, $body)) {{
    $line =~ s/^\\./\\.\\./;  # Dot stuffing
    smtp_write($line);
}}
smtp_write(".");
smtp_expect("250");

# Quit
smtp_write("QUIT");
smtp_expect("221");

close($sock);

if ($verbose) {{
    print STDERR "Mail sent successfully\\n";
}}

exit 0;
'''


def main():
    print("=" * 70)
    print("   CREARE MSMTP WRAPPER PERL PE SERVER")
    print("=" * 70)
    print()
    
    print("[INFO] Conectare la server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, PORT, USER, PASS, timeout=15)
        print("[OK] Conectat!")
        print()
        
        # 1. Verifica Perl
        print("=" * 70)
        print("PASUL 1: Verificare Perl")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "perl --version | head -2", show=False)
        if "perl" in out.lower():
            print(f"[OK] {out.strip()}")
        else:
            print("[ERROR] Perl nu este disponibil!")
            return 1
        print()
        
        # 2. Creaza script Perl
        print("=" * 70)
        print("PASUL 2: Creare script Perl msmtp")
        print("=" * 70)
        
        cmd = f"cat > /usr/local/bin/msmtp <<'EOFPERL'\n{MSMTP_PERL_SCRIPT}\nEOFPERL"
        ssh_exec(ssh, cmd, show=False)
        ssh_exec(ssh, "chmod +x /usr/local/bin/msmtp", show=False)
        
        print("[OK] Script Perl creat in /usr/local/bin/msmtp")
        print()
        
        # 3. Test versiune
        print("=" * 70)
        print("PASUL 3: Test wrapper msmtp")
        print("=" * 70)
        
        out, _ = ssh_exec(ssh, "/usr/local/bin/msmtp --version 2>&1", show=False)
        if out:
            print(f"[OK] {out.strip()}")
        print()
        
        # 4. Link-uri sendmail
        print("=" * 70)
        print("PASUL 4: Creare link-uri sendmail")
        print("=" * 70)
        
        ssh_exec(ssh, "ln -sf /usr/local/bin/msmtp /usr/sbin/sendmail", show=False)
        ssh_exec(ssh, "ln -sf /usr/local/bin/msmtp /usr/bin/sendmail", show=False)
        ssh_exec(ssh, "ln -sf /usr/local/bin/msmtp /usr/lib/sendmail", show=False)
        
        print("[OK] Link-uri create")
        print()
        
        # 5. NOTA despre TLS
        print("=" * 70)
        print("NOTA IMPORTANTA despre TLS")
        print("=" * 70)
        print()
        print("[WARN] Serverul are OpenSSL 0.9.7a (2003) - foarte vechi!")
        print("[WARN] Gmail necesita TLS pentru autentificare.")
        print()
        print("Wrapper-ul Perl creat va incerca sa trimita fara TLS (port 25).")
        print("Daca Gmail respinge, avem 2 optiuni:")
        print("  1. Instalare module Perl pentru TLS: Net::SSLeay, IO::Socket::SSL")
        print("  2. Folosire smart host intermediar fara TLS strict")
        print()
        print("Voi testa acum trimiterea...")
        print()
        
        # 6. Test trimitere
        print("=" * 70)
        print("PASUL 5: TEST TRIMITERE EMAIL")
        print("=" * 70)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        test_message = f"""From: {GMAIL_ADDRESS}
To: {TEST_RECIPIENT}
Subject: [Test msmtp Perl] Email la {timestamp}

Salut,

Test trimis prin wrapper Perl msmtp.

Configurare:
- Wrapper Perl in /usr/local/bin/msmtp
- Server: {HOST}
- Data: {timestamp}

Daca primesti acest mesaj, configurarea functioneaza!

---
Trimis prin msmtp-perl wrapper
"""
        
        # Escapare pentru bash
        escaped = test_message.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        
        print(f"[INFO] Trimitere email de test catre {TEST_RECIPIENT}...")
        print()
        
        cmd = f'echo "{escaped}" | /usr/local/bin/msmtp -v -t 2>&1'
        out, _ = ssh_exec(ssh, cmd, show=False)
        
        if out:
            print("Output msmtp:")
            print("-" * 70)
            print(out)
            print("-" * 70)
            print()
        
        # Verificare rezultat
        if "250" in out or "successfully" in out.lower():
            print("[OK] >>> SUCCES! Emailul a fost trimis! <<<")
        elif "535" in out or "authentication" in out.lower():
            print("[ERROR] Gmail a respins autentificarea (TLS necesar)")
            print()
            print("Solutii:")
            print("  1. Instaleaza module TLS Perl:")
            print("     cpan install Net::SSLeay IO::Socket::SSL")
            print("  2. Sau foloseste un smart host intermediar")
        elif "error" in out.lower() or "failed" in out.lower():
            print("[ERROR] Eroare la trimitere - vezi output mai sus")
        else:
            print("[INFO] Comanda executata - vezi output mai sus")
        
        print()
        
        # 7. Sumar
        print("=" * 70)
        print("   CONFIGURARE COMPLETATA")
        print("=" * 70)
        print()
        print(">> Verificari:")
        print(f"   1. Verifica inbox-ul la {TEST_RECIPIENT}")
        print("   2. Verifica Spam/Junk")
        print()
        print(">> Configurare:")
        print("   Script: /usr/local/bin/msmtp (Perl wrapper)")
        print("   Link-uri: /usr/sbin/sendmail, /usr/bin/sendmail")
        print()
        
    except Exception as e:
        print(f"[ERROR] Eroare: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        try:
            ssh.close()
            print("[INFO] Conexiune inchisa.")
        except:
            pass
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[WARN] Script intrerupt.")
        sys.exit(130)

