import pytest
import os
from tests import testutils
from mkv4cafrlib import mkvmergeutils
from mkv4cafrlib import mkvtoolnixutils
from mkv4cafrlib import findutils


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


def get_media_file_path(file_name) -> str:
    file_path = os.path.join(medias_path, file_name)
    assert os.path.isfile(file_path)
    return file_path


def get_test_file_path(file_name) -> str:
    file_path = os.path.join(testfiles_path, file_name)
    assert os.path.isfile(file_path)
    return file_path


def test_get_media_file_info():
    # Check setup dependencies
    assert mkvmerge_path != None
    assert test01_file_path != None

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(test01_file_path)
    assert json_obj != None


def test_get_tracks_indice_by_type():
    # Check setup dependencies
    assert mkvmerge_path != None
    assert test01_file_path != None

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(test01_file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act (list version)
    accepted_types = list()
    accepted_types.append("video")
    accepted_types.append("subtitles")
    
    indices = list()
    indices = mkvmergeutils.get_tracks_indice_by_type(tracks, accepted_types)

    # assert
    assert len(indices) == 3
    assert indices[0] == 0
    assert indices[1] == 6
    assert indices[2] == 7

    # act (string version)
    accepted_type = "subtitles"
    
    indices = list()
    indices = mkvmergeutils.get_tracks_indice_by_type(tracks, accepted_type)

    # assert
    assert len(indices) == 2
    assert indices[0] == 6
    assert indices[1] == 7


def test_filter_tracks_indice_by_language():
    # Check setup dependencies
    assert mkvmerge_path != None
    assert test01_file_path != None

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(test01_file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    audio_indices = list()
    audio_indices = mkvmergeutils.get_tracks_indice_by_type(tracks, "audio")
    accepted_languages = list()
    accepted_languages.append("fre")
    filtered_indices = mkvmergeutils.filter_tracks_indice_by_language(tracks, audio_indices, accepted_languages)

    # assert
    assert len(filtered_indices) == 2
    assert filtered_indices[0] == 1
    assert filtered_indices[1] == 5


def test_filter_tracks_indice_by_flag():
    # Check setup dependencies
    assert mkvmerge_path != None
    assert test01_file_path != None

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(test01_file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    accepted_types = list()
    accepted_types.append("audio")
    accepted_types.append("subtitles")
    indices = list()
    indices = mkvmergeutils.get_tracks_indice_by_type(tracks, accepted_types)
    accepted_flags = list()
    accepted_flags.append("VFQ")
    indices = mkvmergeutils.filter_tracks_indice_by_flag(tracks, indices, accepted_flags)

    # assert
    assert len(indices) == 2
    assert indices[0] == 5
    assert indices[1] == 6


def test_get_language_friendly_name():
    assert "FR" == mkvmergeutils.get_language_friendly_name("fre")
    assert "EN" == mkvmergeutils.get_language_friendly_name("eng")
    assert "UND" == mkvmergeutils.get_language_friendly_name("und")
    assert "FOO" == mkvmergeutils.get_language_friendly_name("foo")


def test_get_audio_channel_layout_friendly_name():
    assert "1.0" == mkvmergeutils.get_audio_channel_layout_friendly_name(1)
    assert "2.0" == mkvmergeutils.get_audio_channel_layout_friendly_name(2)
    assert "2.1" == mkvmergeutils.get_audio_channel_layout_friendly_name(3)
    assert "4.0" == mkvmergeutils.get_audio_channel_layout_friendly_name(4)
    assert "4.1" == mkvmergeutils.get_audio_channel_layout_friendly_name(5)
    assert "5.1" == mkvmergeutils.get_audio_channel_layout_friendly_name(6)
    assert "7.0" == mkvmergeutils.get_audio_channel_layout_friendly_name(7)
    assert "7.1" == mkvmergeutils.get_audio_channel_layout_friendly_name(8)
    assert "9.0" == mkvmergeutils.get_audio_channel_layout_friendly_name(9)
    assert "9.1" == mkvmergeutils.get_audio_channel_layout_friendly_name(10)

    assert "11.0" == mkvmergeutils.get_audio_channel_layout_friendly_name(11)
    assert "12.0" == mkvmergeutils.get_audio_channel_layout_friendly_name(12)
    assert "13.0" == mkvmergeutils.get_audio_channel_layout_friendly_name(13)
    assert "50.0" == mkvmergeutils.get_audio_channel_layout_friendly_name(50)


def test_test_flag_in_string():
    flag = "foo"
    assert mkvmergeutils.test_flag_in_string("foo", flag) == True
    assert mkvmergeutils.test_flag_in_string("afoob", flag) == False # middle of a name

    assert mkvmergeutils.test_flag_in_string("foo bar", flag) == True # begin of the string
    assert mkvmergeutils.test_flag_in_string("bar foo", flag) == True # end of the string

    # assert found when separated by the following characters: ' ', '.', ',', '-', '(', '['    
    assert mkvmergeutils.test_flag_in_string("a foo b", flag) == True
    assert mkvmergeutils.test_flag_in_string("a.foo.b", flag) == True
    assert mkvmergeutils.test_flag_in_string("a,foo,b", flag) == True
    assert mkvmergeutils.test_flag_in_string("a-foo-b", flag) == True

    # assert parenthesis
    assert mkvmergeutils.test_flag_in_string("a(foo(b", flag) == False # parenthesis are special and need their counterpart closing character
    assert mkvmergeutils.test_flag_in_string("a[foo[b", flag) == False # parenthesis are special and need their counterpart closing character
    assert mkvmergeutils.test_flag_in_string("a(foo)b", flag) == True
    assert mkvmergeutils.test_flag_in_string("a[foo]b", flag) == True

    # assert mix and match
    assert mkvmergeutils.test_flag_in_string("a foo.b", flag) == True and mkvmergeutils.test_flag_in_string("a.foo b", flag) == True
    assert mkvmergeutils.test_flag_in_string("a,foo-b", flag) == True and mkvmergeutils.test_flag_in_string("a-foo,b", flag) == True
    assert mkvmergeutils.test_flag_in_string("a foo-b", flag) == True and mkvmergeutils.test_flag_in_string("a-foo b", flag) == True
    assert mkvmergeutils.test_flag_in_string("a,foo b", flag) == True and mkvmergeutils.test_flag_in_string("a foo,b", flag) == True


def test_get_track_name_flags():
    # Check setup dependencies
    assert mkvmerge_path != None

    # Check file dependencies
    file_path = get_media_file_path("test_get_track_name_flags.mkv")
    assert os.path.isfile(file_path)

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    flags = list()

    # read flags for each track
    for i in range(len(tracks)):
        track = tracks[i]
        current_index = i
        temp = mkvmergeutils.get_track_name_flags(track)
        flags.append(temp)

    # assert
    assert len(flags) == len(tracks)
    expected_flags = [
        None,
        None,
        None,
        'VFF',
        'VFF',
        'VFF',
        'VFF',
        'VFQ',
        'VFQ',
        'VFQ',
        'VFQ',
        'VFQ',
        'VFI',
        'VO',
        'AD',
        'DVD',
        'SDH',
        'AD'
    ]
    assert len(flags) == len(expected_flags)
    for i in range(len(flags)):
        assert flags[i] == expected_flags[i]


def test_get_track_auto_generated_name():
    # Check setup dependencies
    assert mkvmerge_path != None

    # Check file dependencies
    file_path = get_media_file_path("test_get_track_auto_generated_name.mkv")
    assert os.path.isfile(file_path)

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    names = list()

    # read flags for each track
    for i in range(len(tracks)):
        track = tracks[i]
        current_index = i
        temp = mkvmergeutils.get_track_auto_generated_name(track)
        names.append(temp)

    # assert
    assert len(names) == len(tracks)
    expected_names = [
        None,
        'AC3 1.0',
        'FR MP3 2.0',
        'FR AAC 2.0 (VFF)',
        'FR AC3 2.0 (VFQ)',
        'SPA TRUEHD 5.1',
        'GER TRUEHD 5.1',
        'EN AC3 5.1',
        'EN E-AC3 5.1',
        'EN VORBIS 5.1',
        'EN DTS 5.1',
        'MUL OPUS 5.1',
        'MIS FLAC 7.1',
        'ZXX PCM 2.0'
    ]
    assert len(names) == len(expected_names)
    for i in range(len(names)):
        assert names[i] == expected_names[i]


def test_get_first_default_track_id_for_type():
    # Check setup dependencies
    assert mkvmerge_path != None

    # Check file dependencies
    file_path1 = get_test_file_path("test_get_first_default_track_id_for_type_id025.json")
    file_path2 = get_test_file_path("test_get_first_default_track_id_for_type_none.json")
    assert os.path.isfile(file_path1)
    assert os.path.isfile(file_path2)

    # ------------------------------------------------------------------------------
    # file 01
    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.load_media_file_info(file_path1)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    first_default_video_track_id = mkvmergeutils.get_first_default_track_id_for_type(tracks, "video")
    first_default_audio_track_id = mkvmergeutils.get_first_default_track_id_for_type(tracks, "audio")
    first_default_subtitles_track_id = mkvmergeutils.get_first_default_track_id_for_type(tracks, "subtitles")

    # assert
    assert first_default_video_track_id     == 0
    assert first_default_audio_track_id     == 2
    assert first_default_subtitles_track_id == 5

    # ------------------------------------------------------------------------------
    # file 02
    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.load_media_file_info(file_path2)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    first_default_video_track_id = mkvmergeutils.get_first_default_track_id_for_type(tracks, "video")
    first_default_audio_track_id = mkvmergeutils.get_first_default_track_id_for_type(tracks, "audio")
    first_default_subtitles_track_id = mkvmergeutils.get_first_default_track_id_for_type(tracks, "subtitles")

    # assert
    assert first_default_video_track_id     == mkvmergeutils.INVALID_TRACK_ID
    assert first_default_audio_track_id     == mkvmergeutils.INVALID_TRACK_ID
    assert first_default_subtitles_track_id == mkvmergeutils.INVALID_TRACK_ID


def test_get_best_track_id_from_indice():
    # Check setup dependencies
    assert mkvmerge_path != None

    # Check file dependencies
    testfiles_path = testutils.get_test_files_dir_path()
    assert testfiles_path != None
    file_path1 = get_test_file_path("test_get_best_track_id_from_indice_vfq_has_priority_over_default_and_vff_and_fr.json")
    file_path2 = get_test_file_path("test_get_best_track_id_from_indice_vff_has_priority_over_default_and_fr.json")
    file_path3 = get_test_file_path("test_get_best_track_id_from_indice_french_has_priority_over_default_and_english.json")
    file_path4 = get_test_file_path("test_get_best_track_id_from_indice_default_if_nothing_is_best.json")
    assert os.path.isfile(file_path1)
    assert os.path.isfile(file_path2)
    assert os.path.isfile(file_path3)
    assert os.path.isfile(file_path4)

    # ------------------------------------------------------------------------------
    # file 1
    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.load_media_file_info(file_path1)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    best_audio_track_id = mkvmergeutils.get_best_track_id_for_type(tracks, "audio")
    best_subtitles_track_id = mkvmergeutils.get_best_track_id_for_type(tracks, "subtitles")

    # assert
    assert best_audio_track_id     == 3
    assert best_subtitles_track_id == 6

    # ------------------------------------------------------------------------------
    # file 2
    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.load_media_file_info(file_path2)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    best_audio_track_id = mkvmergeutils.get_best_track_id_for_type(tracks, "audio")
    best_subtitles_track_id = mkvmergeutils.get_best_track_id_for_type(tracks, "subtitles")

    # assert
    assert best_audio_track_id     == 2
    assert best_subtitles_track_id == 4

    # ------------------------------------------------------------------------------
    # file 3
    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.load_media_file_info(file_path3)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    best_audio_track_id = mkvmergeutils.get_best_track_id_for_type(tracks, "audio")
    best_subtitles_track_id = mkvmergeutils.get_best_track_id_for_type(tracks, "subtitles")

    # assert
    assert best_audio_track_id     == 2
    assert best_subtitles_track_id == 4

    # ------------------------------------------------------------------------------
    # file 4
    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.load_media_file_info(file_path4)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    best_audio_track_id = mkvmergeutils.get_best_track_id_for_type(tracks, "audio")
    best_subtitles_track_id = mkvmergeutils.get_best_track_id_for_type(tracks, "subtitles")

    # assert
    assert best_audio_track_id     == 2
    assert best_subtitles_track_id == 4


def test_get_best_forced_track_id_for_type():
    # Check setup dependencies
    assert mkvmerge_path != None

    # Check file dependencies
    testfiles_path = testutils.get_test_files_dir_path()
    assert testfiles_path != None
    file_path1 = get_test_file_path("test_get_best_forced_track_id_for_type_vfq_has_priority_over_default_and_vff_and_fr.json")
    file_path2 = get_test_file_path("test_get_best_forced_track_id_for_type_vff_has_priority_over_default_and_fr.json")
    file_path3 = get_test_file_path("test_get_best_forced_track_id_for_type_french_has_priority_over_default_and_english.json")
    file_path4 = get_test_file_path("test_get_best_forced_track_id_for_type_invalid_if_nothing_is_forced.json")
    assert os.path.isfile(file_path1)
    assert os.path.isfile(file_path2)
    assert os.path.isfile(file_path3)
    assert os.path.isfile(file_path4)

    # ------------------------------------------------------------------------------
    # file 1
    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.load_media_file_info(file_path1)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    best_audio_track_id = mkvmergeutils.get_best_forced_track_id_for_type(tracks, "audio")
    best_subtitles_track_id = mkvmergeutils.get_best_forced_track_id_for_type(tracks, "subtitles")

    # assert
    assert best_audio_track_id     == 3
    assert best_subtitles_track_id == 6

    # ------------------------------------------------------------------------------
    # file 2
    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.load_media_file_info(file_path2)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    best_audio_track_id = mkvmergeutils.get_best_forced_track_id_for_type(tracks, "audio")
    best_subtitles_track_id = mkvmergeutils.get_best_forced_track_id_for_type(tracks, "subtitles")

    # assert
    assert best_audio_track_id     == 2
    assert best_subtitles_track_id == 4

    # ------------------------------------------------------------------------------
    # file 3
    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.load_media_file_info(file_path3)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    best_audio_track_id = mkvmergeutils.get_best_forced_track_id_for_type(tracks, "audio")
    best_subtitles_track_id = mkvmergeutils.get_best_forced_track_id_for_type(tracks, "subtitles")

    # assert
    assert best_audio_track_id     == 2
    assert best_subtitles_track_id == 4

    # ------------------------------------------------------------------------------
    # file 4
    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.load_media_file_info(file_path4)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    best_audio_track_id = mkvmergeutils.get_best_forced_track_id_for_type(tracks, "audio")
    best_subtitles_track_id = mkvmergeutils.get_best_forced_track_id_for_type(tracks, "subtitles")

    # assert
    assert best_audio_track_id     == mkvmergeutils.INVALID_TRACK_ID
    assert best_subtitles_track_id == mkvmergeutils.INVALID_TRACK_ID


def test_get_track_id_from_index():
    # Check setup dependencies
    assert mkvmerge_path != None
    assert test02_file_path != None

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(test02_file_path)
    assert json_obj != None
    assert "tracks" in json_obj

    # sort tracks as per MKVToolNix GUI order.
    mkvtoolnixutils.sort_tracks(json_obj)

    tracks = json_obj['tracks']

    # act
    track_id_at_index3 = mkvmergeutils.get_track_id_from_index(tracks, 3)
    track_id_at_index9 = mkvmergeutils.get_track_id_from_index(tracks, 9)

    # assert
    assert track_id_at_index3 == 5
    assert track_id_at_index9 == mkvmergeutils.INVALID_TRACK_ID


def test_get_track_index_from_id():
    # Check setup dependencies
    assert mkvmerge_path != None
    assert test02_file_path != None

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(test02_file_path)
    assert json_obj != None
    assert "tracks" in json_obj

    # sort tracks as per MKVToolNix GUI order.
    mkvtoolnixutils.sort_tracks(json_obj)

    tracks = json_obj['tracks']

    # act
    track_index_for_id3 = mkvmergeutils.get_track_index_from_id(tracks, 3)
    track_index_for_id9 = mkvmergeutils.get_track_index_from_id(tracks, 9)

    # assert
    assert track_index_for_id3 == 1
    assert track_index_for_id9 == mkvmergeutils.INVALID_TRACK_ID


def test_get_track_subtitles_count():
    # Check setup dependencies
    assert mkvmerge_path != None
    assert test01_file_path != None

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(test01_file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    subtitles_indices = mkvmergeutils.get_tracks_indice_by_type(tracks, "subtitles")
    assert len(subtitles_indices) > 0
    first_subtitles_track = tracks[subtitles_indices[0]]

    # act
    subtitles_count = mkvmergeutils.get_track_subtitles_count(first_subtitles_track)

    # assert
    assert subtitles_count == 12

    # ------------------------------------------------------------------------------

    # arrange

    subtitles_indices = mkvmergeutils.get_tracks_indice_by_type(tracks, "audio")
    assert len(subtitles_indices) > 0
    first_audio_track = tracks[subtitles_indices[0]]

    # act
    subtitles_count = mkvmergeutils.get_track_subtitles_count(first_audio_track)

    # assert
    assert subtitles_count is None


def test_get_container_properties_title():
    # Check setup dependencies
    assert mkvmerge_path != None
    assert test01_file_path != None
    assert test02_file_path != None

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(test01_file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    title1 = mkvmergeutils.get_container_properties_title(json_obj)

    # assert
    assert title1 == "Game of Life (1970)"

    # ------------------------------------------------------------------------------

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(test02_file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    title2 = mkvmergeutils.get_container_properties_title(json_obj)

    # assert
    assert title2 is None


def test_get_container_property():
    # Check setup dependencies
    assert mkvmerge_path != None
    assert test01_file_path != None
    assert test02_file_path != None

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(test01_file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    title1 = mkvmergeutils.get_container_property(json_obj, 'title')

    # assert
    assert title1 == "Game of Life (1970)"

    # ------------------------------------------------------------------------------

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(test02_file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    title2 = mkvmergeutils.get_container_property(json_obj, 'title')

    # assert
    assert title2 is None


def test_get_track_property_value():
    # Check setup dependencies
    assert mkvmerge_path != None
    assert test01_file_path != None

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(test01_file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    subtitles_indices = mkvmergeutils.get_tracks_indice_by_type(tracks, "subtitles")
    assert len(subtitles_indices) > 0
    first_subtitles_track_index = subtitles_indices[0]

    # act
    default_track = mkvmergeutils.get_track_property_value(json_obj, first_subtitles_track_index, 'default_track')
    do_not_exists = mkvmergeutils.get_track_property_value(json_obj, first_subtitles_track_index, 'do_not_exists')

    # assert
    assert default_track != None and default_track == True
    assert do_not_exists is None


def test_set_track_property_value():
    # Check setup dependencies
    assert mkvmerge_path != None
    assert test01_file_path != None

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(test02_file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    subtitles_indices = mkvmergeutils.get_tracks_indice_by_type(tracks, "subtitles")
    assert len(subtitles_indices) > 0
    first_subtitles_track_index = subtitles_indices[0]
    default_track = mkvmergeutils.get_track_property_value(json_obj, first_subtitles_track_index, 'default_track')

    # act
    mkvmergeutils.set_track_property_value(json_obj, first_subtitles_track_index, 'do_not_exists', 'yes-i-do')

    # assert
    assert mkvmergeutils.get_track_property_value(json_obj, first_subtitles_track_index, 'do_not_exists') != None


def test_set_track_flag():
    # Check setup dependencies
    assert mkvmerge_path != None
    assert test01_file_path != None

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(test01_file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    result1 = mkvmergeutils.set_track_flag(json_obj, 1, 'VFQ')
    result5 = mkvmergeutils.set_track_flag(json_obj, 5, 'VFF')
    result6 = mkvmergeutils.set_track_flag(json_obj, 6, 'VFI')

    # assert
    assert result1
    assert result5
    assert result6
    name1 = mkvmergeutils.get_track_property_value(json_obj, 1, 'track_name')
    name5 = mkvmergeutils.get_track_property_value(json_obj, 5, 'track_name')
    name6 = mkvmergeutils.get_track_property_value(json_obj, 6, 'track_name')
    assert name1 == 'this is a less important eac3 french track (VFQ)'
    assert name5 == 'this is a ac3 canadian french track (VFF)'
    assert name6 == 'this might be foreign languages subtitles (VFI)'

    # assert setting a flag on a track that has no name
    # arrange
    mkvmergeutils.set_track_property_value(json_obj, 2, 'track_name', None)
    mkvmergeutils.set_track_property_value(json_obj, 2, 'language', 'und')
    mkvmergeutils.set_track_property_value(json_obj, 2, 'language_ietf', 'und')
    # act
    result2 = mkvmergeutils.set_track_flag(json_obj, 2, 'VFQ')
    # assert
    assert result2
    name2 = mkvmergeutils.get_track_property_value(json_obj, 2, 'track_name')
    assert name2 == '(VFQ)'

    # assert setting a flag on a track that has existing flags
    # arrange
    mkvmergeutils.set_track_property_value(json_obj, 2, 'track_name', 'AC3 5.1 (ZZZ,YYY)')
    mkvmergeutils.set_track_property_value(json_obj, 2, 'language', 'und')
    mkvmergeutils.set_track_property_value(json_obj, 2, 'language_ietf', 'und')
    # act
    result2 = mkvmergeutils.set_track_flag(json_obj, 2, 'VFQ')
    # assert
    assert result2
    name2 = mkvmergeutils.get_track_property_value(json_obj, 2, 'track_name')
    assert name2 == 'AC3 5.1 (ZZZ,YYY,VFQ)'

    # assert an exception is thrown when setting a flag that is opposing the existing language
    # arrange
    mkvmergeutils.set_track_property_value(json_obj, 2, 'track_name', 'AC3 5.1 (VFF)')
    mkvmergeutils.set_track_property_value(json_obj, 2, 'language', 'eng')
    mkvmergeutils.set_track_property_value(json_obj, 2, 'language_ietf', 'en-US')
    # act,assert
    with pytest.raises(Exception) as e_info:
        result2 = mkvmergeutils.set_track_flag(json_obj, 2, 'VFQ')


def test_get_container_duration_ms():
    # Check setup dependencies
    assert mkvmerge_path != None
    assert test01_file_path != None

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(test01_file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    actual_length_ms = mkvmergeutils.get_container_duration_ms(json_obj)
    expected_length_ms = 1*60*1000 # 1 min

    # assert
    assert abs(expected_length_ms - actual_length_ms) < 50


def test_load_media_file_info_invalid():
    # act
    result = mkvmergeutils.load_media_file_info("i-do-not-exists.json")

    # assert
    assert result is None


def test_get_media_file_info_invalid():
    # assert an exception is thrown
    with pytest.raises(Exception) as e_info:
        result = mkvmergeutils.get_media_file_info("i-do-not-exists.mkv")


def test_get_codec_friendly_name():
    assert mkvmergeutils.get_codec_friendly_name("MPEG-4p2") == "MPEG4" # *.avi
    assert mkvmergeutils.get_codec_friendly_name("MPEG-1/2") == "MPEG2" # *.mpg or *.mpeg
    assert mkvmergeutils.get_codec_friendly_name("AVC") == "H264" # H.264 files
    assert mkvmergeutils.get_codec_friendly_name("H.264") == "H264"
    assert mkvmergeutils.get_codec_friendly_name("H.265") == "HEVC" # H.265 files

    # subtitles
    assert mkvmergeutils.get_codec_friendly_name("SubRip") == "SRT"
    assert mkvmergeutils.get_codec_friendly_name("SubStationAlpha") == "ASS"
    assert mkvmergeutils.get_codec_friendly_name("HDMV PGS") == "PGS"


def test_get_first_video_track_codec_friendly_name():
    # Check setup dependencies
    assert mkvmerge_path != None
    assert test01_file_path != None

    # -------------------------------------------
    #               test01.mkv
    # -------------------------------------------

    # arrange

    json_obj = mkvmergeutils.get_media_file_info(test01_file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    codec = mkvmergeutils.get_first_video_track_codec_friendly_name(tracks)

    # assert
    assert codec == "H264"

    # -------------------------------------------
    #               test03.mkv
    # -------------------------------------------

    # arrange

    json_obj = mkvmergeutils.get_media_file_info(test03_file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    codec = mkvmergeutils.get_first_video_track_codec_friendly_name(tracks)

    # assert
    assert codec == "HEVC"


def test_get_track_name_flags_from_filename():
    assert mkvmergeutils.get_track_name_flags_from_filename('Star Wars: Episode IV A New Hope (1977) - VF2') == 'VF2'
    assert mkvmergeutils.get_track_name_flags_from_filename('Star Wars: Episode V The Empire Strikes Back (1980) VFF.H264') == 'VFF'
    assert mkvmergeutils.get_track_name_flags_from_filename('Star Wars: Episode VI Return of the Jedi (1983) French VFQ') == 'VFQ'
    assert mkvmergeutils.get_track_name_flags_from_filename('Star Wars: Episode I The Phantom Menace (1999) - VFI') == 'VFI'
    assert mkvmergeutils.get_track_name_flags_from_filename('Star Wars: Episode II Attack of the Clones (2002) - VO') == 'VO'

    # assert VF2 has priority over VFQ and VFF.
    flags = mkvmergeutils.get_track_name_flags_from_filename('Star Wars: Episode III Revenge of the Sith (2005)  - VF2,VFF,VFQ,VFI,VO')
    assert flags == "VF2"
