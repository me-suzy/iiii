#!/usr/bin/env python
"""
Ghid pentru configurarea sendmail cu domeniu nou
"""

import sys

def main():
    print("=" * 70)
    print("   GHID PENTRU CONFIGURAREA SENDMAIL CU DOMENIU NOU")
    print("=" * 70)
    print()
    
    print(">> PROBLEMA IDENTIFICATA:")
    print("   - IP-ul 95.196.191.92 nu are domeniu asociat")
    print("   - Gmail vede root@sariasi66.ro ca spam")
    print("   - Trebuie domeniu legitim pentru a evita ban-urile")
    print()
    
    print(">> SOLUTIA COMPLETA:")
    print("   1. Cumpara domeniul academia.iasi.ro (sau altul)")
    print("   2. Configureaza DNS-ul pentru domeniu")
    print("   3. Adauga A record: mail.academia.iasi.ro -> 95.196.191.92")
    print("   4. Adauga PTR record: 95.196.191.92 -> mail.academia.iasi.ro")
    print("   5. Configureaza sendmail sa foloseasca domeniul nou")
    print()
    
    print(">> PASII DETALIATI:")
    print()
    print("   PASUL 1: CUMPARA DOMENIUL")
    print("   - Mergi la GoDaddy, Namecheap, sau alt provider")
    print("   - Cauta domeniul: academia.iasi.ro")
    print("   - Cumpara domeniul (aproximativ 10-15 EUR/an)")
    print()
    print("   PASUL 2: CONFIGUREAZA DNS-UL")
    print("   - Intră în contul de la providerul de domeniu")
    print("   - Mergi la DNS Management")
    print("   - Adauga record A:")
    print("     * Name: mail")
    print("     * Type: A")
    print("     * Value: 95.196.191.92")
    print()
    print("   PASUL 3: CERE PTR RECORD")
    print("   - Contacteaza providerul de internet pentru 95.196.191.92")
    print("   - Cere configurarea PTR record:")
    print("     95.196.191.92 -> mail.academia.iasi.ro")
    print()
    print("   PASUL 4: CONFIGUREAZA SENDMAIL")
    print("   - Modifica sendmail sa foloseasca domeniul nou")
    print("   - From: root@mail.academia.iasi.ro")
    print("   - In loc de: root@sariasi66.ro")
    print()
    
    print(">> ALTERNATIVA RAPIDA:")
    print("   - Foloseste un domeniu pe care il ai deja")
    print("   - Adauga A record: mail.tudomeniu.ro -> 95.196.191.92")
    print("   - Cere PTR record pentru IP-ul tau")
    print()
    
    print(">> BENEFICIILE:")
    print("   - Emailurile nu vor mai fi considerate spam")
    print("   - Gmail, Yahoo, Outlook vor accepta emailurile")
    print("   - Reputatie IP pozitiva")
    print("   - Fara probleme cu blacklist-urile")
    print()
    
    print(">> COSTURI:")
    print("   - Domeniu: 10-15 EUR/an")
    print("   - Configurare DNS: GRATUIT")
    print("   - PTR record: GRATUIT (de la providerul de internet)")
    print()
    
    print("=" * 70)
    print("INSTRUCTIUNI COMPLETE!")
    print("=" * 70)
    print()
    print("Dupa ce cumperi domeniul si configurezi DNS-ul,")
    print("pot sa configurez sendmail sa foloseasca domeniul nou.")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[WARN] Script intrerupt.")
        sys.exit(130)
