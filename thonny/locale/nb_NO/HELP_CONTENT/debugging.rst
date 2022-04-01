Teknikker for feilsøking
========================

Ikke få panikk hvis programmet ditt ikke fungerer som det skal. 
Det er flere mulige strategier for å løse problemet, for eksempel:

* La noen andre fikse feilen
* Endre *et eller annet* i koden og kjør på nytt
* Nærm deg problemet i to faser: 1) Finn problemet og 2) fiks problemet

Det å be noen andre fikse feilen kan fungere godt, men vil ikke gi deg den flotte mestringsfølelsen. 
Uansett er lurest å vente med denne strategien til man har prøvd litt på egenhånd først. 

Hvis programmene dine er små, så kan du treffe blink med å endre noe tilfeldig å kjøre koden på nytt helt til det fungerer, men det er lite sannsynlig. 
Og selv hvis du tilslutt får koden til å kjøre med denne strategien, så har du ikke vunnet, for du lærer jo lite hvis du hverken forstår problemet eller løsningen.

Hvis du ønsker å bli god til å programmere, så må du bruke en mer systematisk strategi. 
Dette betyr blant annet at du må snevre inn på akkurat hva det er som fikk programmet ditt til å gjøre feil, før du prøver å fikse det. 
Prosessen for å søke etter årsaken bak problemet, kalles gjerne *feilsøking* eller *debugging*. 

Følge programflyten / tenke som Python   
---------------------------------------
Sannsynligvis er ikke koden din fullstendig feil. 
Det kan være en skrivefeil et sted eller kanskje du overså eller missforsto en liten, men kritisk detalj. 
*NB! Ikke få for vane å tenke at Python har misforstått deg – Python er en maskin og prøver ikke å forstå deg, den gjør bare nøyaktig det du ber om.*
Nøkkelen for effektiv feilsøking er å finne nøyaktig hvor og når dine antagelser om hva programmet skal gjøre ikke stemmer med hva som faktisk skjer. 

Hvis, for eksempel, programmet ditt skriver ut et feil svar tilslutt, så gir det litt informasjon om programmets oppførsel, 
men det er sjeldent nok for å finne nøyaktig hvor problemet ligger.
Du må også sjekke hvilke av de **foregående stegene** som stemmer med dine antagelser og hvilke som ikke gjør det.  

En enkel (og veldig nyttig) teknikk er å legge inn **ekstra print kommandoer** i koden som forteller deg hvor Python er og hva som er oppnådd så langt, f.eks:
.. code::

	print("venner før for-løkke", venner)

NB! Av og til trenger du å opprette nye variabler og bryte kompliserte uttrykk inn i mindre biter for å kunne skrive ut mer detaljert informasjon med print

Selv om ``print``-feilsøking er mye brukt, selv blant profesjonelle (de kaller det gjerne *logging*), 
så finnes det et alternativ som ofte er enda mer intuitivt. Det kalles å **gå igjennom koden stegvis** og er noe Thonny er laget spesifikt for. 
Les `Å bruke feilsøkere <debuggers.rst>`_ guiden for å lære mer. 

Kodegjennomgang 
---------------------
En annen nyttig teknikk er kodegjennomgang. 
Det er ganske likt som å gå igjennom koden steg for steg, men du gjør det i hodet ditt og prøver å fokusere på det større bildet. 
Se på alle kommandoer i progammet ditt og prøv å forstå meningen bak hver av dem og hvordan de henger sammen med oppgaven du prøver å løse. 


Still deg selv følgende spørsmål for hver **variabel**:

* Beskriver navnet til variabelen hva hensikten til variabelen er? Er det bedre å bruke entall eller flertall i variabelnavnet?
* Hva slags type verdier vil kunne havne i denne variabelen? Tekststrenger, heltall, lister av strenger, lister av flyttal ...?
* Hvilken rolle har variabelen i programmet? Skal den, for eksempel, oppdateres underveis i programmet slik at den inneholder nyttig informasjon til slutt? Skal den inneholde samme informasjon hele tiden, men brukes flere steder for å unngå at en verdi må klipp-og-limes inn mange steder? Har den en helt annen rolle?

Still deg selv følgende spørsmål for hver **løkke**:

* Hvordan vet du at programmet trenger en løkke?
* Hvor mange ganger skal innholdet i løkka kjøres? Hva bestemmer dette antallet?
* Hvilke kodelinjer bør være inne i løkka og hvilke bør være utenfor?
* Hva må gjøres før løkka og hva må gjøres etter løkka?

Still deg selv følgende spørsmål for hvert **samensatte uttrykk**:

* I hvilken rekkefølge bør hver del av uttrykket evalueres i? Er Python enig i rekkefølgen? Hvis du er i tvil er det lurt å bruke feilsøkingsverktøy eller introdusere hjelpevariabler og bryte opp uttrykket i mindre biter. 
* Hva slags type verdi skal komme ut av uttrykket? Tekststreng? Heltall? Liste av heltall? Noe annet?

Det kan også hende at du mangler noen viktige deler i programmet ditt:

* Krever problemet du skal løse at du behandler forskjellige situasjoner ulikt? I så fall trenger du sannsynligvis ``if`` nøkkelordet og en betingelse
* Krever problemet du skal løse at du gjør noe flere ganger? I så fall trenger du sannsynligvis en løkke. 

Fortsatt forvirret?
------------------------------
"Finn stedet der antagelsene dine brytes" -- Dette er definitivt enklere sagt enn gjort. 
For større, mer kompliserte programmer er det lett å havne i en situasjon hvor du ikke lenger er sikker på hva du antar eller hvorfor du startet å programmere i utgangspunktet. 

I slike tilfeller er det nyttig å forenkle problemet ditt så mye som mulig og prøve å skrive kode som løser det forenklete problemet først. 
Åpne en blank fil og start enten fra grunnen av igjen eller med å kopiere inn eksisterende kode og slett alt som ikke er nødvendig for å løse det forenklete problemet. Et eksempel på en forenkling kan være å anta at brukeren av programmet ditt er veldig samarbeidsvillig og sender alltid inn "god" og gyldig data. 
Eller hvis problemet krever at du gjør noe gjentatte ganger kan du forenkle ved å glemme "gjentagelsen". Hvis problemet krever en komplisert betingelse kan du prøve å forenkle betingelsen, osv. 

Etter å ha løst den forenklede utgaven av problemet har du sannsynligvis lært noe nytt om programmet ditt og du er nok bedre rustet til å løse det fulle problemet også. 
