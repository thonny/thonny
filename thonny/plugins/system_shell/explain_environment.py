import platform
import shutil
import sys
import os.path

def _clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def equivalent_realpath(p):
    pdir = os.path.dirname(p)
    if os.path.isfile(os.path.join(pdir, "activate")):
        # it's a virtual environment
        # can use realpath only if it doesn't move out of its dir
        real = os.path.realpath(p)
        if os.path.dirname(real) == pdir:
            return real
        try:
            link = os.readlink(p)
            if not os.path.isabs(link):
                link = os.path.join(pdir, link)
            link = os.path.normpath(link)
            if os.path.dirname(link) == pdir:
                return link
            return p
        except:
            return p
    else:
        return os.path.realpath(p)

def is_virtual_exe(p):
    pdir = os.path.dirname(p)
    return (
        os.path.exists(os.path.join(pdir, "activate"))
        or os.path.exists(os.path.join(pdir, "activate.bat"))
    )

def list_commands(prefix, highlighted_reals, highlighted_dirs):
    for suffix in ["", "3", "3.5", "3.6", "3.7", "3.8"]:
        cmd = prefix + suffix
        target = shutil.which(cmd)
        if target is not None:
            real = equivalent_realpath(target)
            
            if target == real:
                relation = "=="
            else:
                relation = "->"
                
            line = " - " + cmd.ljust(9) + " " + relation + " " + real
            if (real in highlighted_reals
                or os.path.dirname(real) in highlighted_dirs
                or os.path.dirname(target) in highlight_dirs):
                print("\033[1m" + line + "\033[0m")
            else:
                print(line)

if __name__ == "__main__":
    _clear_screen()
    print("*" * 80)
    print("Some Python commands in PATH:")
    
    sys_real = equivalent_realpath(sys.executable)
    if is_virtual_exe(sys.executable):
        highlight_dirs = os.path.dirname(sys.executable)
    else:
        highlight_dirs = []
    
    if platform.system() == "Windows":
        # Add Scripts for pip
        highlight_dirs.append(os.path.join(os.path.dirname(sys_real), "Scripts"))
        highlight_dirs.append(os.path.join(os.path.dirname(sys.executable), "Scripts"))
            
    list_commands("python", [sys_real], highlight_dirs)
    
    likely_pips = []
    if sys_real[-9:-1] == "python3.":
        likely_pips.append(sys_real[:-9] + "pip3." + sys_real[-1])
    if sys.executable.endswith("/python3"):
        # This is not as likely match as previous, but still quite likely
        likely_pips.append(sys.executable.replace("/python3", "/pip3"))
        
    list_commands("pip", likely_pips, highlight_dirs)
    
    print("")
    print("*" * 80)
    
