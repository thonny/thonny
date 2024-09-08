import os.path
import stat
import xattr

left_prefix = os.path.join(os.path.dirname(__file__), "build")
right_prefix = "/Applications"

def compare_item(path):
    left_path = os.path.join(left_prefix, path)
    right_path = os.path.join(right_prefix, path)

    assert os.path.exists(left_path)
    if not os.path.exists(right_path):
        print(path, "missing in right")
        return

    left_perm = stat.filemode(os.stat(left_path).st_mode)
    right_perm = stat.filemode(os.stat(right_path).st_mode)
    
    if left_perm != right_perm:
        print(path, "permissions", left_perm, "vs", right_perm)

    left_xattr = xattr.listxattr(left_path)
    right_xattr = xattr.listxattr(right_path)

    if left_xattr != right_xattr:
        print(path, "permissions", left_perm, "vs", right_perm)


    assert os.path.isdir(left_path) == os.path.isdir(left_path)

    if os.path.isdir(left_path):
        left_names = []
        for name in os.listdir(left_path):
            compare_item(os.path.join(path, name))
            left_names.append(name)

        for name in os.listdir(right_path):
            if name not in left_names:
                print(os.path.join(path, name), "missing in left")
    else:
        left_size = os.stat(left_path).st_size
        right_size = os.stat(left_path).st_size
        if left_size != right_size:
            print(path, "size", left_size, "vs", right_size)


compare_item("Thonny.app")
