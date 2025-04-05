# Any commands which fail will cause the shell script to exit immediately
set -e

# Install mkvtoolnix.

# Installing mkvtoolnix.
echo Proceeding with instaling mkvtoolnix...
sudo apt update
sudo apt install -y mkvtoolnix
echo

echo mkvtoolnix was installed on the system without error.
echo
