import os.path
import thonny

user_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".thonny")
thonny.THONNY_USER_DIR = os.path.abspath(user_dir)