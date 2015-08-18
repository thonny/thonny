import sys
import os.path

# This may be executed without parent of thonny src folder being in path
# Where are we?
assert(__file__)
src_dir = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir, os.pardir))
sys.path.insert(0, os.path.normpath(os.path.join(src_dir, os.pardir)))
if sys.argv[0] in sys.path:
    sys.path.remove(sys.argv[0]) # .../thonny/thonny

import thonny.plugins.replay.replayer as rep
rep.run()