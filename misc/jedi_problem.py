from operator import abs

from jedi import Script

s = Script(code="""def mula(muusa:int, puusa:str) -> str:
    x = "dadocstring"
    return puusa
musi = 3
suur = 4
mula(mu""")
comps = s.complete(line=6, column=7, fuzzy=True)

ii = 3

ss = "asdf"

def kala(x: int):
    return x



def showsig(x):
    if not x:
        return x
    return x[0].to_string() + "(%s, %s)" % (x[0].index, x[0].bracket_start)

for comp in comps:
    print(comp, comp.type, showsig(comp.get_signatures()), comp.docstring(raw=True, fast=True), sep=" | ")
