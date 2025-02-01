import os
import shutil

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
