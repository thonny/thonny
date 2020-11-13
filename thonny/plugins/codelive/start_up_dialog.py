from tkinter import Toplevel, Label, Button, Frame

class StartUpDialog(Toplevel):
    def __init__(self, master=None, **options):
        super().__init__(master, options)
        self._client_username = ""
        self._host_username = ""
        self._auth_token = ""
        self._max_num_users = ""

        self._pages = {"welcome":      self.welcome_page(),
                       "client_page":  self.client_setup(),
                       "host_page":    self.host_setup()}
        
    
    def welcome_page(self):
        page = Frame(master=self,
                     width=100)
        Label(master = page,
              text="Please choose your session",
              height=30,
              width=50).pack()

        Button(master=page,
               text="Host").pack()
        Button(master=page,
               text="Client").pack()
        page.pack()
        pass
    
    def client_setup(self):
        return ""

    def host_setup(self):
        return ""

    def run(self):
        return {}
    
    def getInfo(self):
        return "Host"
