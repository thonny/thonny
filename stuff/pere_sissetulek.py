def neto(bruto):
    maksuvaba = 144
    if (bruto <= maksuvaba):
        return bruto
    else:
        maksustatav = bruto - maksuvaba
        return maksustatav * 0.79 + maksuvaba

lapsetoetus = 20
ema_bruto = float(input('Sisesta ema brutopalk: '))
isa_bruto = float(input('Sisesta isa brutopalk: '))
laste_arv = int(input('Sisesta alaealiste laste arv: '))

sissetulek = neto(ema_bruto) + neto(isa_bruto) \
     + laste_arv * lapsetoetus

print('Pere sissetulek kuus on ' 
     + str(sissetulek) + ' eurot.')
