import argparse
import os
import sys
import getpass
import subprocess
import json
import copy

import findutils
import fileutils
import mkvtoolnixutils
import mkvmergeutils

# Constants
# N/A

def print_header():
    print("mkv4cafr v1.0")


# Parse output directory
# See https://gist.github.com/harrisont/ecb340616ab6f7cf11f99364fd57ef7e
def directory(raw_path):
    if not os.path.isdir(raw_path):
        raise argparse.ArgumentTypeError('"{}" is not an existing directory'.format(raw_path))
    return os.path.abspath(raw_path)


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

    # Set forced flag to subtitles that contains less than 150 entries or the string "force" in their name
    subtitles_tracks_indice = mkvmergeutils.get_tracks_indice_by_type(tracks, 'subtitles')
    for track_index in subtitles_tracks_indice:
        track = tracks[track_index]
        if not "properties" in track:
            continue
        properties = track['properties']

        # Set forced flag for subtitles that have less than 150 entries
        # (validate with property 'tag_number_of_frames' first)
        tag_number_of_frames_str = properties['tag_number_of_frames'] if 'tag_number_of_frames' in properties else 0
        tag_number_of_frames = int(tag_number_of_frames_str)
        if (tag_number_of_frames > 0 and tag_number_of_frames <= 150):
            json_obj["tracks"][track_index]["properties"]["forced_track"] = True
        # (then validate with property 'num_index_entries')
        num_index_entries = properties['num_index_entries'] if 'num_index_entries' in properties else 0
        if (num_index_entries > 0 and num_index_entries <= 150):
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


def update_properties_as_per_preferences(json_obj: dict):
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
    update_audio_tracks_rename_all_track_names(json_copy)
    update_audio_tracks_default_track(json_copy)
    update_subtitle_tracks_set_forced_flag_if_required(json_copy)
    update_subtitle_tracks_default_track_from_forced_flag(json_copy)
    
    return json_copy


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
        args.append("--set")
        args.append("title=" + new_title)

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
                args.append("--set")
                args.append("{name}={value}".format(name=mkvpropedit_set_argument, value=value))

                # Remember last edited track index
                previous_track_index_edit = i

    if (len(args) <= 2):
        # We did not build an actual command besides the 2 mandatory arguments
        # Return an empty list instead
        return list()

    # Return the commands list
    return args


def main():
    print_header()

    # Parse command line arguments
    # See https://stackoverflow.com/questions/20063/whats-the-best-way-to-parse-command-line-arguments for example.
    parser = argparse.ArgumentParser(description='mkv4cafr sets properties of mkv files for Canadian French viewers')

    parser.add_argument('-i', '--input', type=argparse.FileType('r'), help='input mkv file', required=True)
    parser.add_argument('-o', '--output', type=directory, default=os.path.curdir, help='output mkv file')
    parser.add_argument('-e', '--edit-in-place', action='store_true', help='Process input file in place')

    try:
        args = parser.parse_args()
    except Exception as e:
        print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")    

    print("Argument values:")
    print("  input file: " + str(args.input.name))
    print("  output directory: " + str(args.output))
    print("  edit-in-place: " + str(args.edit_in_place))

    # Search for mkvpropedit on the system
    mkvtoolnix_install_path = mkvtoolnixutils.find_mkvtoolnix_dir_in_path()
    if mkvtoolnix_install_path is None or not os.path.isdir(mkvtoolnix_install_path):
        print("MKVToolNix not found in PATH.")

        print("Searching known installation directories...")
        mkvtoolnix_install_path = mkvtoolnixutils.find_mkvtoolnix_dir_on_system()
        if mkvtoolnix_install_path is None or not os.path.isdir(mkvtoolnix_install_path):
            print("MKVToolNix not found on system.\n")
            sys.exit(1)

        # Found, but not in PATH
        os.environ['PATH'] = mkvtoolnix_install_path + os.pathsep + os.environ['PATH']
    mkvmerge_exec_path    = os.path.join(mkvtoolnix_install_path, "mkvmerge"    + findutils.get_executable_file_extension_name())
    mkvpropedit_exec_path = os.path.join(mkvtoolnix_install_path, "mkvpropedit" + findutils.get_executable_file_extension_name())
    print("Found mkvpropedit: " + mkvpropedit_exec_path)

    # Validate if file exists
    input_abspath = os.path.abspath(args.input.name)
    if not os.path.isfile(input_abspath):
        print("File '" + input_abspath + "' not found.")
        return 1

    # Parse media json
    print("Getting media information...")
    try:
        media_json_bytes = subprocess.check_output(["mkvmerge", "-J", input_abspath])                       
    except subprocess.CalledProcessError as procexc:                                                                                                   
        print("Failed to get json metadata for file '" + input_abspath + "'. Error code: ", procexc.returncode, procexc.output)
        return 1
    media_json_str = media_json_bytes.decode("utf-8")

    # Parse media json
    try:
        json_obj = json.loads(media_json_str)
    except Exception as e:
        print(str(e))

    # Update
    json_copy = update_properties_as_per_preferences(json_obj)

    # DEBUG:
    #json_copy['tracks'][1] = json_obj['tracks'][1]
    #json_copy['tracks'][2] = json_obj['tracks'][2]
    #json_copy['tracks'][3] = json_obj['tracks'][3]
    #json_copy['tracks'][4] = json_obj['tracks'][4]

    # Save metadata for debugging, if possible.
    # Only required if you edit in place.
    if (args.edit_in_place):
        try:
            with open(input_abspath + ".backup.json", "wb") as binary_file:
                binary_file.write(media_json_bytes)
        except Exception as e: pass

        try:
            with open(input_abspath + ".fix.json", "w") as text_file:
                #json.dump(json_copy, text_file)
                #json_copy_str = json.dumps(json_copy, indent=4)
                #print >> text_file, json_copy
                json.dump(json_copy, text_file, indent=2)
        except Exception as e: pass

    # Compute difference between json_obj and json_copy
    json_diff = compute_json_differences(json_obj, json_copy)

    has_diff = bool(json_diff)
    if (not has_diff):
        print("No modification required in input file metadata.")
        return 0
    
    print("Input file requires the following changes in metadata:")
    diff_str = json.dumps(json_diff, indent=2)
    print(diff_str)

    # Set the target file to edit if we do not edit-in-place
    target_file = input_abspath
    if (not args.edit_in_place):
        print("Copying input file to output directory.")
        target_file = fileutils.get_copy_file_to_directory_target(input_abspath, str(args.output))
        success = fileutils.copy_file(input_abspath, target_file)
        if (not success):
            print("Failed to copy file '" + target_file + "' to directory.")
            return 1
    input_abspath = "" # Make sure the rest of the code do not use the input file as reference

    # Change the target file to be modified

    # Build edit-in-place command    
    mkvpropedit_args = get_mkvpropedit_args_for_diff(json_diff, target_file)
    if (mkvpropedit_args is None or len(mkvpropedit_args) == 0):
        print("Failed to get mkvpropedit command to edit file.")
        return 1

    # Update metadata
    try:
        print("Updating meta data of file '" + target_file + "'.")
        subprocess.check_output(mkvpropedit_args)
    except subprocess.CalledProcessError as procexc:                                                                                                   
        print("Failed to execute command '" + " ".join(mkvpropedit_args) + "'.\n")

        output_str = procexc.output.decode("utf-8")
        print("Error code: ", procexc.returncode, output_str)
        return 1
    print("done.")


if __name__ == "__main__":
    main()
