# Any commands which fail will cause the shell script to exit immediately
set -e

# Install mkvtoolnix.

# Installing mkvtoolnix.
echo Proceeding with instaling mkvtoolnix...
sudo apt update

# Installing mkvtoolnix via apt will install version v65.0.0 ('Too Much') 64-bit. 
# This version is too old and do not contains the required features for mkv4cafr.
#sudo apt install -y mkvtoolnix
#echo

# Installing via AppImage as per instructions on https://mkvtoolnix.download/downloads.html#appimage
export MKVTOOLNIX_DOWNLOAD_VERSION=91.0
echo "Downloading MKVToolNix_GUI-$MKVTOOLNIX_DOWNLOAD_VERSION-x86_64.AppImage"
curl -o /tmp/MKVToolNix_GUI-$MKVTOOLNIX_DOWNLOAD_VERSION-x86_64.AppImage https://mkvtoolnix.download/appimage/MKVToolNix_GUI-$MKVTOOLNIX_DOWNLOAD_VERSION-x86_64.AppImage
chmod u+rx /tmp/MKVToolNix_GUI-$MKVTOOLNIX_DOWNLOAD_VERSION-x86_64.AppImage
echo done.
echo

# According to documentation, creating a symlink would allow to run the executables inside the image but that does not look like that.
#chmod u+rx /tmp/MKVToolNix_GUI-$MKVTOOLNIX_DOWNLOAD_VERSION-x86_64.AppImage
#ln -s /tmp/MKVToolNix_GUI-$MKVTOOLNIX_DOWNLOAD_VERSION-x86_64.AppImage mkvpropedit
#ln -s /tmp/MKVToolNix_GUI-$MKVTOOLNIX_DOWNLOAD_VERSION-x86_64.AppImage mkvmerge
#sudo apt install libegl1 libice6 libsm6
#./mkvmerge @medias/test01.json
#
#results in the following error:
#```
#Qt depends on a UTF-8 locale, and has switched to "C.UTF-8" instead.
#If this causes problems, reconfigure your locale. See the locale(1) manual
#for more information.
#qt.qpa.xcb: could not connect to display
#qt.qpa.plugin: From 6.5.0, xcb-cursor0 or libxcb-cursor0 is needed to load the Qt xcb platform plugin.
#qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
#This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.
#```

echo "Extracting the content of the image..."
export MKVTOOLNIX_APP_DIR=/tmp/mkvtoolnix
pushd /tmp && /tmp/MKVToolNix_GUI-$MKVTOOLNIX_DOWNLOAD_VERSION-x86_64.AppImage --appimage-extract && mv /tmp/squashfs-root $MKVTOOLNIX_APP_DIR && popd
echo done.
echo

echo "Setting file exec permissions..."
chmod u+rx $MKVTOOLNIX_APP_DIR/usr/bin/mkvmerge
chmod u+rx $MKVTOOLNIX_APP_DIR/usr/bin/mkvpropedit
sudo ln -s $MKVTOOLNIX_APP_DIR/usr/bin/mkvmerge    /usr/bin/mkvmerge
sudo ln -s $MKVTOOLNIX_APP_DIR/usr/bin/mkvpropedit /usr/bin/mkvpropedit
echo done.
echo

# Add $MKVTOOLNIX_APP_DIR/usr/lib as a shared libraries directory
# https://unix.stackexchange.com/questions/425251/using-ldconfig-and-ld-so-conf-versus-ld-library-path
#echo "$MKVTOOLNIX_APP_DIR/usr/lib">/etc/ld.so.conf.d/mkvtoolnix.conf
echo "Adding directory \'$MKVTOOLNIX_APP_DIR/usr/lib\' as a shared library source directory..."
echo "$MKVTOOLNIX_APP_DIR/usr/lib" | sudo tee --append /etc/ld.so.conf.d/x86_64-linux-gnu.conf
echo done.
echo "Updaing system with ldconfig..."
sudo ldconfig
echo done.
echo

echo mkvtoolnix was installed on the system:
mkvmerge --version
mkvpropedit --version

echo
