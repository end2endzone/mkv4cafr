# Any commands which fail will cause the shell script to exit immediately
set -e

# Install ffmpeg.

# Installing ffmpeg.
echo Proceeding with instaling ffmpeg...
sudo apt update
sudo apt install -y ffmpeg
echo

echo ffmpeg was installed on the system without error.
echo
