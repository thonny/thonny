from operator import abs

from jedi import Script

code = """print(end"""
s = Script(code=code)
comps = s.complete(line=1, column=len(code), fuzzy=True)

for comp in comps:
    print("--------------------------")
    """
    for name in dir(comp):
        if not name.startswith("_"):
            print(name, ":", getattr(comp, name))
    """
    print(comp.name, comp.get_completion_prefix_length())
