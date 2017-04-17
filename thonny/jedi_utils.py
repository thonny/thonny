def get_module_node(script):
    if hasattr(script, "_get_module_node"):
        return script._get_module_node()
    elif hasattr(script, "_get_module"):
        return script._get_module()
    else:
        return script._parser.module()