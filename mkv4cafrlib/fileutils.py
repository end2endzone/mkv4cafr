import os
import io
import time
import shutil
import argparse
import sys

# https://stackoverflow.com/questions/56762491/python-equivalent-to-c-line
def LINE():
    return sys._getframe(1).f_lineno


def get_file_separator():
    if os.name == 'nt' or os.name == 'win32':
        return "\\"
    else:
        return "/"


def get_copy_file_to_directory_target(input_path: str, output_dir: str):
    input_dir, input_file_name = os.path.split(input_path)
    output_file_path_relative = os.path.join(output_dir, input_file_name)
    output_file_path_abs = os.path.abspath(output_file_path_relative)
    return output_file_path_abs


def copy_file(input_path: str, output_path: str):
    # https://docs.python.org/3/library/shutil.html#shutil.copy2
    try:
        shutil.copy2(input_path, output_path)
    except shutil.Error as err:
        print(err)
        return False
    return True


def get_progress_bar_string(actual: int, total: int, max_length: int):
    fill_length = int(actual/total*max_length)
    remaining_length = max_length - fill_length
    output = '>'*fill_length + '-'*remaining_length
    return output


def get_spinning_cursor():
    DIGIT_DISPLAY_TIME_MS = 75
    DIGITS = "-\\|/"
    elapsed_time_ms = int(time.time() * 1000)
    digit_index = int(elapsed_time_ms / DIGIT_DISPLAY_TIME_MS) % len(DIGITS)
    return DIGITS[digit_index]


def print_progress_bar(actual: int, total: int):
    # Example:
    # - [>>>>>>>>>>] 100%
    
    percent = int(actual/total*100.0)
    
    # https://stackoverflow.com/questions/61836508/getting-oserror-winerror-6-the-handle-is-invalid-while-working-on-os-module
    # Do not use `os.get_terminal_size().columns` to get terminal size.
    # The function may raise the following exception:
    # `[WinError 6] The handle is invalid` when running on Windows.
    MAX_BAR_LENGTH = shutil.get_terminal_size().columns - 1 # -1 to leave space for the cursor position 1 character after the text
    MINIMUM_BAR_LENGTH = len("- [] 100% ")
    INDENT = 1
    progress_width = MAX_BAR_LENGTH - MINIMUM_BAR_LENGTH - INDENT
    if (progress_width < 10):
        progress_width = 10

    spinner = get_spinning_cursor()
    bar = spinner + ' '*INDENT + '[' + get_progress_bar_string(actual, total, progress_width) + "] " + format(percent, "3d") + "% "
    print("\r" + bar, end="", flush=True)

    return len(bar)


def copy_file_with_progress(input_path: str, output_path: str):
    try:
        bar_lenght = 0
        chunk_size = 10*1024*1024 # 10Mb chunk size
        input_size = os.path.getsize(input_path)
        output_size = 0
        with open(input_path, 'rb') as fin:
            with open(output_path, 'wb') as fout:

                # read a chunk of the input file
                data = fin.read(chunk_size)

                while (len(data) > 0):
                    # write this chunk to the output file
                    fout.write(data)
                    output_size += len(data)

                    # and update the progress on screen
                    bar_lenght = print_progress_bar(output_size, input_size)

                    # read the next chunk
                    data = fin.read(chunk_size)

    except shutil.Error as err:
        print("") # new line. go 1 line below the progress bar
        print(err)
        return False
    except Exception as e:
        err_desc = str(e)
        print(err_desc)
        return False
        
    # Erase copying bar
    print("\r" + ' '*bar_lenght + "\r", end="", flush=True)

    return True


def get_str_path_or_empty_str(obj):
    debug = str(type(obj))
    output = ""
    if (isinstance(obj, str)):
        output = obj
    elif (isinstance(obj, io.BufferedReader)):
        output = str(obj.name)
    elif (isinstance(obj, io.TextIOBase)):
        output = str(obj)
    elif (isinstance(obj, argparse.FileType)):
        output = str(obj.name)
    return output


def get_str_path_or_none(obj):
    debug = type(obj)
    output = None
    if (isinstance(obj, str)):
        output = obj
    elif (isinstance(obj, io.BufferedReader)):
        output = str(obj.name)
    elif (isinstance(obj, io.TextIOBase)):
        output = str(obj)
    elif (isinstance(obj, argparse.FileType)):
        output = str(obj.name)
    return output
