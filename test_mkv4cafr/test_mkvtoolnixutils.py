import pytest
import os
from mkv4cafr import mkvtoolnixutils


def test_mkvtoolnix_exists():
    mkvtoolnix_install_path = mkvtoolnixutils.setup_mkvtoolnix()
    assert (mkvtoolnix_install_path != None)
