from thonny.globals import get_workbench

from thonny.plugins.moodle.moodle_view import MoodleView

def _load_plugin():
    get_workbench().add_view(MoodleView, "Moodle", 'nw')
