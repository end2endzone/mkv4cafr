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


def find_ffmpeg_exec_path():
    exec_path = find_file_in_path("ffmpeg" + get_executable_file_extension_name())
    return exec_path


def find_MKVToolNix_install_dir():
    exec_path = find_file_in_path("mkvmerge" + get_executable_file_extension_name())
    if not exec_path is None:
        dir_path = os.path.dirname(exec_path)
        return dir_path
        
    # Not in PATH
    # Add default installation location in PATH
    os.environ['PATH'] = "C:\\Program Files\\MKVToolNix" + os.pathsep + os.environ['PATH']

    # and search again
    exec_path = find_file_in_path("mkvmerge" + get_executable_file_extension_name())
    if not exec_path is None:
        dir_path = os.path.dirname(exec_path)
        return dir_path
        
    return None
