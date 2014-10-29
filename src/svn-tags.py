#!/usr/bin/python

#
# svn-tags assumes that we are using the recommended svn repo layout:
#
#	my-repo/
#	|_ .svn/
#	|_ branches/
#	|_ tags/
#	|_ trunk/
#
# NOTE: Otherwise this tool will not work correctly.
#

import os
import subprocess
import re
from colorama import Fore
from exceptions import Exception


def main():
	found, svn_base_dir = find_svn_base_dir()
	if not found:
		on_failed_to_find_svn_repo()

	tags_dir = find_tags_dir(svn_base_dir)
	tags = find_tags(tags_dir)

	print_tags(tags)


def print_tags(tags):
	print "Tags:"
	for t in tags:
		print "\t" + t


def find_tags(tags_dir):
	output = subprocess.check_output(["svn", "list", tags_dir])
	tags = output.split("\n")
	tags.remove("")

	for i in range(0, len(tags)):
		tags[i] = tags[i][:-1]

	return tags


def find_tags_dir(svn_base_dir):
	tags_dir = "tags"
	files = os.listdir(svn_base_dir)
	if not tags_dir in files:
		raise Exception("SVN base dir does not have 'tags' dir.")

	return os.path.join(svn_base_dir, tags_dir)


def on_failed_to_find_svn_repo():
	print Fore.RED + "This directory is not part of svn repository." \
		+ Fore.RESET
	exit(1)


def find_svn_base_dir():
	cur_dir = os.getcwd()
	files = os.listdir(cur_dir)

	while keep_looking_for_svn_dir(files, cur_dir):
		os.chdir("..")
		cur_dir = os.getcwd()
		files = os.listdir(cur_dir)

	return has_svn_dir(files), cur_dir


def keep_looking_for_svn_dir(files, cur_dir):
	return (not has_svn_dir(files)) and (not is_base_path(os.getcwd()))


def has_svn_dir(files_dirs):
	return ".svn" in files_dirs


def is_base_path(path):
	return path == "/"


main()
