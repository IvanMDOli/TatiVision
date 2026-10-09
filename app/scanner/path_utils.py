import os


def is_path_within_root(path, root_path):
    if not path or not root_path:
        return False

    normalized_root = os.path.normcase(os.path.abspath(root_path))
    normalized_path = os.path.normcase(os.path.abspath(path))
    try:
        return os.path.commonpath(
            [normalized_root, normalized_path]
        ) == normalized_root
    except ValueError:
        return False
