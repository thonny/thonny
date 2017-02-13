from thonny.running import BackendProxy
from thonny.globals import get_workbench


class MicrobitProxy(BackendProxy):
    @classmethod
    def get_configurations():
        return [""]
    
    


def load_early_plugin():
    get_workbench().add_backend("BBC micro:bit", MicrobitProxy)
        
        