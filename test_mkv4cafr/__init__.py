import sys
import os

# Add the project root directory as a search path for packages.
# This forces all import statements to use the syntax `from mkv4cafr import xyz`.
file_dir_path = os.path.dirname(os.path.abspath(__file__))
project_root_dir_path = os.path.dirname(file_dir_path)
sys.path.append(project_root_dir_path)
