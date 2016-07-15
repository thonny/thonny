
DELEGATION_SUCCESSFUL = "Delegation successful"

def launch():
    import sys
    from thonny import workbench
    try:
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
        try:
            bench.mainloop()
        except SystemExit:
            bench.destroy()
        return 0
    except:
        from logging import exception
        exception("Internal error")
        import tkinter.messagebox
        import traceback
        tkinter.messagebox.showerror("Internal error", traceback.format_exc())
        return -1

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

launch()