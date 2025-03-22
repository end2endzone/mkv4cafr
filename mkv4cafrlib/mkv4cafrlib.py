import argparse
import os
import sys
import getpass
import subprocess
import json
import copy
import glob

from mkv4cafrlib import findutils
from mkv4cafrlib import fileutils
from mkv4cafrlib import mkvtoolnixutils
from mkv4cafrlib import mkvmergeutils
from mkv4cafrlib import jsonutils

# Constants
MAX_SUBTITLES_PER_HOUR_RATIO = 75.0

def update_video_tracks_set_default_track_flag(json_obj: dict):
    tracks = json_obj['tracks'] if 'tracks' in json_obj else None
    if (tracks is None):
        return

    # Set video tracks as default tracks
    video_tracks_indice = mkvmergeutils.get_tracks_indice_by_type(tracks, 'video')
    for track_index in video_tracks_indice:
        # Update the track
        json_obj['tracks'][track_index]['properties']['default_track'] = True


def update_video_tracks_remove_track_name(json_obj: dict):
    tracks = json_obj['tracks'] if 'tracks' in json_obj else None
    if (tracks is None):
        return

    # Remove name from video tracks
    video_tracks_indice = mkvmergeutils.get_tracks_indice_by_type(tracks, 'video')
    for track_index in video_tracks_indice:
        # Update the track
        json_obj['tracks'][track_index]['properties']['track_name'] = ""


def update_set_language_from_track_name_hints(json_obj: dict):
    tracks = json_obj['tracks'] if 'tracks' in json_obj else None
    if (tracks is None):
        return

    # Force language of audio/subtitles if a language hint is found in the track's name
    tracks_indice = mkvmergeutils.get_tracks_indice_by_type(tracks, ['audio', 'subtitles'])
    for track_index in tracks_indice:
        # Update the track
        track = json_obj['tracks'][track_index]
        if not "properties" in track:
            continue
        flags = mkvmergeutils.get_track_name_flags(track)
        if flags is None:
            continue

        if (flags.find("VFQ") != -1):
            json_obj['tracks'][track_index]['properties']['language'] = "fre"
            json_obj['tracks'][track_index]['properties']['language_ietf'] = "fr-CA"
        elif (flags.find("VFF") != -1):
            json_obj['tracks'][track_index]['properties']['language'] = "fre"
            json_obj['tracks'][track_index]['properties']['language_ietf'] = "fr-FR"


def update_audio_tracks_language_or_track_name_from_input_file_name(json_obj: dict, input_file_path: str):
    tracks = json_obj['tracks'] if 'tracks' in json_obj else None
    if (tracks is None):
        return

    flags = mkvmergeutils.get_track_name_flags_from_filename(input_file_path)

    audio_tracks_indice = mkvmergeutils.get_tracks_indice_by_type(tracks, "audio")
    french_audio_tracks_indice = mkvmergeutils.filter_tracks_indice_by_language(tracks, audio_tracks_indice, ['fre'])

    total_audio_tracks_count = len(audio_tracks_indice)
    french_audio_tracks_count = len(french_audio_tracks_indice)

    # Handle cases where there is only a single French audio track.
    # The track's language can be deduced from the flag in the file's name
    if (flags in ['VFQ', 'VFF', 'VFI'] and french_audio_tracks_count == 1):
        track_index = french_audio_tracks_indice[0]

        track = json_obj['tracks'][track_index]
        if not "properties" in track:
            return

        match flags:
            case "VFQ":
                mkvmergeutils.set_track_flag(json_obj, track_index, flags)
            case "VFF":
                mkvmergeutils.set_track_flag(json_obj, track_index, flags)
            case "VFI":
                mkvmergeutils.set_track_flag(json_obj, track_index, flags)
            case _:
                pass

    if (flags in ['VF2'] and french_audio_tracks_count == 2):
        vfq_audio_tracks_indice     = mkvmergeutils.filter_tracks_indice_by_flag(tracks, audio_tracks_indice, ['VFQ'])
        vff_audio_tracks_indice     = mkvmergeutils.filter_tracks_indice_by_flag(tracks, audio_tracks_indice, ['VFF'])
        vfi_audio_tracks_indice     = mkvmergeutils.filter_tracks_indice_by_flag(tracks, audio_tracks_indice, ['VFI'])
        vfq_audio_tracks_count = len(vfq_audio_tracks_indice)
        vff_audio_tracks_count = len(vff_audio_tracks_indice)
        vfi_audio_tracks_count = len(vfi_audio_tracks_indice)
    
        if (vfi_audio_tracks_count > 0):
            return # We do not know which tracks must be forced set to VFF or VFQ
        
        # Force VFF on the second track if a single VFQ track is found
        if (vfq_audio_tracks_count == 1 and vff_audio_tracks_count == 0):
            # A VFQ track is found. The other french track must be forced to VFF
            for track_index in french_audio_tracks_indice:
                # Ignore VFQ tracks
                if (track_index in vfq_audio_tracks_indice):
                    continue

                # Update the track
                mkvmergeutils.set_track_flag(json_obj, track_index, "VFF")

                # Update
                vff_audio_tracks_indice.append(track_index)
                vff_audio_tracks_count = len(vff_audio_tracks_indice)

        # Force VFQ on the second track if a single VFF track is found
        if (vfq_audio_tracks_count == 0 and vff_audio_tracks_count == 1):
            # A VFF track is found. The other french track must be forced to VFQ
            for track_index in french_audio_tracks_indice:
                # Ignore VFF tracks
                if (track_index in vff_audio_tracks_indice):
                    continue

                # Update the track
                mkvmergeutils.set_track_flag(json_obj, track_index, "VFQ")

                # Update
                vfq_audio_tracks_indice.append(track_index)
                vfq_audio_tracks_count = len(vfq_audio_tracks_indice)
        
        # If a single english audio track is left, then it must certainy be VO
        # refresh counters
        audio_tracks_indice = mkvmergeutils.get_tracks_indice_by_type(tracks, "audio")
        french_audio_tracks_indice  = mkvmergeutils.filter_tracks_indice_by_language(tracks, audio_tracks_indice, ['fre'])
        total_audio_tracks_count = len(audio_tracks_indice)
        french_audio_tracks_count = len(french_audio_tracks_indice)

        english_audio_tracks_indice  = mkvmergeutils.filter_tracks_indice_by_language(tracks, audio_tracks_indice, ['eng'])
        if ((total_audio_tracks_count - french_audio_tracks_count) == 1 and len(english_audio_tracks_indice) == 1 ):
            # Only VF2 containers should be have their English audio track automatically flagged as 'VO'.
            track_index = english_audio_tracks_indice[0]

            # Update the track
            mkvmergeutils.set_track_flag(json_obj, track_index, "VO")


    # Refresh
    french_audio_tracks_indice  = mkvmergeutils.filter_tracks_indice_by_language(tracks, audio_tracks_indice, ['fre'])
    vfq_audio_tracks_indice     = mkvmergeutils.filter_tracks_indice_by_flag(tracks, audio_tracks_indice, ['VFQ'])
    vff_audio_tracks_indice     = mkvmergeutils.filter_tracks_indice_by_flag(tracks, audio_tracks_indice, ['VFF'])
    vfi_audio_tracks_indice     = mkvmergeutils.filter_tracks_indice_by_flag(tracks, audio_tracks_indice, ['VFI'])
    french_audio_tracks_count = len(french_audio_tracks_indice)
    vfq_audio_tracks_count = len(vfq_audio_tracks_indice)
    vff_audio_tracks_count = len(vff_audio_tracks_indice)
    vfi_audio_tracks_count = len(vfi_audio_tracks_indice)

    # Final check
    if (flags in ['VF2'] and vfi_audio_tracks_count == 0 and (vfq_audio_tracks_count == 0 or vff_audio_tracks_count == 0)):
        print("WARNING: Failed to identify VFQ and VFF tracks in VF2 filename '" + input_file_path + "'.")


def update_audio_tracks_rename_all_track_names(json_obj: dict):
    tracks = json_obj['tracks'] if 'tracks' in json_obj else None
    if (tracks is None):
        return

    # Rename audio tracks
    audio_tracks_indice = mkvmergeutils.get_tracks_indice_by_type(tracks, 'audio')
    for track_index in audio_tracks_indice:
        # Update the track
        new_name = mkvmergeutils.get_track_auto_generated_name(json_obj['tracks'][track_index])
        json_obj['tracks'][track_index]['properties']['track_name'] = new_name


def update_audio_tracks_default_track(json_obj: dict):
    tracks = json_obj['tracks'] if 'tracks' in json_obj else None
    if (tracks is None):
        return

    # Update default audio track as per preferences
    first_default_audio_track_id = mkvmergeutils.get_first_default_track_id_for_type(tracks, 'audio')
    best_audio_track_id = mkvmergeutils.get_best_track_id_for_type(tracks, 'audio')

    # Unset all defaults audio tracks
    audio_tracks_indice = mkvmergeutils.get_tracks_indice_by_type(tracks, 'audio')
    for track_index in audio_tracks_indice:
        json_obj['tracks'][track_index]['properties']['default_track'] = False

    # Set default_track from "best"
    if ( best_audio_track_id != mkvmergeutils.INVALID_TRACK_ID ):
        track_index = mkvmergeutils.get_track_index_from_id(tracks, best_audio_track_id)
        json_obj["tracks"][track_index]["properties"]["default_track"] = True
    elif ( first_default_audio_track_id != mkvmergeutils.INVALID_TRACK_ID ):
        track_index = mkvmergeutils.get_track_index_from_id(tracks, first_default_audio_track_id)
        json_obj["tracks"][track_index]["properties"]["default_track"] = True


def update_subtitle_tracks_set_forced_flag_if_required(json_obj: dict):
    tracks = json_obj['tracks'] if 'tracks' in json_obj else None
    if (tracks is None):
        return

    # Set forced flag to subtitles that contains less than 75 entries per hour or the string "force" in their name
    subtitles_tracks_indice = mkvmergeutils.get_tracks_indice_by_type(tracks, 'subtitles')
    for track_index in subtitles_tracks_indice:
        track = tracks[track_index]
        if not "properties" in track:
            continue
        properties = track['properties']

        # Set forced flag for subtitles that have less than 75 entries per hour
        track_subtitles_count = mkvmergeutils.get_track_subtitles_count(track)
        if (track_subtitles_count > 0):
            container_duration_ms = mkvmergeutils.get_container_duration_ms(json_obj)
            if (container_duration_ms > 0):
                container_duration_hours = container_duration_ms/3600000.0
                subtitles_per_hour = track_subtitles_count / container_duration_hours
                if (subtitles_per_hour < MAX_SUBTITLES_PER_HOUR_RATIO):
                    json_obj["tracks"][track_index]["properties"]["forced_track"] = True

        # Check if word "forced" is found, it is propably a forced subtible track
        track_name = properties['track_name'] if 'track_name' in properties else ""
        track_name = track_name.upper()
        if ( track_name.find("FORCE") != -1 or track_name.find("FORCÉ") != -1 ):
            json_obj["tracks"][track_index]["properties"]["forced_track"] = True


def update_subtitle_tracks_default_track_from_forced_flag(json_obj: dict):
    tracks = json_obj['tracks'] if 'tracks' in json_obj else None
    if (tracks is None):
        return

    # Update forced subtitles track as per preferences
    best_forced_subtitle_track_id = mkvmergeutils.get_best_forced_track_id_for_type(tracks, 'subtitles')

    # Unset all defaults subtitles tracks
    subtitles_tracks_indice = mkvmergeutils.get_tracks_indice_by_type(tracks, 'subtitles')
    for track_index in subtitles_tracks_indice:
        json_obj['tracks'][track_index]['properties']['default_track'] = False

    # Set default_track from "best"
    if ( best_forced_subtitle_track_id != mkvmergeutils.INVALID_TRACK_ID ):
        track_index = mkvmergeutils.get_track_index_from_id(tracks, best_forced_subtitle_track_id)
        json_obj["tracks"][track_index]["properties"]["default_track"] = True


def update_properties_as_per_preferences(json_obj: dict, input_file_path: str):
    # Make a deep copy of all the json data
    json_copy = copy.deepcopy(json_obj)

    tracks = json_copy['tracks'] if 'tracks' in json_copy else None
    if (tracks is None):
        return

    # Clear the title, if any
    try:
        json_copy['container']['properties']['title'] = ""
    except Exception as e: pass
    
    update_video_tracks_set_default_track_flag(json_copy)
    update_video_tracks_remove_track_name(json_copy)
    update_set_language_from_track_name_hints(json_copy)
    update_audio_tracks_language_or_track_name_from_input_file_name(json_copy, input_file_path)
    update_audio_tracks_rename_all_track_names(json_copy)
    update_audio_tracks_default_track(json_copy)
    update_subtitle_tracks_set_forced_flag_if_required(json_copy)
    update_subtitle_tracks_default_track_from_forced_flag(json_copy)
    
    return json_copy


def validate_inconsistencies(json_obj, input_abspath):
    tracks = json_obj['tracks'] if 'tracks' in json_obj else None
    if (tracks is None):
        return
    
    audio_tracks_indice = mkvmergeutils.get_tracks_indice_by_type(tracks, "audio")
    
    # Validate a maximum of a single audio track with flag VO
    vo_audio_tracks_indice = mkvmergeutils.filter_tracks_indice_by_flag(tracks, audio_tracks_indice, ['VO'])
    vo_audio_tracks_count = len(vo_audio_tracks_indice)
    if (vo_audio_tracks_count > 1):
        print("Error, multiple audio tracks were identified with the VO flag: " + ",".join(str(x) for x in vo_audio_tracks_indice) + ".")
        return False
    
    # Validate that a VFI audio track do has language set to FR and language_ietf is empty.
    vfi_audio_tracks_indice = mkvmergeutils.filter_tracks_indice_by_flag(tracks, audio_tracks_indice, ['VFI'])
    for track_index in vfi_audio_tracks_indice:
        track_language = mkvmergeutils.get_track_property_value(json_obj, track_index, 'language')
        if (not track_language == "fre"):
            print("Error, track index " + str(track_index) + " is flagged as VFI but language is set to '" + track_language + "'. Expected: 'fre'.")
            return False

        track_language_ietf = mkvmergeutils.get_track_property_value(json_obj, track_index, 'language_ietf')
        if (not track_language_ietf is None):
            track_language_ietf = str(track_language_ietf)
            if (track_language_ietf.find('-') != -1):
                print("Error, track index " + str(track_index) + " is flagged as VFI but language_ietf is set to '" + track_language_ietf + "' which is region specific.")
                return False

    return True


def compute_json_differences(json_left: dict, json_right: dict):
    json_diff = dict()

    diff_found = False

    # Compare number of tracks
    tracks_left = json_left['tracks'] if 'tracks' in json_left else None
    tracks_right = json_right['tracks'] if 'tracks' in json_right else None
    if (tracks_left is None or
        tracks_right is None):
        return None
    num_tracks_left = len(tracks_left)
    num_tracks_right = len(tracks_right)
    if (num_tracks_left != num_tracks_right):
        return None

    # Compare title
    title_left = mkvmergeutils.get_container_properties_title(json_left)
    title_right = mkvmergeutils.get_container_properties_title(json_right)
    if (not title_left is None and
        not title_right is None and
        title_left != title_right):

        # Title has changed
        json_diff['container'] = dict()
        json_diff['container']['properties'] = dict()
        json_diff['container']['properties']['title'] = title_right
        diff_found = True

    # Create an empty track list
    if (not 'tracks' in json_diff):
        json_diff['tracks'] = list()

    # Compare tracks one by one
    for i in range(len(tracks_right)):
        track_left = tracks_left[i]
        track_right = tracks_right[i]

        # Check for errors
        if (track_left is None or
            track_right is None):
            return None
        
        # Check integrity
        type_left = track_left['type'] if 'type' in track_left else None
        type_right = track_right['type'] if 'type' in track_right else None
        if (type_left is None or
            type_right is None):
            return None
        id_left = track_left['id'] if 'id' in track_left else None
        id_right = track_right['id'] if 'id' in track_right else None
        if (id_left is None or
            id_right is None):
            return None

        # At this point, we are certain that we are dealing with the same track
        
        # Always add an empty track to the list
        json_diff['tracks'].append(dict())

        # Remember the index to be able to match the original tracks by index
        track_index = len(json_diff['tracks']) - 1

        # If no change in these tracks is found, skip those
        if (track_left == tracks_right):
            # Next tracks
            continue

        properties_left = track_left['properties'] if 'properties' in track_left else None
        properties_right = track_right['properties'] if 'properties' in track_right else None
        if (properties_left is None or
            properties_right is None):
            return None

        # If no property has changed
        if (properties_left == properties_right):
            # Next tracks
            continue

        # Compare properties one by one
        property_names = mkvmergeutils.get_track_supported_property_names()
        for property_name in property_names:
            # Get value
            property_value_left = properties_left[property_name] if property_name in properties_left else None
            property_value_right = properties_right[property_name] if property_name in properties_right else None

            # Check if property is not set on both sides (left and right)
            if (property_value_left is None and 
                property_value_right is None):
                continue
            # Force right property as an empty string (this will effectively force a change when transionning from `None` to ``. )
            if (property_value_right is None):
                property_value_right = ""

            if (property_value_left != property_value_right):
                # Property has changed

                # Check for existing 'properties' container in the track
                if (not 'properties' in json_diff['tracks'][track_index]):
                    json_diff['tracks'][track_index]['properties'] = dict()

                # Set the property value as a diff
                json_diff['tracks'][track_index]['properties'][property_name] = property_value_right
                diff_found = True
                
        # end for each property_name

        # Check to see if new track was added

    # end for each tracks

    # Allow returning an empty dict() if no differences was found
    if (diff_found == False):
        json_diff = dict()
    
    return json_diff


def get_mkvpropedit_args_for_diff(json_obj: dict, file_path: str):
    args = list()
    args.append("mkvpropedit")
    args.append(file_path)
    
    new_title = mkvmergeutils.get_container_properties_title(json_obj)
    if (not new_title is None):
        args.append("--edit")
        args.append("info")
        if (new_title != ""):
            args.append("--set")
            args.append("title=" + new_title)
        else:
            args.append("--delete")
            args.append("title")

    # Get all tracks, if any
    if ('tracks' in json_obj):
        tracks = json_obj['tracks']

        # For each tracks
        previous_track_index_edit = -1
        for i in range(len(tracks)):
            track = tracks[i]

            # Skip track if no 'properties'
            if (not 'properties' in track):
                # Next track
                continue

            # For each property
            property_names = mkvmergeutils.get_track_supported_property_names()
            for property_name in property_names:
                value = track['properties'][property_name] if property_name in track['properties'] else None
                if (value is None):
                    # Next property
                    continue

                mkvpropedit_set_argument = mkvmergeutils.get_mkvpropedit_set_argument_for_mkvmerge_property(property_name)
                if (mkvpropedit_set_argument is None):
                    print("Error, unable to get mkvpropedit property name for property '" + property_name + "'.")
                    return None
                
                if (i != previous_track_index_edit):
                    args.append("--edit")
                    args.append("track:{0}".format(i+1)) # mkvpropedit's track number starts at 1
                
                if (value != ""):
                    args.append("--set")
                    args.append("{prop_name}={prop_value}".format(prop_name=mkvpropedit_set_argument, prop_value=value))
                else:
                    args.append("--delete")
                    args.append("{prop_name}".format(prop_name=mkvpropedit_set_argument))

                # Remember last edited track index
                previous_track_index_edit = i

    if (len(args) <= 2):
        # We did not build an actual command besides the 2 mandatory arguments
        # Return an empty list instead
        return list()

    # Return the commands list
    return args

