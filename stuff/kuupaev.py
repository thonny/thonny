def kuu_nimi(kuu):
    if kuu == 1:
        return 'jaanuar'
    elif kuu == 2:
        return 'veebruar'
    elif kuu == 3:
        return 'marts'
    elif kuu == 4:
        return 'aprill'
    elif kuu == 5:
        return 'mai'
    elif kuu == 6:
        return 'juuni'
    elif kuu == 7:
        return 'juuli'
    elif kuu == 8:
        return 'august'
    elif kuu == 9:
        return 'september'
    elif kuu == 10:
        return 'oktoober'
    elif kuu == 11:
        return 'november'
    elif kuu == 12:
        return 'detsember'


def kuupaev_sonena(paev, kuu, aasta):
    return str(paev) + '. ' + kuu_nimi(kuu) \
        + ' ' + str(aasta)


paev = int(input('Sisesta paev numbriga: '))
kuu = int(input('Sisesta kuu numbriga: '))
aasta = int(input('Sisesta aasta numbriga: '))

print(kuupaev_sonena(paev, kuu, aasta))
