#
# This module has utility functions related to svn repo manipulation.
#

import os
from exceptions import Exception

#
# Returns svn repository root path.
# Throws exception if current directory is not within svn repository.
#
def find_svn_root_path():
	cur_dir = os.getcwd()
	files = os.listdir(cur_dir)

	while keep_looking_for_svn_dir(files, cur_dir):
		os.chdir("..")
		cur_dir = os.getcwd()
		files = os.listdir(cur_dir)

	if not has_svn_dir(files):
		raise Exception("This directory is not part of svn repository.")

	return cur_dir


def keep_looking_for_svn_dir(files, cur_dir):
	return (not has_svn_dir(files)) and (not is_base_path(os.getcwd()))


def has_svn_dir(files_dirs):
	return ".svn" in files_dirs


def is_base_path(path):
	return path == "/"
