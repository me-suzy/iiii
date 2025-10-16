#!/usr/bin/env python
"""
Ghid pentru cererea de excludere de la Spamhaus PBL
"""

import webbrowser
import sys

def main():
    print("=" * 70)
    print("   GHID PENTRU CEREREA DE EXCLUDERE DE LA SPAMHAUS PBL")
    print("=" * 70)
    print()
    
    print(">> PROBLEMA IDENTIFICATA:")
    print("   - IP-ul 95.196.191.92 este pe Spamhaus PBL")
    print("   - PBL este pentru IP-uri care nu ar trebui sa trimita email direct")
    print("   - NU este o problema majora - este standard pentru broadband")
    print()
    
    print(">> SOLUTIA:")
    print("   1. Cere excludere de la PBL pentru ca rulezi un mail server")
    print("   2. Configureaza SMTP auth cu Gmail ca relay extern")
    print()
    
    print(">> PASII PENTRU EXCLUDERE DE LA PBL:")
    print("   1. Mergi la: https://check.spamhaus.org")
    print("   2. Introdu IP-ul: 95.196.191.92")
    print("   3. Click pe 'More Info' pentru a vedea politica ISP-ului")
    print("   4. Bifeaza: 'I am running my own mail server'")
    print("   5. Cere excluderea")
    print()
    
    print(">> DETALII IMPORTANTE:")
    print("   - Excluderile sunt valabile pentru 1 an")
    print("   - Daca IP-ul se listeaza pe alte blocklist-uri, se relisteaza automat pe PBL")
    print("   - Trebuie sa demonstrezi ca rulezi un mail server legitim")
    print()
    
    print(">> ALTERNATIVA - SMTP AUTH CU GMAIL:")
    print("   - Configureaza sendmail sa foloseasca Gmail ca relay extern")
    print("   - Foloseste autentificare SMTP cu credidentialele Gmail")
    print("   - Evita complet problemele cu blocklist-urile")
    print()
    
    # Deschide link-ul automat
    try:
        print(">> DESCHID LINK-UL SPAMHAUS...")
        webbrowser.open("https://check.spamhaus.org")
        print("[OK] Link deschis in browser!")
    except:
        print("[WARN] Nu am putut deschide link-ul automat")
        print("       Mergi manual la: https://check.spamhaus.org")
    
    print()
    
    print("=" * 70)
    print("INSTRUCTIUNI COMPLETE!")
    print("=" * 70)
    print()
    print("Am identificat problema exacta: IP-ul este pe Spamhaus PBL.")
    print("Urmareste pasii de mai sus pentru cererea de excludere.")
    print()
    print("Daca nu poti cere excluderea, pot configura SMTP auth cu Gmail.")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[WARN] Script intrerupt.")
        sys.exit(130)
