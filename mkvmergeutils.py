import subprocess
import json

# Constants
INVALID_TRACK_ID = -1
INVALID_TRACK_INDEX = -1


def get_tracks_indice_by_type(input_tracks: list, type: str):
    types = list()
    types.append(type)
    return get_tracks_indice_by_type(input_tracks, types)


def get_tracks_indice_by_type(input_tracks: list, accepted_types: list):
    matching_track_indice = list()
    for i in range(len(input_tracks)):
        track = input_tracks[i]
        track_index = i
        #properties = track['properties']
        track_type = track['type']
        if (track_type in accepted_types):
            matching_track_indice.append(track_index)
    return matching_track_indice


def filter_tracks_indice_by_language(input_tracks: list, pre_filtered_track_indice: list, accepted_languages: list):
    matching_track_indice = list()
    for i in range(len(input_tracks)):
        track = input_tracks[i]
        track_index = i

        # Skip this track if not already in pre_filtered_track_indice
        if (track_index not in pre_filtered_track_indice):
            continue

        if ("properties" not in track):
            continue
        properties = track['properties']

        track_language      = properties['language']        if 'language' in properties else ""
        track_language_ietf = properties['language_ietf']   if 'language_ietf' in properties else ""

        # Validate track's language against accepted languages.
        valid = False
        if (track_language != "" and track_language in accepted_languages):
            valid = True
        if (track_language_ietf != "" and track_language_ietf in accepted_languages):
            valid = True

        if (valid):
            matching_track_indice.append(track_index)
    return matching_track_indice


def filter_tracks_indice_by_flag(input_tracks: list, pre_filtered_track_indice: list, accepted_flags: list):
    matching_track_indice = list()
    for i in range(len(input_tracks)):
        track = input_tracks[i]
        track_index = i

        # Skip this track if not already in pre_filtered_track_indice
        if (track_index not in pre_filtered_track_indice):
            continue

        if ("properties" not in track):
            continue
        properties = track['properties']

        track_flags = get_track_name_flags(track)

        # Validate track's flags against accepted flags.
        if (track_flags in accepted_flags):
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


def test_flag_in_string(value: str, flag: str):
    value_upper = value.upper()

    # define previous accepted characters
    valid_previous_characters = ['\0', ' ', '.', ',', '-', '(', '[']
    valid_next_characters     = ['\0', ' ', '.', ',', '-', ')', ']']

    search_pos = 0
    find_pos = value_upper.find(flag, search_pos)
    while(find_pos != -1):
        prev_char = value_upper[find_pos - 1] if find_pos > 0 else '\0'
        next_char = value_upper[find_pos + len(flag)] if (find_pos + len(flag)) < len(value_upper) else '\0'

        if (prev_char in valid_previous_characters and next_char in valid_next_characters):
            return True

        # search next
        search_pos += 1
        find_pos = value_upper.find(flag, search_pos)

    return False


def get_track_name_flags(track: dict):
    if not "properties" in track:
        return None
    properties = track['properties']
    
    track_name = str(properties['track_name']).upper() if 'track_name' in properties else ""
    track_language_ietf = properties['language_ietf'] if 'language_ietf' in properties else ""

    #has_vff = (track_name.find("VFF") != -1)
    #has_vfq = (track_name.find("VFQ") != -1)
    #has_vfi = (track_name.find("VFI") != -1)
    #has_vo = (track_name.find("VO") != -1)
    #has_vff |= (track_language_ietf == "fr-FR")
    #has_vfq |= (track_language_ietf == "fr-CA")

    has_vff = test_flag_in_string(track_name, "VFF") or (track_language_ietf == "fr-FR")
    has_vfq = test_flag_in_string(track_name, "VFQ") or (track_language_ietf == "fr-CA")
    has_vfi = test_flag_in_string(track_name, "VFI")
    has_vo  = test_flag_in_string(track_name, "VO")

    if ( has_vff ):
      return "VFF"
    if ( has_vfq ):
      return "VFQ"
    if ( has_vfi ):
      return "VFI"
    if ( has_vo ):
      return "VO"

    return None


def get_track_name_flags_from_filename(file_path: str):
    if (test_flag_in_string(file_path, "VF2")):
        return "VF2"
    if (test_flag_in_string(file_path, "VFF")):
        return "VFF"
    if (test_flag_in_string(file_path, "VFQ")):
        return "VFQ"
    if (test_flag_in_string(file_path, "VFI")):
        return "VFI"
    if (test_flag_in_string(file_path, "VO")):
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


def get_container_properties_title(json_obj: dict):
    if not "container" in json_obj:
        return None
    container = json_obj['container']
    
    if not "properties" in container:
        return None
    properties = container['properties']

    title = properties['title'] if "title" in properties else None
    return title
    

def get_track_property_value(json_obj: dict, track_index: int, property_name: str):
    if not "tracks" in json_obj:
        return None
    tracks = json_obj['tracks']

    # Validate track_index
    if (track_index < 0 or track_index >= len(tracks)):
        return None
    track = tracks[track_index]

    # Validate track's properties
    if not "properties" in track:
        return None
    properties = track['properties']

    # Validate specific property name
    if not property_name in properties:
        return None
    value = properties[property_name]

    return value


def set_track_property_value(json_obj: dict, track_index: int, property_name: str, property_value: str):
    if not "tracks" in json_obj:
        return False
    tracks = json_obj['tracks']

    # Validate track_index
    if (track_index < 0 or track_index >= len(tracks)):
        return False
    track = tracks[track_index]

    # Validate track's properties
    if not "properties" in track:
        return False
    properties = track['properties']

    # Set value
    json_obj['tracks'][track_index]['properties'][property_name] = property_value
    return True


def set_track_flag(json_obj: dict, track_index: int, flag_value: str):
    if not "tracks" in json_obj:
        return False
    tracks = json_obj['tracks']

    # Validate track_index
    if (track_index < 0 or track_index >= len(tracks)):
        return False
    track = tracks[track_index]

    # Validate track's properties
    if not "properties" in track:
        return False
    properties = track['properties']
        
    # Force flag in track_name, if not present
    flags_track_name = get_track_name_flags(track)
    if flags_track_name is None:
        # The track does not already have a flag indicator
        new_track_name = get_track_property_value(json_obj, track_index, "track_name")
        if (new_track_name is None):
            new_track_name = ""
        new_track_name += " (" + flag_value + ")"
        set_track_property_value(json_obj, track_index, 'track_name', new_track_name)

    # Update language
    match flag_value:
        case "VFQ":
            set_track_property_value(json_obj, track_index, 'language', 'fre')
            set_track_property_value(json_obj, track_index, 'language_ietf', 'fr-CA')
        case "VFF":
            set_track_property_value(json_obj, track_index, 'language', 'fre')
            set_track_property_value(json_obj, track_index, 'language_ietf', 'fr-FR')
        case "VFI":
            set_track_property_value(json_obj, track_index, 'language', 'fre')
        case _:
            # VF2
            print("Unknown track flag '" + flag_value + "' used in function 'set_track_flag()'.")
            pass


def get_track_supported_property_names():
    property_names = list()
    property_names.append("default_track")
    #property_names.append("display_dimensions")
    property_names.append("enabled_track")
    property_names.append("forced_track")
    property_names.append("language")
    property_names.append("language_ietf")
    property_names.append("pixel_dimensions")
    property_names.append("track_name")
    property_names.append("uid")
    return property_names


def get_mkvpropedit_set_argument_for_mkvmerge_property(name: str):
    # https://mkvtoolnix.download/doc/mkvpropedit.html#mkvpropedit.examples
    # mkvpropedit --list-property-names to get all names
    match name:
        case "default_track":
            return "flag-default"
        case "enabled_track":
            return "flag-enabled"
        case "forced_track":
            return "flag-forced"
        case "language":
            return "language"
        case "language_ietf":
            return "language-ietf"
        case "track_name":
            return "name"

        # If an exact match is not confirmed, this last case will be used if provided
        case _:
            return None
