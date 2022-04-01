Shell 
=====
Shell er hovedmåten du kjører og kommuniserer med, programmet ditt. 
Shell ligner for det meste på offisiell Python REPL (Read-Evaluate-Print Loop), 
men kommer med noen forskjeller og litt ekstra funksjonalitet

Pythonkommandoer
---------------
Akkurat som for den offisielle Python REPL, så aksepterer Thonnys Shell også Pythonkode, både enkeltlinje og mulitlinje. 
Hvis du trykker på enter tasten, så bruker Thonny noen algoritmer til å gjette om du ønsker å sende inn kommandoen eller å fortsette å skrive på neste linje. 
Hvis Thonny gir deg en ny linje når du egentlig ønsket å sende kommandoen bør du dobbeltsjekke om du glemte å lukke en parentes eller liknende. 

Magiske kommandoer
------------------
Hvis du velger “Kjør => Kjør gjeldene skript” eller trykker på f5 knappen, så ser du at Thonny skriver inn en kommando som starter med ``%Run`` inn i Shell. 
Kommandoer som starter med ``%`` kalles *magiske kommandoer* (slik som i `IPython <https://ipython.org/>`_ ) og brukes for enkelte oppgaver som ikke (enkelt) kan beskrives som Python kommandoer. 
De aller fleste slike magiske kommandoer har en tilsvarende knapp i menyen, så du slipper å skrive de for hånd. 

Systemkommandoer
----------------
For å kjøre en enkel systemkommando raskt uten å starte en Terminal kan du skrive inn kommandoen med et utropstegn ``!`` foran ` (f.eks. ``!pytest mitt-skript.py``) rett inn i Thonnys Shell.

Kommandohistorie
----------------
Hvis du vil gi samme eller lik kommando flere ganger uten å skrive inn hele kommandoen på nytt, 
så kan du bruke opp-tasten til å hente inn forrige kommando fra kommando historien. 
Trykker du opp en gang til går du et hakk til tilbake i historien. 
For å gå fremover i historien kan du bruke ned-tasten.

Utskrift med farger
-------------------
Hvis du har Shell i terminal emulator modus (under Verktøy => Alternativer... => Shell) kan du bruke såkalte `ANSI koder  <https://en.wikipedia.org/wiki/ANSI_escape_code>`_ for å få farger på utskriften. 
Prøv følgende eksempel:
.. code::

    print("\033[31m" + "Rød" + "\033[m")
    print("\033[1;3;33;46m" + "Lys&fet kursiv gul text på turkis bakgrunn" + "\033[m")

Fargekodene kan være vanskelige å huske og du kan bruke et bibliotek som `colorama <https://pypi.org/project/colorama/>`_ for å hjelpe deg å produsere riktige fargekoder.


Skrive over utskrift
--------------------
Mer fullstendige terminator emulatorer støtter ANSI kode som tillater at du skriver til tilfeldige posisjoner i terminal skjermen. 
Thonnys Shell er ikke så avansert at den støtter det, men den støtter noen enklere triks du kan bruke. 
Prøv for eksempel følgende program:

.. code::

	from time import sleep
	
	for i in range(100):
	    print(i, "%", end="")
	    sleep(0.05)
	    print("\r", end="")
	
	print("Ferdig!")


Dette trikset bruker ``"\r"`` tegnet som flytter utskriftsmarkøren tilbake til begynnelsen av den gjeldende linja slik at neste ``print`` kommando vil overskrive den gamle utskriften. 
Legg merke til at vi bruker ``print(..., end="")`` for å unngå linjeskift.

``"\b"`` er en nær slekning av  ``"\r"`` som flytter utksriftsmarkøren et tegn til venstre (``"\b"`` gjør ingenting hvis du allerede er på den første posisjonen i linja)

		
Lage lyd
--------
Når Shell er satt til terminal emulator modus (under Verktøy => Alternativer... => Shell) kan du lage en bjellelyd (plingelyd) ved å skrive ut tegnet ``"\a"``.

Vise frem bilder
-----------------
Du kan vise frem bilder i Shell ved å enkode en GIF eller PNG fil med Base64 og skrive den ut som en enkeltlinje data URL

.. code::

	print("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==")

Plotte en serie av tall (tegne graf)
------------------------------------
Du kan visualisere en serie med tall som er skrevet ut til Shell ved å bruke `Plotteren<plotter.rst>`_.
