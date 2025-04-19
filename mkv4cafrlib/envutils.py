import os
from mkv4cafrlib import findutils
from mkv4cafrlib import fileutils


def get_path_variable_name():
    if os.name == 'nt' or os.name == 'win32':
        return "Path"
    else:
        return "PATH"


def get_path_separator():
    if os.name == 'nt' or os.name == 'win32':
        return ";"
    else:
        return ":"


def remove_directory_in_path(dirname: str) -> os._Environ:
    path_var_name = get_path_variable_name()
    path_separator = get_path_separator()

    # get the old PATH environment variable as a list
    path_value = os.environ[path_var_name]
    paths = path_value.split(path_separator)

    # remove the specific directory entries
    try:
        paths.remove(dirname)
    except ValueError:
        pass   
    try:
        paths.remove(dirname + fileutils.get_file_separator())
    except ValueError:
        pass   

    # rebuild as a string
    new_path_value = path_separator.join(paths)

    # update current environment
    os.environ.__setitem__(path_var_name, new_path_value)

