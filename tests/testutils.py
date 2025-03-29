import os


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
