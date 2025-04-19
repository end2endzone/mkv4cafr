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


def find_exec_in_path(file_name):
    path_list = os.environ['PATH'].split(os.pathsep)
    # find as is
    location = find_file_in_hints(file_name, path_list)
    if (location != None):
        return location
    # find as an executable
    location = find_file_in_hints(file_name + get_executable_file_extension_name(), path_list)
    if (location != None):
        return location
    return None


def find_file_in_hints(file_name, hints):
    for path_entry in hints:
        full_path = os.path.join(path_entry,file_name)
        if os.path.isfile(full_path):
            return full_path
    return None


def is_absolute_file_in_path(exec_path: str):
    path, file = os.path.split(exec_path)
    file_abs_path = find_file_in_path(file)
    if (file_abs_path is None):
        return False
    if (file_abs_path == exec_path):
        return True
    return False
