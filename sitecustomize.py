import coverage
import os

# Enable multiprocess code coverage support.
# This program is launched by unit tests. To properly compute coverage of this process,
# the environment variable 'COVERAGE_PROCESS_START' must be set to the path of the project's `.coveragerc` file.
# If set, we should start the coverage module to compute the coverage of this specific process.
# https://stackoverflow.com/questions/78181708/coverage-of-process-spawned-by-pytest
# https://coverage.readthedocs.io/en/latest/subprocess.html#implicit-coverage
#
# Bash:
#   export COVERAGE_PROCESS_START=$PWD/.coveragerc
# Powershell:
#   $env:COVERAGE_PROCESS_START = (Join-Path (Get-Location) -ChildPath ".coveragerc")
#
do_start_coverage = os.environ['COVERAGE_PROCESS_START'] if 'COVERAGE_PROCESS_START' in os.environ else None
if (do_start_coverage != None):
    coverage.process_startup()
