import os
import sys
from shutil import which

def recommend_exe(prefix):
    pass

if __name__ == "__main__":
    os.system("clear")
    print("********************************************************************************")
    print("This session is prepared for using Python installation in")
    print(sys.exec_prefix)
    print("")
    print("Some important commands and their full paths:")
    print("python ...", which("python"))
    print("********************************************************************************")
    print("")
    