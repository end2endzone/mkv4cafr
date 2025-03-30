import pytest
import sys
import os
import subprocess
from mkv4cafrlib import mkvmergeutils
from mkv4cafrlib import mkvtoolnixutils
from mkv4cafrlib import findutils
from tests import testutils
from random import shuffle
from functools import cmp_to_key


def test_get_media_file_info():
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    medias_path = testutils.get_medias_dir_path()
    testfiles_path = testutils.get_test_files_dir_path()
    assert medias_path != None
    assert testfiles_path != None
    file_path = os.path.join(medias_path,"test01.mkv")
    assert os.path.isfile(file_path)

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(file_path)
    assert json_obj != None


def test_get_tracks_indice_by_type():
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    medias_path = testutils.get_medias_dir_path()
    testfiles_path = testutils.get_test_files_dir_path()
    assert medias_path != None
    assert testfiles_path != None
    file_path = os.path.join(medias_path,"test01.mkv")
    assert os.path.isfile(file_path)

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
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


def test_filter_tracks_indice_by_language():
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    medias_path = testutils.get_medias_dir_path()
    testfiles_path = testutils.get_test_files_dir_path()
    assert medias_path != None
    assert testfiles_path != None
    file_path = os.path.join(medias_path,"test01.mkv")
    assert os.path.isfile(file_path)

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(file_path)
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
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    medias_path = testutils.get_medias_dir_path()
    testfiles_path = testutils.get_test_files_dir_path()
    assert medias_path != None
    assert testfiles_path != None
    file_path = os.path.join(medias_path,"test01.mkv")
    assert os.path.isfile(file_path)

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(file_path)
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
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    medias_path = testutils.get_medias_dir_path()
    testfiles_path = testutils.get_test_files_dir_path()
    assert medias_path != None
    assert testfiles_path != None
    file_path = os.path.join(medias_path,"test_get_track_name_flags.mkv")
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
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    medias_path = testutils.get_medias_dir_path()
    testfiles_path = testutils.get_test_files_dir_path()
    assert medias_path != None
    assert testfiles_path != None
    file_path = os.path.join(medias_path,"test_get_track_auto_generated_name.mkv")
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
        'SPA TrueHD 5.1',
        'GER TrueHD 5.1',
        'EN AC3 5.1',
        'EN E-AC3 5.1',
        'EN Vorbis 5.1',
        'EN DTS 5.1',
        'MUL Opus 5.1',
        'MIS FLAC 7.1',
        'ZXX PCM 2.0'
    ]
    assert len(names) == len(expected_names)
    for i in range(len(names)):
        assert names[i] == expected_names[i]


def test_get_first_default_track_id_for_type():
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    testfiles_path = testutils.get_test_files_dir_path()
    assert testfiles_path != None
    file_path1 = os.path.join(testfiles_path,"test_get_first_default_track_id_for_type_id025.json")
    file_path2 = os.path.join(testfiles_path,"test_get_first_default_track_id_for_type_none.json")
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
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    testfiles_path = testutils.get_test_files_dir_path()
    assert testfiles_path != None
    file_path1 = os.path.join(testfiles_path,"test_get_best_track_id_from_indice_vfq_has_priority_over_default_and_vff_and_fr.json")
    file_path2 = os.path.join(testfiles_path,"test_get_best_track_id_from_indice_vff_has_priority_over_default_and_fr.json")
    file_path3 = os.path.join(testfiles_path,"test_get_best_track_id_from_indice_french_has_priority_over_default_and_english.json")
    file_path4 = os.path.join(testfiles_path,"test_get_best_track_id_from_indice_default_if_nothing_is_best.json")
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
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    testfiles_path = testutils.get_test_files_dir_path()
    assert testfiles_path != None
    file_path1 = os.path.join(testfiles_path,"test_get_best_forced_track_id_for_type_vfq_has_priority_over_default_and_vff_and_fr.json")
    file_path2 = os.path.join(testfiles_path,"test_get_best_forced_track_id_for_type_vff_has_priority_over_default_and_fr.json")
    file_path3 = os.path.join(testfiles_path,"test_get_best_forced_track_id_for_type_french_has_priority_over_default_and_english.json")
    file_path4 = os.path.join(testfiles_path,"test_get_best_forced_track_id_for_type_invalid_if_nothing_is_forced.json")
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
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    medias_path = testutils.get_medias_dir_path()
    assert medias_path != None
    file_path = os.path.join(medias_path,"test02.mkv")
    assert os.path.isfile(file_path)

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # sort tracks as per MKVToolNix GUI order.
    # without this sort, mkvmerge will output tracks in ID order
    # which makes 'index' and 'id' always he same (index == id).
    comparator_tracks_py3 = cmp_to_key(mkvtoolnixutils.compare_tracks)
    tracks.sort(key = comparator_tracks_py3)

    # act
    track_id_at_index3 = mkvmergeutils.get_track_id_from_index(tracks, 3)
    track_id_at_index9 = mkvmergeutils.get_track_id_from_index(tracks, 9)

    # assert
    assert track_id_at_index3 == 5
    assert track_id_at_index9 == mkvmergeutils.INVALID_TRACK_ID


def test_get_track_index_from_id():
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    medias_path = testutils.get_medias_dir_path()
    assert medias_path != None
    file_path = os.path.join(medias_path,"test02.mkv")
    assert os.path.isfile(file_path)

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # sort tracks as per MKVToolNix GUI order.
    # without this sort, mkvmerge will output tracks in ID order
    # which makes 'index' and 'id' always he same (index == id).
    comparator_tracks_py3 = cmp_to_key(mkvtoolnixutils.compare_tracks)
    tracks.sort(key = comparator_tracks_py3)

    # act
    track_index_for_id3 = mkvmergeutils.get_track_index_from_id(tracks, 3)
    track_index_for_id9 = mkvmergeutils.get_track_index_from_id(tracks, 9)

    # assert
    assert track_index_for_id3 == 1
    assert track_index_for_id9 == mkvmergeutils.INVALID_TRACK_ID


def test_get_track_subtitles_count():
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    medias_path = testutils.get_medias_dir_path()
    assert medias_path != None
    file_path = os.path.join(medias_path,"test01.mkv")
    assert os.path.isfile(file_path)

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(file_path)
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
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    medias_path = testutils.get_medias_dir_path()
    assert medias_path != None
    file_path1 = os.path.join(medias_path,"test01.mkv")
    file_path2 = os.path.join(medias_path,"test02.mkv")
    assert os.path.isfile(file_path1)
    assert os.path.isfile(file_path2)

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(file_path1)
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
    json_obj = mkvmergeutils.get_media_file_info(file_path2)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    title2 = mkvmergeutils.get_container_properties_title(json_obj)

    # assert
    assert title2 is None


def test_get_container_property():
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    medias_path = testutils.get_medias_dir_path()
    assert medias_path != None
    file_path1 = os.path.join(medias_path,"test01.mkv")
    file_path2 = os.path.join(medias_path,"test02.mkv")
    assert os.path.isfile(file_path1)
    assert os.path.isfile(file_path2)

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(file_path1)
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
    json_obj = mkvmergeutils.get_media_file_info(file_path2)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    title2 = mkvmergeutils.get_container_property(json_obj, 'title')

    # assert
    assert title2 is None


def test_get_track_property_value():
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    medias_path = testutils.get_medias_dir_path()
    assert medias_path != None
    file_path = os.path.join(medias_path,"test01.mkv")
    assert os.path.isfile(file_path)

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(file_path)
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
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    medias_path = testutils.get_medias_dir_path()
    assert medias_path != None
    file_path = os.path.join(medias_path,"test01.mkv")
    assert os.path.isfile(file_path)

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(file_path)
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
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    medias_path = testutils.get_medias_dir_path()
    assert medias_path != None
    file_path = os.path.join(medias_path,"test01.mkv")
    assert os.path.isfile(file_path)

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(file_path)
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


def test_get_container_duration_ms():
    # Check program dependencies
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert mkvtoolnix_install_path != None
    mkvmerge_path = findutils.find_exec_in_path("mkvmerge")
    assert mkvmerge_path != None

    # Check file dependencies
    medias_path = testutils.get_medias_dir_path()
    assert medias_path != None
    file_path = os.path.join(medias_path,"test01.mkv")
    assert os.path.isfile(file_path)

    # arrange

    # Load media info into a json dict
    json_obj = mkvmergeutils.get_media_file_info(file_path)
    assert json_obj != None
    assert "tracks" in json_obj
    tracks = json_obj['tracks']

    # act
    actual_length_ms = mkvmergeutils.get_container_duration_ms(json_obj)
    expected_length_ms = 1*60*1000 # 1 min

    # assert
    assert abs(expected_length_ms - actual_length_ms) < 50
