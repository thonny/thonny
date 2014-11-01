import sys
import os.path

if "" in sys.path:
    sys.path.remove("") # don't want current directory in path

# Where are we?
assert(__file__)
src_dir = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))
sys.path.insert(0, os.path.normpath(os.path.join(src_dir, os.pardir)))


from thonny import main
main.Thonny(src_dir).mainloop()    