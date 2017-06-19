
app = None

def handle_dataexplore(command_line, main):
    from thonny.common import parse_shell_command
    from pandastable.app import DataExplore
    import tkinter as tk
    global app
    command, args = parse_shell_command(command_line, False)
    
    if app is None:
        app = DataExplore()
    else:
        try:
            app.state()
        except tk.TclError:
            app = DataExplore()
        
    
    if len(args) == 1 and args[0].strip() != "":
        expr = args[0].strip()
        df = eval(expr, main.__dict__)
        app.load_dataframe(df, expr)
        

def load_plugin(vm):
    vm.add_magic_command("dataexplore", handle_dataexplore)    
    vm.add_magic_command("de", handle_dataexplore)
    