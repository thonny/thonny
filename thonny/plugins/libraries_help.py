from thonny.globals import get_workbench
import webbrowser
def load_plugin():
    get_workbench().add_command("pygame_help", "help", "Installing extra packages",
                                lambda: webbrowser.open("https://bitbucket.org/plas/thonny/wiki/InstallingPackages"),
                                group=30)
