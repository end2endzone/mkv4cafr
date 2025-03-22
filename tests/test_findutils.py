import pytest
import os
from src import findutils

def test_find_exec_in_path():
    # test not found
    location = findutils.find_exec_in_path("foobar")
    assert location is None

    # search for python exec
    location = findutils.find_exec_in_path("python")
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
