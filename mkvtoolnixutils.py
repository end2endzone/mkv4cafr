import findutils
import getpass
import os

def get_mkvtoolnix_install_directory_hints():
    hints = []

    # User's home directory
    username = getpass.getuser()
    hints.append("/home/" + username)

    # Default linux directories
    hints.append("/bin")
    hints.append("/usr/bin")
    hints.append("/usr/lib")

    # Windows default installation directories
    hints.append("C:\\Program Files\\MKVToolNix")
    hints.append("C:\\Program Files (x86)\\MKVToolNix")
    
    return hints


def find_mkvtoolnix_dir_in_path():
    exec_path = findutils.find_file_in_path("mkvmerge" + findutils.get_executable_file_extension_name())
    if not exec_path is None:
        dir_path = os.path.dirname(exec_path)
        return dir_path        
    return None


def find_mkvtoolnix_dir_on_system():
    exec_path = findutils.find_file_in_path("mkvmerge" + findutils.get_executable_file_extension_name())
    if not exec_path is None:
        dir_path = os.path.dirname(exec_path)
        return dir_path
    
    # MKVToolNix not in PATH.
    # Search again in known installation directories
    mkvtoolnix_install_hints = get_mkvtoolnix_install_directory_hints()
    exec_path = findutils.find_file_in_hints("mkvmerge" + findutils.get_executable_file_extension_name(), mkvtoolnix_install_hints)
    if not exec_path is None:
        dir_path = os.path.dirname(exec_path)
        return dir_path
        
    return None
