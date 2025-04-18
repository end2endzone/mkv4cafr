import pytest
import os
from mkv4cafrlib import findutils

def test_find_exec_in_path():
    # test not found
    location = findutils.find_exec_in_path("i-do-not-exists")
    assert location is None

    # search for python exec
    location = findutils.find_exec_in_path("python")
    assert location != None

    # on Windows, search for python.exe
    if os.name == 'nt' or os.name == 'win32':
        location = findutils.find_exec_in_path("python.exe")
        assert location != None


def test_find_file_in_hints():
    search_paths  = os.curdir
    search_paths += os.pathsep + os.path.join(os.curdir,"medias")
    hints = search_paths.split(os.pathsep)

    # test not found
    location = findutils.find_file_in_hints("i_do_not_exists.mkv", hints)
    assert location is None

    # test to search for an actual media
    location = findutils.find_file_in_hints("test01.mkv", hints)
    assert location != None


def test_is_absolute_file_in_path():
    file_dir = ""
    file_name = ""
    bad_dir = ""
    if os.name == 'nt' or os.name == 'win32': 
        file_dir = 'C:\\Windows\\system32'
        file_name = 'cmd.exe'
        bad_dir = 'c:\\idonotexist'
    else: 
        file_dir = '/usr/bin'
        file_name = 'sh'
        bad_dir = '/idonotexist'

    # assert failing to find something 
    file_path = os.path.join(bad_dir, "filename-that-do-not-exists")
    found = findutils.is_absolute_file_in_path(file_path)
    assert (found == False)

    # assert finding something 
    file_path = os.path.join(file_dir, file_name)
    found = findutils.is_absolute_file_in_path(file_path)
    assert (found == True)

    # file_name will be found in PATH but not as the 
    bad_file_path = os.path.join(bad_dir, file_name)
    found = findutils.is_absolute_file_in_path(bad_file_path)
    assert (found == False)
