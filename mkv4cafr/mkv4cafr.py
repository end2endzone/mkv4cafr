import argparse
import os
import sys
import getpass
import subprocess
import json
import copy
import glob
import signal
import coverage

from mkv4cafrlib import mkv4cafrlib
from mkv4cafrlib import findutils
from mkv4cafrlib import fileutils
from mkv4cafrlib import mkvtoolnixutils
from mkv4cafrlib import mkvmergeutils
from mkv4cafrlib import jsonutils

# Constants
MAX_SUBTITLES_PER_HOUR_RATIO = 75.0


# Register a signal handler to properly exit the application.
# Required to properly compute code coverage
# https://stackoverflow.com/questions/77135323/python-coverage-when-using-subprocess-wont-work
def signal_handler(number, frame):
    sys.exit(0)
signal.signal(signal.SIGTERM, signal_handler)


def print_header():
    print("mkv4cafr v0.2.0")


# Parse output directory
# See https://gist.github.com/harrisont/ecb340616ab6f7cf11f99364fd57ef7e
def directory_must_exist(raw_path):
    if not os.path.isdir(raw_path):
        raise argparse.ArgumentTypeError('"{}" is not an existing directory'.format(raw_path))
    return os.path.abspath(raw_path)


def directory_must_exist_if_specified(raw_path):
    if (raw_path is None):
        return ""
    if not os.path.isdir(raw_path):
        raise argparse.ArgumentTypeError('"{}" is not an existing directory'.format(raw_path))
    return os.path.abspath(raw_path)


def main() -> int:
    print_header()

    # Parse command line arguments
    # See https://stackoverflow.com/questions/20063/whats-the-best-way-to-parse-command-line-arguments for example.
    parser = argparse.ArgumentParser(description='mkv4cafr sets properties of mkv files for Canadian French viewers')

    parser.add_argument('-f', '--input-file', type=argparse.FileType('rb'), help='input mkv file')
    parser.add_argument('-d', '--input-dir', action='store', type=str, help='input mkv directory', default=None)
    parser.add_argument('-o', '--output-dir', type=directory_must_exist_if_specified, default=os.path.curdir, help='output directory')
    parser.add_argument('-e', '--edit-in-place', action='store_true', help='Process input file in place', default=False)

    try:
        args = parser.parse_args()
    except Exception as e:
        print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")    

    print("Argument values:")
    print("  input file: " + fileutils.get_str_path_or_empty_str(args.input_file) )
    print("  input directory: " + fileutils.get_str_path_or_empty_str(args.input_dir))
    print("  output directory: " + fileutils.get_str_path_or_empty_str(args.output_dir))
    print("  edit-in-place: " + str(args.edit_in_place))

    # Valide input arguments
    if (fileutils.get_str_path_or_none(args.input_dir) != None and fileutils.get_str_path_or_none(args.input_file) != None):
        print("<input file> and <input directory> are mutually exclusive.")
        return 1
    if (fileutils.get_str_path_or_none(args.input_dir) == None and fileutils.get_str_path_or_none(args.input_file) == None):
        print("Must specify <input file> or <input directory>.")
        return 1
    if (not args.edit_in_place and fileutils.get_str_path_or_none(args.output_dir) == None):
        print("Must specify <output directory> if not editing in-place.")
        return 1

    # Search for mkvpropedit on the system    
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    if (mkvtoolnix_install_path is None):
        sys.exit(1)
    mkvmerge_exec_path    = os.path.join(mkvtoolnix_install_path, "mkvmerge"    + findutils.get_executable_file_extension_name())
    mkvpropedit_exec_path = os.path.join(mkvtoolnix_install_path, "mkvpropedit" + findutils.get_executable_file_extension_name())
    print("Found mkvpropedit: " + mkvpropedit_exec_path)

    # If we run in input directory mode
    if (fileutils.get_str_path_or_none(args.input_dir) != None):
        # Validate if directory exists
        input_dir_abspath = os.path.abspath(fileutils.get_str_path_or_empty_str(args.input_dir))
        if not os.path.isdir(input_dir_abspath):
            print("Directory '" + input_dir_abspath + "' not found.")
            return 1

        # Find all *.mkv files
        mkv_files = []
        for mkv_file in glob.glob(glob.escape(input_dir_abspath) + "/*.mkv"):
            mkv_files.append(mkv_file)

        print("Processing " + str(len(mkv_files)) + " mkv files from input directory '" + input_dir_abspath + "'.")
        for i in range(len(mkv_files)):
            mkv_file_path = mkv_files[i]
            print("Processing file " + str(i+1) + " of " + str(len(mkv_files)) + ": '" + mkv_file_path + "'.")
            exit_code = process_file(mkv_file_path, str(args.output_dir), args.edit_in_place)
            if (exit_code != 0):
                print("Failed processing file " + str(i+1) + " of " + str(len(mkv_files)) + ": '" + mkv_file_path + "'!")
                return exit_code
            
        print("done.")
        return 0
    
    # or we run in input file mode
    elif (fileutils.get_str_path_or_none(args.input_file) != None):
        exit_code = process_file(fileutils.get_str_path_or_empty_str(args.input_file), str(args.output_dir), args.edit_in_place)
        if (exit_code != 0):
            print("Failed processing file '" + fileutils.get_str_path_or_empty_str(args.input_file) + "'!")
        else:
            print("done.")
        return exit_code
    else:
        print("Nothing to do!")
        return 1


def indent_string(value: str, indent: int):
    lines = value.split("\n")
    for i in range(len(lines)):
        lines[i] = (' '*indent) + lines[i]
    output = '\n'.join(lines)
    return output


def process_file(input_file_path: str, output_dir_path: str, edit_in_place: bool) -> int:

    # Validate if file exists
    input_abspath = os.path.abspath(input_file_path)
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
        return 1

    # Update
    json_copy = mkv4cafrlib.update_properties_as_per_preferences(json_obj, input_abspath)

    # Validate inconsistencies
    has_inconsistencies = mkv4cafrlib.validate_inconsistencies(json_copy, input_abspath)
    if (has_inconsistencies == False or has_inconsistencies is None):
        print("Inconsistencies were found during metadata validation for file '" + input_abspath + "'.")
        print("Aborting update.")
        return 1

    # DEBUG:
    #json_copy['tracks'][1] = json_obj['tracks'][1]
    #json_copy['tracks'][2] = json_obj['tracks'][2]
    #json_copy['tracks'][3] = json_obj['tracks'][3]
    #json_copy['tracks'][4] = json_obj['tracks'][4]

    # Save metadata for debugging, if possible.
    # Only required if you edit in place.
    if (edit_in_place):
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
    json_diff = mkv4cafrlib.compute_json_differences(json_obj, json_copy)

    has_diff = bool(json_diff)
    if (not has_diff):
        print("No modification required in input file metadata.")
        return 0
    
    print("Input file requires the following changes in metadata:")
    #diff_str = json.dumps(json_diff, indent=2)
    diff_str = jsonutils.dump_details(json_diff)
    diff_str = indent_string(diff_str, 2)
    print(diff_str)

    # Set the target file to edit if we do not edit-in-place
    target_file = input_abspath
    if (not edit_in_place):
        print("Copying input file to output directory...")
        target_file = fileutils.get_copy_file_to_directory_target(input_abspath, output_dir_path)
        success = fileutils.copy_file_with_progress(input_abspath, target_file)
        if (not success):
            print("Failed to copy file '" + target_file + "' to directory.")
            return 1
        print("Copy completed.")
    input_abspath = "" # Make sure the rest of the code do not use the input file as reference

    # Change the target file to be modified

    # Build edit-in-place command    
    mkvpropedit_args = mkv4cafrlib.get_mkvpropedit_args_for_diff(json_diff, target_file)
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
    return 0


if __name__ == "__main__":
    # Enable multiprocess code coverage support.
    # This program is launched by unit tests. To properly compute coverage of this process,
    # the environment variable 'COVERAGE_PROCESS_START' must be set to the path of the project's `.coveragerc` file.
    # If set, we should start the coverage module to compute the coverage of this specific process.
    # https://stackoverflow.com/questions/78181708/coverage-of-process-spawned-by-pytest
    # https://coverage.readthedocs.io/en/latest/subprocess.html#implicit-coverage
    do_start_coverage = os.environ['COVERAGE_PROCESS_START'] if 'COVERAGE_PROCESS_START' in os.environ else None
    if (do_start_coverage != None):
        coverage.process_startup()

    exit_code = main()
    sys.exit(exit_code)
