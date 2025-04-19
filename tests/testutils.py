import os
import subprocess
import coverage


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


def run_mkv4cafr(additional_args: list) -> dict:
    # Output values
    output = dict()

    # Builds args for starting mkv4cafr
    args = list()

    # subprocess python module will finds the python executable fron PATH environment variable.
    args.append("python")
    args.append("-m")
    args.append("mkv4cafr.mkv4cafr")

    if (additional_args != None):
        args.extend(additional_args)

    cwd = get_project_root_dir_path()

    # We are specifying the exec and its arguments as a list or an array
    # We do not have to invoke the shell to parse our command.
    is_shell=False

    # initialize return values
    output['command'] = " ".join(args)
    output['exit_code'] = 0
    output['stdout'] = ""

    try:
        output_bytes = subprocess.check_output(args, cwd=cwd, shell=is_shell, stderr=subprocess.STDOUT)
        output['stdout'] = output_bytes.decode("utf-8")
    except subprocess.CalledProcessError as p:
        output['stdout'] = p.output.decode("utf-8")
        output['exit_code'] = p.returncode
    except Exception as e:
        output['stdout'] = str(e)
        output['exit_code'] = 1 # use this exit code but the output will be meaningful as an exception
    return output


def run_mkv4cafr_env(additional_args: list, env: list) -> dict:
    # Output values
    output = dict()

    # Builds args for starting mkv4cafr
    args = list()

    # subprocess python module will finds the python executable fron PATH environment variable.
    args.append("python")
    args.append("-m")
    args.append("mkv4cafr.mkv4cafr")

    if (additional_args != None):
        args.extend(additional_args)

    cwd = get_project_root_dir_path()

    # We are specifying the exec and its arguments as a list or an array
    # We do not have to invoke the shell to parse our command.
    is_shell=False

    # initialize return values
    output['command'] = " ".join(args)
    output['exit_code'] = 0
    output['stdout'] = ""

    try:
        output_bytes = subprocess.check_output(args, cwd=cwd, shell=is_shell, stderr=subprocess.STDOUT, env=env)
        output['stdout'] = output_bytes.decode("utf-8")
    except subprocess.CalledProcessError as p:
        output['stdout'] = p.output.decode("utf-8")
        output['exit_code'] = p.returncode
    except Exception as e:
        output['stdout'] = str(e)
        output['exit_code'] = 1 # use this exit code but the output will be meaningful as an exception
    return output


def print_mkv4cafr_call_result(result: dict):
    err_desc = ""
    err_desc += "Failed to execute command:\n"
    err_desc += result['command']
    err_desc += "\n"
    err_desc += "Return code: {0}\n".format(result['exit_code'])
    err_desc += "Program output:\n"
    err_desc += result['stdout']
    err_desc += "\n"
    print(err_desc)

