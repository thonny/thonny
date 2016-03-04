from thonny import exersys

class VPLExercisePlugin(exersys.Plugin):
    pass

def load_plugin():
    exersys.add_plugin(VPLExercisePlugin())
