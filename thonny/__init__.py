import os.path
import sys
import runpy

try:
    runpy.run_module("thonny.customize", run_name="__main__")
except ImportError:
    pass


THONNY_USER_DIR = os.environ.get("THONNY_USER_DIR", 
                                 os.path.expanduser(os.path.join("~", ".thonny")))

THONNY_USER_BASE = os.path.join(THONNY_USER_DIR, "plugins")

def launch():
    _prepare_thonny_user_dir()
    
    try:
        _update_sys_path()
        
        from thonny import workbench
        
        if _should_delegate():
            # First check if there is existing Thonny instance to handle the request
            delegation_result = _try_delegate_to_existing_instance(sys.argv[1:])
            if delegation_result == True:
                # we're done
                print("Delegated to an existing Thonny instance. Exiting now.")
                return
            
            if hasattr(delegation_result, "accept"):
                # we have server socket to put in use
                server_socket = delegation_result
            else:
                server_socket = None
                 
            bench = workbench.Workbench(server_socket)
        else:
            bench = workbench.Workbench()
            
        try:
            bench.mainloop()
        except SystemExit:
            bench.destroy()
        return 0
    except SystemExit as e:
        from tkinter import messagebox
        messagebox.showerror("System exit", str(e))
    except:
        from logging import exception
        exception("Internal error")
        import tkinter.messagebox
        import traceback
        tkinter.messagebox.showerror("Internal error", traceback.format_exc())
        return -1
    finally:
        from thonny.globals import get_runner
        runner = get_runner()
        if runner != None:
            runner.kill_backend()


def _prepare_thonny_user_dir():
    if not os.path.exists(THONNY_USER_DIR):
        os.makedirs(THONNY_USER_DIR, mode=0o700, exist_ok=True)
        
        # user_dir_template is a post-installation means for providing
        # alternative default user environment in multi-user setups
        template_dir = os.path.join(os.path.dirname(__file__), "user_dir_template")
                    
        if os.path.isdir(template_dir):
            import shutil
            
            def copy_contents(src_dir, dest_dir):
                # I want the copy to have current user permissions
                for name in os.listdir(src_dir):
                    src_item = os.path.join(src_dir, name)
                    dest_item = os.path.join(dest_dir, name)
                    if os.path.isdir(src_item):
                        os.makedirs(dest_item, mode=0o700)
                        copy_contents(src_item, dest_item)
                    else:
                        shutil.copyfile(src_item, dest_item)
                        os.chmod(dest_item, 0o600)
                        
            copy_contents(template_dir, THONNY_USER_DIR)
            

def _update_sys_path():
    import site
    
    # remove old dir from path
    if site.getusersitepackages() in sys.path:
        sys.path.remove(site.getusersitepackages())
        
    # compute usersitepackages that plugins installation subprocess would see
    import subprocess
    env = os.environ.copy()
    env["PYTHONUSERBASE"] = THONNY_USER_BASE
    proc = subprocess.Popen(
        [sys.executable.replace("thonny.exe", "pythonw.exe"),
         "-c", "import site; print(site.getusersitepackages())"],
        universal_newlines=True, env=env, stdout=subprocess.PIPE)
    plugins_sitepackages = proc.stdout.readline().strip()
    
    sys.path.append(plugins_sitepackages)

def _should_delegate():
    from thonny import workbench
    from thonny.config import try_load_configuration
    configuration_manager = try_load_configuration(workbench.CONFIGURATION_FILE_NAME)
    # Setting the default
    configuration_manager.set_default("general.single_instance", workbench.SINGLE_INSTANCE_DEFAULT)
    # getting the value (may use the default or return saved value)
    return configuration_manager.get_option("general.single_instance")

def _try_delegate_to_existing_instance(args):
    import socket
    from thonny import workbench
    try:
        # Try to create server socket.
        # This is fastest way to find out if Thonny is already running
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind(("localhost", workbench.THONNY_PORT))
        serversocket.listen(10)
        # we were able to create server socket (ie. Thonny was not running)
        # Let's use the socket in Thonny so that requests coming while 
        # UI gets constructed don't get lost.
        # (Opening several files with Thonny in Windows results in many
        # Thonny processes opened quickly) 
        return serversocket
    except OSError:
        # port was already taken, most likely by previous Thonny instance.
        # Try to connect and send arguments
        try:
            return _delegate_to_existing_instance(args)
        except:
            import traceback
            traceback.print_exc()
            return False
        
        
def _delegate_to_existing_instance(args):
    import socket
    from thonny import workbench
    data = repr(args).encode(encoding='utf_8')
    sock = socket.create_connection(("localhost", workbench.THONNY_PORT))
    sock.sendall(data)
    sock.shutdown(socket.SHUT_WR)
    response = bytes([])
    while len(response) < len(workbench.SERVER_SUCCESS):
        new_data = sock.recv(2)
        if len(new_data) == 0:
            break
        else:
            response += new_data
    
    return response.decode("UTF-8") == workbench.SERVER_SUCCESS


    
def get_version():
    try:
        package_dir = os.path.dirname(sys.modules["thonny"].__file__)
        with open(os.path.join(package_dir, "VERSION"), encoding="ASCII") as fp:
            return fp.read().strip()
    except:
        return "0.0.0"
      
    
