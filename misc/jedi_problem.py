from jedi import Script

s = Script(source="a\n", line=1, column=0, path="test.py")
s.goto_definitions()
print("After first")

s = Script(source="'\n", line=1, column=0, path="test.py")
s.goto_definitions()
print("After second")
