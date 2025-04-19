import getpass
import os
from mkv4cafrlib import findutils
from functools import cmp_to_key

TRACK_TYPE_NATURAL_SORT_ORDER = ["video", "audio", "subtitles"]


def compare_tracks(a: dict, b: dict):
    a_index = TRACK_TYPE_NATURAL_SORT_ORDER.index(a['type']) if 'type' in a else 999999
    b_index = TRACK_TYPE_NATURAL_SORT_ORDER.index(b['type']) if 'type' in b else 999999
    if a_index > b_index:
        return 1
    elif a_index == b_index:
        a_id = a['id'] if 'id' in a else 999999
        b_id = b['id'] if 'id' in b else 999999
        if a_id > b_id:
            return 1
        elif a_id == b_id:
            return 0
        else:
            return -1
    else:
        return -1


def sort_tracks(json_obj: dict):
    tracks = json_obj['tracks'] if 'tracks' in json_obj else None
    if (tracks is None):
        return

    # sort tracks as per MKVToolNix GUI order.
    # without this sort, mkvmerge will output tracks in ID order
    # which makes 'index' and 'id' always he same (index == id).
    comparator_tracks_py3 = cmp_to_key(compare_tracks)
    tracks.sort(key = comparator_tracks_py3)

    json_obj['tracks'] = tracks


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


def setup_mkvtoolnix():
    mkvtoolnix_install_path = find_mkvtoolnix_dir_in_path()
    if mkvtoolnix_install_path is None or not os.path.isdir(mkvtoolnix_install_path):
        print("MKVToolNix not found in PATH.")

        print("Searching known installation directories...")
        mkvtoolnix_install_path = find_mkvtoolnix_dir_on_system()
        if mkvtoolnix_install_path is None or not os.path.isdir(mkvtoolnix_install_path):
            print("MKVToolNix not found on system.\n")
            return None

        # Found, but not in PATH
        os.environ['PATH'] = mkvtoolnix_install_path + os.pathsep + os.environ['PATH']
    return mkvtoolnix_install_path
