import platform
import shutil
import os

def _clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def list_commands(prefix):
    for suffix in ["", "3", "2.7", "3.5", "3.6", "3.7", "3.8"]:
        cmd = prefix + suffix
        target = shutil.which(cmd)
        if target is not None:
            print(" -", cmd.ljust(9), "=>", target)

if __name__ == "__main__":
    _clear_screen()
    print("*" * 80)
    print("Some Python commands in PATH:")
    list_commands("python")
    list_commands("pip")
    print("")
    print("*" * 80)
    