def get_module_node(script):
    if hasattr(script, "_get_modsule_node"):
        return script._get_module_node()
    elif hasattr(script, "_get_module"):
        m = script._get_module()
        return m.tree_node
    else:
        return script._parser.module()