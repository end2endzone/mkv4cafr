import pytest
import sys
import os
import random
import copy
from mkv4cafrlib import mkvmergeutils
from mkv4cafrlib import mkvtoolnixutils
from mkv4cafrlib import findutils
from tests import testutils
from functools import cmp_to_key


# Globals
mkvmerge_path = None
medias_path = None
testfiles_path = None
test01_file_path = None
test02_file_path = None
test03_file_path = None


# https://stackoverflow.com/questions/72085517/getting-pytest-to-run-setup-and-teardown-for-every-test-coming-from-nose
# https://docs.pytest.org/en/6.2.x/xunit_setup.html
def setup_function():
    """ setup any state tied to the execution of the given function. Invoked for every test function in the module."""

    # Check program dependencies
    mkvtoolnix_install_path_tmp = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path_tmp != None
    mkvmerge_path_tmp = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path_tmp != None

    # Check file dependencies
    medias_path_tmp = testutils.get_medias_dir_path()
    testfiles_path_tmp = testutils.get_test_files_dir_path()
    assert medias_path_tmp != None
    assert testfiles_path_tmp != None

    # Assert some know medias files
    test01_file_path_tmp = os.path.join(medias_path_tmp, "test01.mkv")
    test02_file_path_tmp = os.path.join(medias_path_tmp, "test02.mkv")
    test03_file_path_tmp = os.path.join(medias_path_tmp, "test03.mkv")
    assert os.path.isfile(test01_file_path_tmp)
    assert os.path.isfile(test02_file_path_tmp)
    assert os.path.isfile(test03_file_path_tmp)

    # Setup global variables
    global mkvmerge_path
    global medias_path
    global testfiles_path
    global test01_file_path
    global test02_file_path
    global test03_file_path
    mkvmerge_path   = mkvmerge_path_tmp
    medias_path     = medias_path_tmp
    testfiles_path  = testfiles_path_tmp
    test01_file_path = test01_file_path_tmp
    test02_file_path = test02_file_path_tmp
    test03_file_path = test03_file_path_tmp


def teardown_function():
    """ teardown any state that was previously setup with a setup_function call."""
    pass


def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    pass


def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module method."""
    pass


def test_compare_tracks():
    # Check setup dependencies
    assert mkvmerge_path != None
    assert test01_file_path != None

    # arrange

    # Load media info into a json dict
    original_json_obj = mkvmergeutils.get_media_file_info(test01_file_path)
    assert original_json_obj != None
    assert "tracks" in original_json_obj
    tracks = original_json_obj['tracks']
    assert len(tracks) == 8

    #---------------------------------------------
    #        test default sorting order
    #---------------------------------------------

    # randomize actual content
    json_obj2 = copy.deepcopy(original_json_obj)
    random.shuffle(json_obj2['tracks'])
    assert mkvmergeutils.get_track_property_value(json_obj2, 0, 'id') != 0

    # act
    mkvtoolnixutils.sort_tracks(json_obj2)

    # assert
    assert mkvmergeutils.get_track_key_value(json_obj2, 0, 'id') == 0
    assert mkvmergeutils.get_track_key_value(json_obj2, 1, 'id') == 1
    assert mkvmergeutils.get_track_key_value(json_obj2, 2, 'id') == 2
    assert mkvmergeutils.get_track_key_value(json_obj2, 3, 'id') == 3
    assert mkvmergeutils.get_track_key_value(json_obj2, 4, 'id') == 4
    assert mkvmergeutils.get_track_key_value(json_obj2, 5, 'id') == 5
    assert mkvmergeutils.get_track_key_value(json_obj2, 6, 'id') == 6
    assert mkvmergeutils.get_track_key_value(json_obj2, 7, 'id') == 7

    #---------------------------------------------
    #            test duplicate values
    #---------------------------------------------

    # randomize actual content
    json_obj2 = copy.deepcopy(original_json_obj)
    random.shuffle(json_obj2['tracks'])
    assert mkvmergeutils.get_track_property_value(json_obj2, 0, 'id') != 0

    # arrange
    # duplicate a track twice
    tracks0 = dict(original_json_obj['tracks'][0]).copy()
    json_obj2['tracks'].append(tracks0)
    json_obj2['tracks'].append(tracks0)

    # act
    mkvtoolnixutils.sort_tracks(json_obj2)

    # assert
    assert mkvmergeutils.get_track_key_value(json_obj2, 0, 'id') == 0
    assert mkvmergeutils.get_track_key_value(json_obj2, 1, 'id') == 0
    assert mkvmergeutils.get_track_key_value(json_obj2, 2, 'id') == 0
    assert mkvmergeutils.get_track_key_value(json_obj2, 3, 'id') == 1
    assert mkvmergeutils.get_track_key_value(json_obj2, 4, 'id') == 2
    assert mkvmergeutils.get_track_key_value(json_obj2, 5, 'id') == 3
    assert mkvmergeutils.get_track_key_value(json_obj2, 6, 'id') == 4
    assert mkvmergeutils.get_track_key_value(json_obj2, 7, 'id') == 5
    assert mkvmergeutils.get_track_key_value(json_obj2, 8, 'id') == 6
    assert mkvmergeutils.get_track_key_value(json_obj2, 9, 'id') == 7
