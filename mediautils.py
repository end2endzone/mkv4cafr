import argparse
import os
import sys
import getpass
import subprocess
import json


def get_executable_file_extension_name():
    if os.name == 'nt' or os.name == 'win32':
        return ".exe"
    else:
        return ""


def find_file_in_path(file_name):
    path_list = os.environ['PATH'].split(os.pathsep)
    return find_file_in_hints(file_name, path_list)


def find_file_in_hints(file_name, hints):
    for path_entry in hints:
        full_path = os.path.join(path_entry,file_name)
        if os.path.isfile(full_path):
            return full_path
    return None


def get_MKVToolNix_install_directory_hints():
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


def find_ffmpeg_dir_in_path():
    exec_path = find_file_in_path("ffmpeg" + get_executable_file_extension_name())
    if not exec_path is None:
        dir_path = os.path.dirname(exec_path)
        return dir_path        
    return None


def find_ffmpeg_exec_path_in_path():
    exec_path = find_file_in_path("ffmpeg" + get_executable_file_extension_name())
    return exec_path


def find_mkvtoolnix_dir_in_path():
    exec_path = find_file_in_path("mkvmerge" + get_executable_file_extension_name())
    if not exec_path is None:
        dir_path = os.path.dirname(exec_path)
        return dir_path        
    return None


def is_absolute_file_in_path(exec_path: str):
    path, file = os.path.split(exec_path)
    file_abs_path = find_file_in_path(file)
    if (file_abs_path is None):
        return True
    return False


def find_mkvtoolnix_dir_on_system():
    exec_path = find_file_in_path("mkvmerge" + get_executable_file_extension_name())
    if not exec_path is None:
        dir_path = os.path.dirname(exec_path)
        return dir_path
    
    # MKVToolNix not in PATH.
    # Search again in known installation directories
    mkvtoolnix_install_hints = get_MKVToolNix_install_directory_hints()
    exec_path = find_file_in_hints("mkvmerge" + get_executable_file_extension_name(), mkvtoolnix_install_hints)
    if not exec_path is None:
        dir_path = os.path.dirname(exec_path)
        return dir_path
        
    return None

