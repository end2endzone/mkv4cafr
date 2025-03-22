import os
from mkv4cafr import findutils

def find_ffmpeg_exec_path_in_path():
    exec_path = findutils.find_file_in_path("ffmpeg" + findutils.get_executable_file_extension_name())
    return exec_path


def find_ffmpeg_dir_in_path():
    exec_path = findutils.find_file_in_path("ffmpeg" + findutils.get_executable_file_extension_name())
    if not exec_path is None:
        dir_path = os.path.dirname(exec_path)
        return dir_path        
    return None


