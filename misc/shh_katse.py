import subprocess

proc = subprocess.Popen(["C:/Users/aivar/Desktop/plink.exe",
                         "-ssh",
                         #"-t",
                         "-batch",
                         "-pw", "pi-top",
                         "pi@pi-top",
                         "python3",
                         "/home/pi/Desktop/prob.py"], 
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         universal_newlines=True)
"""
proc = subprocess.Popen(["C:/Py3/Scripts/python.exe", "-m", "intera"], 
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         universal_newlines=True)
"""


while True:
    c = proc.stdout.read(1)
    print(c, end="")
    if c == ":":
        print("ennekirj")
        proc.stdin.write("Aivar\n")
        proc.stdin.flush()
        print("pealekirj")



    
    