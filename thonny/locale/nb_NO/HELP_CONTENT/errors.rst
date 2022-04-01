Forstå feilmeldinger
====================

Hvis programmet ditt gir feilmeldinger eller feil resultater er det viktig at du ikke prøver å
fikse noe før du forstår problemet. Du kan lese mer om dette på en `annen side <debugging.rst>`__,
men her er en rask sjekkliste for å komme i gang med feilsøkingen. 

Er du redd?
-----------
Ikke få panikk! Feilmeldinger er ment for å hjelpe deg. Hvis du får en feilmelding så betyr det
ikke at du er en dårlig programmerer. Og ta det med ro, du har ikke ødelagt datamaskinen. Selv om
feilmeldinger kan se helt uforståelige ut ved første øyekast, så kan man, med litt øvelse, hente
mye nyttig informasjon fra dem. 

Hvor i koden skjedde feilen?
----------------------------
Feilmeldinger i Thonny inneholder en eller flere lenker som kan flytte deg til det stedet i koden
som førte til feilen. I tilfellene hvor du får flere lenker er det gjerne den siste lenken som er
mest relevant. 
 
Hvis feilen skjedde inne i en funksjon, så inneholder feilmeldingen flere lenker. Prøv å trykke på
dem en etter en fra topp til bunn for å se hvordan Python havnet på stedet hvor feilen skjedde. En
sånn samling lenker heter *stakksporet* (*the stack trace*).

Hva betyr feilemeldingen?
-------------------------
Den siste linja i feilmeldings-blokka sier hva problemet var for Python. Når du prøver å forstå
denne beskjeden må du ikke glemme konteksten rundt. Prøv og finn sammenhengen mellom deler av
beskjeden og området i koden som den lenker til. Noen ganger kan Thonnys Assistent forklare
feilbeskjeden med enklere ord og noen ganger må du søke på nettet (Husk å legge til "Python"
som søkeord). 

Hva var innholdet til variablene i det feilen skjedde?
------------------------------------------------------
Åpne variablene og se selv! Hvis feilen skjedde inne i en funksjon så kan du se på de lokale
variablene ved å trykke på lenkene i stakksporet. 

Hvordan ble feilen til?
-----------------------
Se `siden om feilsøking <debugging.rst>`_ eller `siden om å bruke Thonnys feilsøkere <debuggers.rst>`_.