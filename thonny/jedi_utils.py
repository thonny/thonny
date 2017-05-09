def get_module_node(script):
    if hasattr(script, "_get_module_node"):
        return script._get_module_node()
    elif hasattr(script, "_get_module"):
        return script._get_module()
    else:
        return script._parser.module()

def get_version_tuple():
    import jedi
    nums = []
    for item in jedi.__version__.split("."):
        try:
            nums.append(int(item))
        except:
            nums.append(0)
            
    return tuple(nums)