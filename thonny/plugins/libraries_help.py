from thonny.globals import get_workbench
import webbrowser
def load_plugin():
    get_workbench().add_command("pygame_help", "help", "Using Pygame",
                                lambda: webbrowser.open("https://bitbucket.org/plas/thonny/wiki/Pygame"),
                                group=30)
    get_workbench().add_command("pygame_help", "help", "Using scientific libraries",
                                lambda: webbrowser.open("https://bitbucket.org/plas/thonny/wiki/ScientificPython"),
                                group=30)
