import pytest
import os
import tempfile
from mkv4cafrlib import mkvtoolnixutils
from mkv4cafrlib import mkvmergeutils
from mkv4cafrlib import findutils
from tests import testutils


# https://stackoverflow.com/questions/72085517/getting-pytest-to-run-setup-and-teardown-for-every-test-coming-from-nose
# https://docs.pytest.org/en/6.2.x/xunit_setup.html
def setup_function():
    """ setup any state tied to the execution of the given function. Invoked for every test function in the module."""

    # Check program dependencies
    mkvtoolnix_install_path_tmp = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path_tmp != None
    mkvmerge_path_tmp = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path_tmp != None


def teardown_function():
    """ teardown any state that was previously setup with a setup_function call."""
    pass


def assert_track_properties(json_obj: dict,
                            track_index: int,
                            expected_language: str,
                            expected_language_ietf: str,
                            expected_is_default: bool,
                            expected_is_forced: bool,
                            expected_track_name: str,
                            ):
    
    # assert json_obj and track_index
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']
    assert track_index < len(tracks)

    # get all properties
    actual_language      = mkvmergeutils.get_track_property_value(json_obj, track_index, 'language')
    actual_language_ietf = mkvmergeutils.get_track_property_value(json_obj, track_index, 'language_ietf')
    actual_is_default    = mkvmergeutils.get_track_property_value(json_obj, track_index, 'default_track')
    actual_is_forced     = mkvmergeutils.get_track_property_value(json_obj, track_index, 'forced_track')
    actual_track_name    = mkvmergeutils.get_track_property_value(json_obj, track_index, 'track_name')

    # assert actual values are all expected
    assert actual_language      == expected_language     
    assert actual_language_ietf == expected_language_ietf
    assert actual_is_default    == expected_is_default   
    assert actual_is_forced     == expected_is_forced    
    assert actual_track_name    == expected_track_name   


def test_media_test01():
    temp_dir = tempfile.gettempdir()

    # act
    args = list()
    args.append("--input-file")
    args.append("medias/test01.mkv")
    args.append("--output-dir")
    args.append(temp_dir)
    returncode = testutils.run_mkv4cafr(args)
    assert returncode == 0

    # assert
    output_file_path = os.path.join(temp_dir, "test01.mkv")
    assert os.path.isfile(output_file_path)

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(output_file_path)
    assert json_obj != None

    # assert track count
    assert json_obj != None
    assert "tracks" in json_obj
    assert len(json_obj['tracks']) == 8

    assert mkvmergeutils.get_container_properties_title(json_obj) == None

    assert_track_properties(json_obj, 0, 'und', 'und', True, False, None)
    assert_track_properties(json_obj, 1, 'fre', 'fr', False, False, 'FR E-AC3 5.1')
    assert_track_properties(json_obj, 2, 'eng', 'en', False, False, 'EN AAC 2.0')
    assert_track_properties(json_obj, 3, 'eng', 'en', False, False, 'EN DTS 5.1')
    assert_track_properties(json_obj, 4, 'eng', 'en', False, False, 'EN FLAC 7.1 (VO)')
    assert_track_properties(json_obj, 5, 'fre', 'fr-CA', True, False, 'FR AC3 5.1 (VFQ)')
    assert_track_properties(json_obj, 6, 'fre', 'fr-CA', False, False, 'this might be foreign languages subtitles')
    assert_track_properties(json_obj, 7, 'eng', 'en', False, False, 'full')


def test_media_test02():
    temp_dir = tempfile.gettempdir()

    # act
    args = list()
    args.append("--input-file")
    args.append("medias/test02.mkv")
    args.append("--output-dir")
    args.append(temp_dir)
    returncode = testutils.run_mkv4cafr(args)
    assert returncode == 0

    # assert
    output_file_path = os.path.join(temp_dir, "test02.mkv")
    assert os.path.isfile(output_file_path)

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(output_file_path)
    assert json_obj != None

    # assert track count
    assert json_obj != None
    assert "tracks" in json_obj
    assert len(json_obj['tracks']) == 8

    assert mkvmergeutils.get_container_properties_title(json_obj) == None

    assert_track_properties(json_obj, 0, 'und', 'und', True, False, None)
    assert_track_properties(json_obj, 3, 'fre', 'fr', False, False, 'FR E-AC3 5.1')
    assert_track_properties(json_obj, 4, 'eng', 'en', False, False, 'EN AAC 2.0')
    assert_track_properties(json_obj, 5, 'eng', 'en', False, False, 'EN DTS 5.1')
    assert_track_properties(json_obj, 6, 'eng', 'en', False, False, 'EN FLAC 7.1 (VO)')
    assert_track_properties(json_obj, 7, 'fre', 'fr-CA', True, False, 'FR AC3 5.1 (VFQ)')
    assert_track_properties(json_obj, 1, 'fre', 'fr-CA', False, False, 'this might be foreign languages subtitles')
    assert_track_properties(json_obj, 2, 'eng', 'en', False, False, 'full')


def test_media_test_get_track_name_flags():
    temp_dir = tempfile.gettempdir()

    # act
    args = list()
    args.append("--input-file")
    args.append("medias/test_get_track_name_flags.mkv")
    args.append("--output-dir")
    args.append(temp_dir)
    returncode = testutils.run_mkv4cafr(args)
    assert returncode == 0

    # assert
    output_file_path = os.path.join(temp_dir, "test_get_track_name_flags.mkv")
    assert os.path.isfile(output_file_path)

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(output_file_path)
    assert json_obj != None

    # assert track count
    assert json_obj != None
    assert "tracks" in json_obj
    assert len(json_obj['tracks']) == 18

    assert mkvmergeutils.get_container_properties_title(json_obj) == None

    assert_track_properties(json_obj,  0, 'und', 'und', True, False, None)
    assert_track_properties(json_obj,  1, 'und', 'und', False, False, 'AC3 2.0')
    assert_track_properties(json_obj,  2, 'und', 'und', False, False, 'AC3 2.0')
    assert_track_properties(json_obj,  3, 'fre', 'fr-FR', False, False, 'FR AC3 2.0 (VFF)')
    assert_track_properties(json_obj,  4, 'fre', 'fr-FR', False, False, 'FR AC3 2.0 (VFF)')
    assert_track_properties(json_obj,  5, 'fre', 'fr-FR', False, False, 'FR AC3 2.0 (VFF)')
    assert_track_properties(json_obj,  6, 'fre', 'fr-FR', False, False, 'FR AC3 2.0 (VFF)')

    assert_track_properties(json_obj,  7, 'fre', 'fr-CA',  True, False, 'FR AC3 2.0 (VFQ)')
    assert_track_properties(json_obj,  8, 'fre', 'fr-CA', False, False, 'FR AC3 2.0 (VFQ)')
    assert_track_properties(json_obj,  9, 'fre', 'fr-CA', False, False, 'FR AC3 2.0 (VFQ)')
    assert_track_properties(json_obj, 10, 'fre', 'fr-CA', False, False, 'FR AC3 2.0 (VFQ)')
    assert_track_properties(json_obj, 11, 'fre', 'fr-CA', False, False, 'FR AC3 2.0 (VFQ)')

    assert_track_properties(json_obj, 12, 'fre', 'fr', False, False, 'FR AC3 2.0 (VFI)')
    assert_track_properties(json_obj, 13, 'und', 'und', False, False, 'AC3 2.0 (VO)')
    assert_track_properties(json_obj, 14, 'und', 'und', False, False, 'AC3 2.0 (AD)')
    assert_track_properties(json_obj, 15, 'und', 'und', False, False, 'AC3 2.0 (DVD)')
    assert_track_properties(json_obj, 16, 'und', 'und', False, False, 'AC3 2.0 (SDH)')
    assert_track_properties(json_obj, 17, 'und', 'und', False, False, 'AC3 2.0 (AD)')


def test_media_test_get_track_auto_generated_name():
    temp_dir = tempfile.gettempdir()

    # act
    args = list()
    args.append("--input-file")
    args.append("medias/test_get_track_auto_generated_name.mkv")
    args.append("--output-dir")
    args.append(temp_dir)
    returncode = testutils.run_mkv4cafr(args)
    assert returncode == 0

    # assert
    output_file_path = os.path.join(temp_dir, "test_get_track_auto_generated_name.mkv")
    assert os.path.isfile(output_file_path)

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(output_file_path)
    assert json_obj != None

    # assert track count
    assert json_obj != None
    assert "tracks" in json_obj
    assert len(json_obj['tracks']) == 14

    assert_track_properties(json_obj,  0, 'und', 'und', True, False, None)
    assert_track_properties(json_obj,  1, 'und', 'und', False, False, 'AC3 1.0')
    assert_track_properties(json_obj,  2, 'fre', 'fr', False, False, 'FR MP3 2.0')
    assert_track_properties(json_obj,  3, 'fre', 'fr-FR', False, False, 'FR AAC 2.0 (VFF)')
    assert_track_properties(json_obj,  4, 'fre', 'fr-CA', True, True, 'FR AC3 2.0 (VFQ)')
    assert_track_properties(json_obj,  5, 'spa', 'es', False, False, 'SPA TrueHD 5.1')
    assert_track_properties(json_obj,  6, 'ger', 'de', False, False, 'GER TrueHD 5.1')
    assert_track_properties(json_obj,  7, 'eng', 'en', False, False, 'EN AC3 5.1')
    assert_track_properties(json_obj,  8, 'eng', 'en-US', False, False, 'EN E-AC3 5.1')
    assert_track_properties(json_obj,  9, 'eng', 'en-GB', False, False, 'EN Vorbis 5.1')
    assert_track_properties(json_obj, 10, 'eng', 'en-CA', False, False, 'EN DTS 5.1')
    assert_track_properties(json_obj, 11, 'mul', 'mul', False, False, 'MUL Opus 5.1')
    assert_track_properties(json_obj, 12, 'mis', 'mis', False, False, 'MIS FLAC 7.1')
    assert_track_properties(json_obj, 13, 'zxx', 'zxx', False, False, 'ZXX PCM 2.0')



