from thonny.config_ui import ConfigurationPage
from thonny import get_workbench


class AssistantConfigPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)
        
        self.add_checkbox("assistance.open_assistant_on_errors",
                          "Open Assistant automatically when program crashes with an exception")
            
        self.add_checkbox("assistance.open_assistant_on_warnings",
                          "Open Assistant automatically when it has warnings for your code")


def load_plugin():
    get_workbench().add_configuration_page("Assistant", AssistantConfigPage)