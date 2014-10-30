#!/usr/bin/python

import os
import sys
import subprocess
from optparse import OptionParser

import svn_utils
import console_utils


def main():
	if len(sys.argv) > 1:
		svn_flow = SvnFlow()

		cmd = sys.argv[1]
		if cmd == "init":
			svn_flow.init()

		else:
			console_utils.print_error("Unknown command: " + cmd)
	else:
		print "Usage:"
		print ("\tsvn-flow init - initializes svn repository to work "
			"with svn-flow.")


def log(msg):
	print msg


class Svn:
	def __init__(self, svn_root_path):
		self.root_path = svn_root_path

	#
	# The specified directory path is relative to svn repository root path.
	# E.g. to create trunk directory simply execute
	#	svn.mkdir("trunk")
	#
	def mkdir(self, relative_dir_path):
		full_path = os.path.join(self.root_path, relative_dir_path)
		subprocess.call(["svn", "mkdir", full_path])

	def commit(self, msg):
		subprocess.call(["svn", "commit", "-m", msg])

	#
	# The specified directory paths are relative to svn repository root path.
	# E.g. to create development branch directory simply execute
	#	svn.branch("trunk", "branches/develop")
	#
	def branch(self, src_dir, target_dir):
		src_dir = os.path.join(self.root_path, src_dir)
		target_dir = os.path.join(self.root_path, target_dir)
		print "svn branch " + src_dir + " " + target_dir
		subprocess.call(["svn", "copy", src_dir, target_dir])

	#
	# Calls svn update on repository root path: recursively updates
	# all branches.
	#
	def update_all(self):
		subprocess.call(["svn", "update", self.root_path])

	#
	# Returns list of directories and files added to svn
	# repo that are in the specified directory. This directory path
	# is relative to svn repo root path. Default value is svn repo root
	# path.
	#
	def list(self, dir = ""):
		full_path = os.path.join(self.root_path, dir)

		output = subprocess.check_output(["svn", "list", full_path])
		lines = output.split("\n")
		lines.remove("")

		return lines

	#
	# Returns True if the specified path is tracked by svn. False otherwise.
	#
	def is_tracked(self, file_path):
		full_path = os.path.join(self.root_path, file_path)

		fnull = open(os.devnull, "w")
		svn_retval = subprocess.call(["svn", "info", full_path], \
			stdout = fnull, stderr = fnull)
		return not bool(svn_retval)


class SvnFlow:
	def __init__(self):
		self.svn = Svn(svn_utils.find_svn_root_path())


	def init(self):
		self.__create_dir("trunk")

		branches_dir = "branches"
		self.__create_dir(branches_dir)

		self.__create_dir("tags")

		self.__create_develop_branch(branches_dir)

		features_dir = os.path.join(branches_dir, "feature")
		self.__create_dir(features_dir)

		releases_dir = os.path.join(branches_dir, "release")
		self.__create_dir(releases_dir)

		hotfix_dir = os.path.join(branches_dir, "hotfix")
		self.__create_dir(hotfix_dir)

		self.svn.update_all()


	def __create_dir(self, dir_path):
		self.__raise_if_dir_invalid(dir_path)

		full_path = os.path.join(self.svn.root_path, dir_path)
		if not os.path.exists(full_path):
			self.svn.mkdir(dir_path)
			self.__commit_and_log("Created directory '" \
				+ dir_path + "'.")
		else:
			log("Directory '" + dir_path + "' exists. Skipping.")


	def __create_develop_branch(self, branches_dir):
		dir_path = os.path.join(branches_dir, "develop")
		self.__raise_if_dir_invalid(dir_path)

		full_path = os.path.join(self.svn.root_path, dir_path)
		if not os.path.exists(full_path):
			self.svn.branch("trunk", dir_path)
			self.__commit_and_log(svn, "Created 'develop' branch.")
		else:
			log("Branch 'develop' exists. Skipping")


	def __commit_and_log(self, msg):
		self.svn.commit(msg)
		log(msg)


	def __raise_if_dir_invalid(self, dir_path):
		full_path = os.path.join(self.svn.root_path, dir_path)

		if os.path.exists(full_path) and not self.svn.is_tracked(dir_path):
			raise Exception("'" + dir_path + "' is not tracked by SVN.")

		if self.svn.is_tracked(dir_path) and not os.path.isdir(full_path):
			raise Exception("'" + dir_path + "' is not a directory.")


main()
