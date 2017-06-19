def handle_dataexplore(command_line):
    print("Handling", command_line)

def load_plugin(vm):
    vm.add_magic_command("dataexplore", handle_dataexplore)