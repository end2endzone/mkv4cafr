import argparse
import os
import sys
import getpass
import subprocess
import json

# Constants
INVALID_TRACK_ID = -1
INVALID_TRACK_INDEX = -1


# Parse output directory
# See https://gist.github.com/harrisont/ecb340616ab6f7cf11f99364fd57ef7e
def directory(raw_path):
    if not os.path.isdir(raw_path):
        raise argparse.ArgumentTypeError('"{}" is not an existing directory'.format(raw_path))
    return os.path.abspath(raw_path)


def get_mkvpropedit_exec_name():
    if os.name == 'nt' or os.name == 'win32':
        return "mkvpropedit.exe"
    else:
        return "mkvpropedit"


def get_mkvpropedit_hints():
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


def find_file_in_path(file_name):
    path_list = os.environ['PATH'].split(os.pathsep)
    return find_file_in_hints(file_name, path_list)


def find_file_in_hints(file_name, hints):
    for path_entry in hints:
        full_path = os.path.join(path_entry,file_name)
        if os.path.isfile(full_path):
            return full_path
    return None


def get_tracks_indice_by_type(input_tracks: list, type: str):
    matching_track_indice = list()
    for i in range(len(input_tracks)):
        track = input_tracks[i]
        track_index = i
        #properties = track['properties']
        track_type = track['type']
        if track_type == type:
            matching_track_indice.append(track_index)
    return matching_track_indice


def get_language_friendly_name(name_tmp: str):
    name = name_tmp.upper()
    if name == "ENG":
        return "EN"
    elif name == "FRE":
        return "FR"
    return name


def get_codec_friendly_name(name: str):
    # audio
    if name == "E-AC-3":
      return "E-AC3"
    elif name == "AC-3":
      return "AC3"
    elif name == "AAC":
      return "AAC"

    # video
    elif name == "MPEG-1/2":
      return "MPEG2"
    elif name == "AVC/H.264/MPEG-4p10":
      return "H.264"
    elif name == "HEVC/H.265/MPEG-H":
      return "HEVC"
    elif name == "AV1":
      return "AV1"

    # subtitles
    elif name == "VobSub":
      return "VobSub"
    elif name == "SubRip/SRT":
      return "SRT"
    elif name == "HDMV PGS":
      return "PGS"

    return name


def get_audio_channel_layout_friendly_name(num_channels: int):
    if num_channels == 2:
        return "2.0"
    elif num_channels == 6:
        return "5.1"
    elif num_channels == 8:
        return "7.1"
    
    return "{0}.x".format(num_channels)


def get_first_video_track_codec_friendly_name(tracks: list):
    try:
        video_tracks_indice = get_tracks_indice_by_type(tracks, 'video')
        for track_index in video_tracks_indice:
            codec = tracks[track_index]['codedc']
            return get_codec_friendly_name(codec)
    except Exception as e: pass
    return None


def get_track_name_flags(track: dict):
    if not "properties" in track:
        return None
    properties = track['properties']
    
    track_name = str(properties['track_name']).upper() if 'track_name' in properties else None
    track_language_ietf = properties['language_ietf'] if 'language_ietf' in properties else None

    has_vff = (track_name.find("VFF") != -1)
    has_vfq = (track_name.find("VFQ") != -1)
    has_vfi = (track_name.find("VFI") != -1)
    has_vo = (track_name.find("VO") != -1)

    has_vff |= (track_language_ietf == "fr-FR")
    has_vfq |= (track_language_ietf == "fr-CA")

    if ( has_vff ):
      return "VFF"
    if ( has_vfq ):
      return "VFQ"
    if ( has_vfi ):
      return "VFI"
    if ( has_vo ):
      return "VO"

    return None


def get_track_auto_generated_name(track: dict):
    # Skip tracks that are not audio
    if "type" in track and track['type'] != 'audio':
        return None

    if not "properties" in track:
        return None
    properties = track['properties']

    language_friendly = get_language_friendly_name(properties['language']) if "language" in properties else None
    codec_friendly = get_codec_friendly_name(track['codec']) if "codec" in track else None
    channel_layout_friendly = get_audio_channel_layout_friendly_name(properties["audio_channels"]) if "audio_channels" in properties else None
    if  language_friendly is None or \
        codec_friendly is None or \
        channel_layout_friendly is None:
        return None

    flags = get_track_name_flags(track)

    new_name = language_friendly + " " + codec_friendly + " " + channel_layout_friendly
    if not flags is None:
      new_name = new_name + " (" + flags + ")"

    return new_name


def get_first_default_track_id_for_type(tracks: list, type: str):
    # Filter for tracks of the given type
    try:
        matching_tracks_indice = get_tracks_indice_by_type(tracks, type)
        for track_index in matching_tracks_indice:
            # Get track
            track = tracks[track_index]
            if not "properties" in track:
                continue
            properties = track['properties']

            # Check track properties
            is_default = properties['default_track'] if 'default_track' in properties else False
            track_id = track['id'] if 'id' in track else INVALID_TRACK_ID
            if is_default:
                return track_id
    except Exception as e: pass
    
    # No track with "defaut" flag set
    return INVALID_TRACK_ID


def get_first_default_track_id_for_indice(tracks: list, tracks_indice: list):
    # Filter for tracks of the given type
    try:
        for track_index in tracks_indice:
            # Get track
            track = tracks[track_index]
            if not "properties" in track:
                continue
            properties = track['properties']

            # Check track properties
            is_default = properties['default_track'] if 'default_track' in properties else False
            track_id = track['id'] if 'id' in track else INVALID_TRACK_ID
            if is_default:
                return track_id
    except Exception as e: pass
    
    # No track with "defaut" flag set
    return INVALID_TRACK_ID


def get_best_track_id_from_indice(tracks: list, tracks_indice: list):
    # Search for a VFQ track
    for track_index in tracks_indice:
        # Get track, properties and id
        track = tracks[track_index]
        if not "properties" in track:
            continue
        properties = track['properties']
        track_id = track['id'] if 'id' in track else INVALID_TRACK_ID

        # Check for flag
        flags = get_track_name_flags(track)
        if not flags is None and flags.find("VFQ") != -1:
            return track_id
        
    # Search for a VFF track
    for track_index in tracks_indice:
        # Get track, properties and id
        track = tracks[track_index]
        if not "properties" in track:
            continue
        properties = track['properties']
        track_id = track['id'] if 'id' in track else INVALID_TRACK_ID

        # Check for flag
        flags = get_track_name_flags(track)
        if not flags is None and flags.find("VFF") != -1:
            return track_id
    
    # Search for a French track
    for track_index in tracks_indice:
        # Get track, properties and id
        track = tracks[track_index]
        if not "properties" in track:
            continue
        properties = track['properties']
        track_id = track['id'] if 'id' in track else INVALID_TRACK_ID

        # Check language
        language = properties['language'] if 'language' in properties else ""
        language = language.upper()
        if language.find("FRE") != -1:
            return track_id
        
    # No track with VFQ, VFF or french language found.
    # Return existing default track
    existing_default_track_id = get_first_default_track_id_for_indice(tracks, tracks_indice)
    return existing_default_track_id


def get_best_track_id_for_type(tracks: list, type: str):
    # Filter for tracks of the given type
    try:
        matching_tracks_indice = get_tracks_indice_by_type(tracks, type)
    except Exception as e: pass

    # Find the best
    track_id = get_best_track_id_from_indice(tracks, matching_tracks_indice)
    return track_id


def get_best_forced_track_id_for_type(tracks: list, type: str):
    # Filter for tracks of the given type
    try:
        matching_tracks_indice = get_tracks_indice_by_type(tracks, type)
    except Exception as e: pass
    
    forced_track_indice = list()
    
    # Filter for forced tracks
    for track_index in matching_tracks_indice:
        # Get track, properties and id
        track = tracks[track_index]
        if not "properties" in track:
            continue
        properties = track['properties']
        track_id = track['id'] if 'id' in track else INVALID_TRACK_ID
        is_forced = properties['forced_track'] if 'forced_track' in properties else False
    
        if is_forced:
            forced_track_indice.append(track_index)

    # Find the best of the "forced list"
    track_id = get_best_track_id_from_indice(tracks, forced_track_indice)
    return track_id


def get_track_id_from_index(tracks: list, target_index: int):
    for i in range(len(tracks)):
        track = tracks[i]
        current_index = i
        current_id = track['id'] if 'id' in track else INVALID_TRACK_ID
        if target_index == current_index:
            return current_id
    return INVALID_TRACK_ID


def get_track_index_from_id(tracks: list, target_id: int):
    for i in range(len(tracks)):
        track = tracks[i]
        current_index = i
        current_id = track['id'] if 'id' in track else INVALID_TRACK_ID
        if target_id == current_id:
            return current_index
    return INVALID_TRACK_INDEX


def update_properties_as_per_preferences(json_obj: dict):
    json_copy = json_obj.copy()
    tracks = json_copy['tracks'] if 'tracks' in json_copy else None

    # Clear the title
    try:
        json_copy['container']['properties']['title'] = ""
    except Exception as e: pass
    
    # Set video tracks as default tracks
    try:
        video_tracks_indice = get_tracks_indice_by_type(tracks, 'video')
        for track_index in video_tracks_indice:
            # Update the track
            try:
                json_copy['tracks'][track_index]['properties']['default_track'] = True
            except Exception as e: pass
    except Exception as e: pass
    
    # Rename audio tracks
    try:
        audio_tracks_indice = get_tracks_indice_by_type(tracks, 'audio')
        for track_index in audio_tracks_indice:
            # Update the track
            try:
                new_name = get_track_auto_generated_name(json_copy['tracks'][track_index])
                json_copy['tracks'][track_index]['properties']['track_name'] = new_name
            except Exception as e: pass
    except Exception as e: pass

    # Update default audio track as per preferences
    first_default_audio_track_id = get_first_default_track_id_for_type(tracks, 'audio')
    best_audio_track_id = get_best_track_id_for_type(tracks, 'audio')
    # Unset all defaults audio tracks
    try:
        audio_tracks_indice = get_tracks_indice_by_type(tracks, 'audio')
        for track_index in audio_tracks_indice:
            try:
                json_copy['tracks'][track_index]['properties']['default_track'] = False
            except Exception as e: pass
    except Exception as e: pass
    if ( best_audio_track_id != INVALID_TRACK_ID ):
        track_index = get_track_index_from_id(tracks, best_audio_track_id)
        json_copy["tracks"][track_index]["properties"]["default_track"] = True
    elif ( first_default_audio_track_id != INVALID_TRACK_ID ):
        track_index = get_track_index_from_id(tracks, first_default_audio_track_id)
        json_copy["tracks"][track_index]["properties"]["default_track"] = True;

    # Set forced flag to subtitles that contains less than 150 entries or the string "force" in their name
    for i in range(len(tracks)):
        track = tracks[i]
        if not "properties" in track:
            continue
        properties = track['properties']

        # Set forced flag for subtitles that have less than 150 entries
        # (validate with property 'tag_number_of_frames' first)
        tag_number_of_frames_str = properties['tag_number_of_frames'] if 'tag_number_of_frames' in track else 0
        tag_number_of_frames = int(tag_number_of_frames_str)
        if (tag_number_of_frames > 0 and tag_number_of_frames <= 150):
            json_copy["tracks"][i]["properties"]["forced_track"] = True
        # (then validate with property 'num_index_entries')
        num_index_entries = properties['num_index_entries'] if 'num_index_entries' in track else 0
        if (num_index_entries > 0 and num_index_entries <= 150):
            json_copy["tracks"][i]["properties"]["forced_track"] = True

        # Check if word "forced" is found, it is propably a forced subtible track
        track_name = properties['track_name'] if 'track_name' in track else ""
        track_name = track_name.upper()
        if ( track_name.find("FORCE") != -1 ):
          json_copy["tracks"][i]["properties"]["forced_track"] = True
        
    # Update forced subtitles track as per preferences
    best_forced_track_id = get_best_forced_track_id_for_type(tracks, 'subtitles')
    # Unset all defaults subtitles tracks
    try:
        subtitles_tracks_indice = get_tracks_indice_by_type(tracks, 'subtitles')
        for track_index in subtitles_tracks_indice:
            try:
                json_copy['tracks'][track_index]['properties']['default_track'] = False
            except Exception as e: pass
    except Exception as e: pass
    if ( best_forced_track_id != INVALID_TRACK_ID ):
        track_index = get_track_index_from_id(tracks, best_forced_track_id)
        json_copy["tracks"][track_index]["properties"]["default_track"] = True

    return json_copy


def main():
    # Parse command line arguments
    # See https://stackoverflow.com/questions/20063/whats-the-best-way-to-parse-command-line-arguments for example.
    parser = argparse.ArgumentParser(description='mkv4cafr sets mkv properties for Canadian French viewers first')

    parser.add_argument('-i', '--input', type=argparse.FileType('r'), help='input mkv file', required=True)
    parser.add_argument('-o', '--output', type=directory, default=os.path.curdir, help='output mkv file')
    parser.add_argument('-e', '--edit-in-place', action='store_true', help='Process input file in place')

    args = parser.parse_args()

    print("Argument values:")
    print(args.input)
    print(args.output)
    print(args.edit_in_place)

    # Search for mkvpropedit on the system
    mkvpropedit_exec_filename = get_mkvpropedit_exec_name()
    print("Searching location of " + mkvpropedit_exec_filename + "...")
    mkvpropedit_exec_path = find_file_in_path(mkvpropedit_exec_filename)
    if mkvpropedit_exec_path is None:
        print("Program not found in PATH. Searching into know locations...")
        hints = get_mkvpropedit_hints()
        mkvpropedit_exec_path = find_file_in_hints(mkvpropedit_exec_filename, hints)
    if mkvpropedit_exec_path is None:
        print("Failed to find " + mkvpropedit_exec_filename + " on system.")
        return 1
    print("Found " + mkvpropedit_exec_filename + ": " + mkvpropedit_exec_path)

    # Adding directory to PATH so that we can call mkvpropedit without specifing the absolute path 
    mkvtoolnix_install_dir = os.path.dirname(mkvpropedit_exec_path)
    os.environ['PATH'] = mkvtoolnix_install_dir + os.pathsep + os.environ['PATH']

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
    print("done.")
    media_json_str = media_json_bytes.decode("utf-8")

    # Save metadata for debugging, if possible
    try:
        with open(input_abspath + ".json", "wb") as binary_file:
            binary_file.write(media_json_bytes)
    except Exception as e: pass

    # Parse media json
    try:
        json_obj = json.loads(media_json_str)
    except Exception as e:
        print(str(e))

    # Update
    json_copy = update_properties_as_per_preferences(json_obj)

    # Save new metadata for debugging, if possible
    try:
        with open(input_abspath + ".fix.json", "w") as text_file:
            #json.dump(json_copy, text_file)
            #json_copy_str = json.dumps(json_copy, indent=4)
            #print >> text_file, json_copy
            json.dump(json_copy, text_file, indent=2)
    except Exception as e: pass



if __name__ == "__main__":
    main()
