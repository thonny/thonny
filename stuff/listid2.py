mehed = ["Kalle", "Peeter", "Jaan"]
naised = ["Malle", "Triin", "Mari", "Tiina"]

lisanimi = input("Sisesta yks naisenimi: ")
naised = naised + [lisanimi]

koik_nimed = mehed + naised

for nimi in koik_nimed:
    if nimi in mehed:
        tiitliga_nimi = "hr. " + nimi
    else:
        tiitliga_nimi = "pr. " + nimi
        
    print(tiitliga_nimi)

