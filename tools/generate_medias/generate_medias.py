import os
import sys
import subprocess

from mkv4cafrlib import findutils
from mkv4cafrlib import ffmpegutils
from mkv4cafrlib import mkvtoolnixutils

# Constants
# N/A


def format_timecode(time_abs_seconds):
    remaining = time_abs_seconds
    
    hours = int(remaining / 3600)
    remaining -= (hours * 3600)

    minutes = int(remaining / 60)
    remaining -= (minutes * 60)
    
    seconds = int(remaining)
    remaining -= seconds

    milliseconds = int(remaining * 1000)

    time_str = "{:02d}:{:02d}:{:02d},{:03d}".format(hours, minutes, seconds, milliseconds)
    return time_str


def generate_subtitle_timecodes_detailed(framerate: int, video_length_seconds: int, subtitles_count: int):
    # Compute details
    interval_seconds = video_length_seconds / subtitles_count

    # Create subtitles
    #
    # Format details:
    #   5
    #   00:00:20,000 --> 00:00:20,999
    #   20
    #   
    #   6
    #   00:00:25,000 --> 00:00:25,999
    #   25
    #   
    with open("medias/timecodes detailed.srt", "w") as text_file:
        for i in range(subtitles_count):
            sub_start_time = i * interval_seconds
            sub_stop_time = (i+1) * interval_seconds - 0.001
            frame_number = int(sub_start_time * framerate)
            
            text_file.write (str(i+1) + "\n")
            text_file.write("{0} --> {1}\n".format(format_timecode(sub_start_time), format_timecode(sub_stop_time)))
            text_file.write(str(frame_number) + "\n")
            text_file.write("\n")


def generate_life_h264():
    try:
        filter = ""
        filter = filter + "ratio=0.7:"
        filter = filter + "s=320x240:"
        filter = filter + "rate=24,"
        filter = filter + "edgedetect"
        #filter = filter + ",negate"
        #filter = filter + ",fade=in:0:100"

        # ffmpeg -y -f lavfi -i "life=%FILTER%" -t 60 -pix_fmt yuv420p     -c:v libx264 -preset slow -crf 0 life-h264.mp4
        command_args=[]
        command_args.append("ffmpeg")
        command_args.append("-y")
        command_args.append("-hide_banner")
        command_args.append("-f")
        command_args.append("lavfi")
        command_args.append("-i")
        command_args.append("life="+filter)
        command_args.append("-t")
        command_args.append("60")
        command_args.append("-pix_fmt")
        command_args.append("yuv420p")
        command_args.append("-c:v")
        command_args.append("libx264")
        command_args.append("-preset")
        command_args.append("slow")
        command_args.append("-crf")
        command_args.append("0")
        command_args.append("medias/life-h264.mp4")
        subprocess.check_call(command_args)
    except subprocess.CalledProcessError as procexc:                                                                                                   
        print("Failed to execute ffmpeg '", " ".join(command_args), "'. Error code: ", procexc.returncode, procexc.output)
        sys.exit(2)
    print("done.")
    print("")
    print("")


def generate_life_h265():
    try:
        filter = ""
        filter = filter + "ratio=0.7:"
        filter = filter + "s=320x240:"
        filter = filter + "rate=24,"
        filter = filter + "edgedetect"
        #filter = filter + ",negate"
        #filter = filter + ",fade=in:0:100"

        # ffmpeg -y -f lavfi -i "life=%FILTER%" -t 60 -pix_fmt yuv420p10le -c:v libx265 -x265-params "aq-mode=0:repeat-headers=0:strong-intra-smoothing=1:bframes=4:b-adapt=2:frame-threads=0:hdr10_opt=0:hdr10=0:chromaloc=0" -preset slow -crf 0 life-h265.mp4
        command_args=[]
        command_args.append("ffmpeg")
        command_args.append("-y")
        command_args.append("-hide_banner")
        command_args.append("-f")
        command_args.append("lavfi")
        command_args.append("-i")
        command_args.append("life="+filter)
        command_args.append("-t")
        command_args.append("60")
        command_args.append("-pix_fmt")
        command_args.append("yuv420p10le")
        command_args.append("-c:v")
        command_args.append("libx265")
        command_args.append("-x265-params")
        command_args.append("aq-mode=0:repeat-headers=0:strong-intra-smoothing=1:bframes=4:b-adapt=2:frame-threads=0:hdr10_opt=0:hdr10=0:chromaloc=0")
        command_args.append("-preset")
        command_args.append("slow")
        command_args.append("-crf")
        command_args.append("0")
        command_args.append("medias/life-h265.mp4")
        subprocess.check_call(command_args)
    except subprocess.CalledProcessError as procexc:                                                                                                   
        print("Failed to execute ffmpeg '", " ".join(command_args), "'. Error code: ", procexc.returncode, procexc.output)
        sys.exit(2)
    print("done.")
    print("")
    print("")


def generate_testsrc2():
    try:
        filter = ""
        filter = filter + "testsrc2=s=1280x720:rate=24:d=60"
        filter = filter + ",scale='-1:min(ih,1080)'"
        filter = filter + ",pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
        filter = filter + ",setsar=1"
        filter = filter + ",format=yuv420p"
        filter = filter + "[v]"

        # ffmpeg -y -filter_complex "%FILTER%" -map "[v]" -an -c:v libx264 -preset slow -crf 30 testsrc2.mp4
        command_args=[]
        command_args.append("ffmpeg")
        command_args.append("-y")
        command_args.append("-hide_banner")
        command_args.append("-filter_complex")
        command_args.append(filter)
        command_args.append("-map")
        command_args.append("[v]")
        command_args.append("-an")
        command_args.append("-c:v")
        command_args.append("libx264")
        command_args.append("-preset")
        command_args.append("slow")
        command_args.append("-crf")
        command_args.append("30")
        command_args.append("medias/testsrc2.mp4")
        subprocess.check_call(command_args)
    except subprocess.CalledProcessError as procexc:                                                                                                   
        print("Failed to execute ffmpeg '", " ".join(command_args), "'. Error code: ", procexc.returncode, procexc.output)
        sys.exit(2)
    print("done.")
    print("")
    print("")


def get_anullsrc_filter(channel_layout: str, sample_rate: int):
    filter = "anullsrc=channel_layout={channel_layout}}:sample_rate={sample_rate}".format(channel_layout=channel_layout, sample_rate=sample_rate)
    return filter
def generate_audio_tracks():
    try:
        commands = list()
        commands.append("ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=stereo:sample_rate=44100                      -vn -c:a pcm_s16le            medias/audio_silence_44khz.wav")
        commands.append("ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=mono:sample_rate=44100                        -vn -c:a ac3 -b:a  96k        medias/audio_1ch_192kbps.ac3")
        commands.append("ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=stereo:sample_rate=48000                      -vn -c:a mp3 -b:a 128k        medias/audio_2ch_128kbps.mp3")
        commands.append("ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=stereo:sample_rate=48000                      -vn -c:a ac3 -b:a 192k        medias/audio_2ch_192kbps.ac3")
        commands.append("ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=stereo:sample_rate=48000                      -vn -c:a aac -b:a 192k        medias/audio_2ch_192kbps.aac")
        commands.append("ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=5.1(side):sample_rate=44100 -strict -2        -vn -c:a dca -b:a 1510k       medias/audio_6ch_1510kbps.dts")
        commands.append("ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=5.1:sample_rate=48000                         -vn -c:a ac3 -b:a 640k        medias/audio_6ch_640kbps.ac3")
        commands.append("ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=5.1:sample_rate=48000                         -vn -c:a eac3 -b:a 1152k      medias/audio_6ch_1152kbps.eac3")
        commands.append("ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=5.1:sample_rate=48000                         -vn -c:a libopus -b:a 1536k   medias/audio_6ch_1536kbps.opus")
        commands.append("ffmpeg -y -hide_banner -f lavfi -t 60 -i sine=frequency=100:duration=60:sample_rate=96000 -ac 6 -strict -2     -vn -c:a truehd               medias/audio_6ch_96kHz.thd")
        commands.append("ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=5.1:sample_rate=192000 -strict -2             -vn -c:a truehd               medias/audio_6ch_192kHz.thd")
        commands.append("ffmpeg -y -hide_banner -f lavfi -t 60 -i anullsrc=channel_layout=5.1:sample_rate=48000                         -vn -c:a libvorbis -b:a 1440k medias/audio_6ch_1440kbps.ogg")
        commands.append("ffmpeg -y -hide_banner -f lavfi -t 60 -i sine=frequency=100:duration=60:sample_rate=48000 -ac 8                -vn -c:a flac                 medias/audio_8ch.flac")

        for command in commands:
            command = str(command)
            while(command.find("  ") != -1):
                command = command.replace("  ", " ")
            command_args = str(command).split(' ')
            subprocess.check_call(command_args)
    except subprocess.CalledProcessError as procexc:                                                                                                   
        print("Failed to execute ffmpeg command: '", command, "'. Error code: ", procexc.returncode, procexc.output)
        sys.exit(2)
    print("done.")
    print("")
    print("")


def generate_mkv_files():
    try:
        commands = list()
        commands.append("mkvmerge @medias/test01.json")
        commands.append("mkvmerge @medias/test02.json")
        commands.append("mkvmerge @medias/test_get_track_name_flags.json")
        commands.append("mkvmerge @medias/test_get_track_auto_generated_name.json")
        commands.append("mkvmerge @medias/test_get_track_id_from_index.json")
        for command in commands:
            command = str(command)
            while(command.find("  ") != -1):
                command = command.replace("  ", " ")
            command_args = str(command).split(' ')
            subprocess.check_call(command_args)
    except subprocess.CalledProcessError as procexc:                                                                                                   
        print("Failed to execute MKVToolNix command: '", command, "'. Error code: ", procexc.returncode, procexc.output)
        sys.exit(2)
    print("done.")
    print("")
    print("")


def main():
    # Find ffmpeg in path
    ffmpeg_exec_path = ffmpegutils.find_ffmpeg_exec_path_in_path()
    if ffmpeg_exec_path is None or not os.path.isfile(ffmpeg_exec_path):
        print("ffmpeg not found in PATH\n")
        sys.exit(1)

    # Find mkvmerge on system
    mkvtoolnix_install_path = mkvtoolnixutils.find_mkvtoolnix_dir_in_path()
    if mkvtoolnix_install_path is None or not os.path.isdir(mkvtoolnix_install_path):
        print("MKVToolNix not found in PATH.\n")

        print("Searching known installation directories...")
        mkvtoolnix_install_path = mkvtoolnixutils.find_mkvtoolnix_dir_on_system()
        if mkvtoolnix_install_path is None or not os.path.isdir(mkvtoolnix_install_path):
            print("MKVToolNix not found on system.\n")
            sys.exit(1)

        # Found, but not in PATH
        os.environ['PATH'] = mkvtoolnix_install_path + os.pathsep + os.environ['PATH']
    mkvmerge_exec_path    = os.path.join(mkvtoolnix_install_path, "mkvmerge"    + findutils.get_executable_file_extension_name())
    mkvpropedit_exec_path = os.path.join(mkvtoolnix_install_path, "mkvpropedit" + findutils.get_executable_file_extension_name())


    # Generate subtitles
    framerate = 24
    subtitles_count = 180
    video_length_seconds = 60
    generate_subtitle_timecodes_detailed(framerate, video_length_seconds, subtitles_count)

    # Generate video files
    generate_life_h264()
    generate_life_h265()
    generate_testsrc2()

    # Generate audio files
    generate_audio_tracks()

    # Generate mkv files
    generate_mkv_files()


if __name__ == "__main__":
    main()
