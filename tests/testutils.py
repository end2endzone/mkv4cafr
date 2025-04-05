import os
import subprocess


def get_project_root_dir_path():
    tests_directory_path = os.path.dirname(os.path.abspath(__file__))
    project_root_dir_path = os.path.dirname(tests_directory_path)
    return project_root_dir_path


def get_medias_dir_path():
    dir_path = get_project_root_dir_path()
    if (dir_path is None):
        return None
    dir_path = os.path.join(dir_path,"medias")
    return dir_path


def get_test_files_dir_path():
    dir_path = get_project_root_dir_path()
    if (dir_path is None):
        return None
    dir_path = os.path.join(dir_path,"tests")
    dir_path = os.path.join(dir_path,"test_files")
    return dir_path


def get_test_output_dir_path():
    dir_path = get_project_root_dir_path()
    if (dir_path is None):
        return None
    dir_path = os.path.join(dir_path,"tests")
    dir_path = os.path.join(dir_path,"output")
    return dir_path


def run_mkv4cafr(additional_args: list):
    # Builds args for starting mkv4cafr
    args = list()
    args.append("python")
    args.append("-m")
    args.append("mkv4cafr.mkv4cafr")

    if (additional_args != None):
        args.extend(additional_args)

    cwd = get_project_root_dir_path()
    output_str = None

    try:
        output_bytes = subprocess.check_output(args, cwd=cwd, shell=True)
        output_str = output_bytes.decode("utf-8")
    except subprocess.CalledProcessError as p:
        output_str = p.output.decode("utf-8")

        err_desc = str()
        err_desc += "Failed to execute command:\n"
        err_desc += " ".join(args)
        err_desc += "\n"
        err_desc += "Return code: {0}\n".format(p.returncode)
        err_desc += "Program output:\n"
        err_desc += output_str
        err_desc += "\n"

        #raise Exception(err_desc)
        print(err_desc)
        return p.returncode
    return 0
