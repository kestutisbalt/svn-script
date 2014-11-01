import os
import subprocess

from console_utils import exec_silent


#
# This class wraps svn command line tool.
#
class Svn:
	def __init__(self, svn_root_path):
		self.__assert_svn_repo(svn_root_path)
		self.root_path = svn_root_path

	#
	# The specified directory path is relative to svn repository root path.
	# E.g. to create trunk directory simply execute
	#	svn.mkdir("trunk")
	#
	def mkdir(self, relative_dir_path):
		full_path = self.full_path(relative_dir_path)
		exec_silent(["svn", "mkdir", full_path])

	def commit(self, msg):
		exec_silent(["svn", "commit", "-m", msg])

	#
	# The specified directory paths are relative to svn repository root path.
	# E.g. to create development branch directory simply execute
	#	svn.branch("trunk", "branches/develop")
	#
	def branch(self, src_dir, target_dir):
		exec_silent(["svn", "copy", self.full_path(src_dir), \
			self.full_path(target_dir)])

	#
	# Calls svn update on repository root path: recursively updates
	# all branches.
	#
	def update_all(self):
		exec_silent(["svn", "update", self.root_path])

	#
	# Returns list of directories and files added to svn
	# repo that are in the specified directory. This directory path
	# is relative to svn repo root path. Default value is svn repo root
	# path.
	#
	def list(self, dir = ""):
		output = subprocess.check_output(["svn", "list", \
			self.full_path(dir)])
		lines = output.split("\n")
		lines.remove("")

		return lines

	#
	# Returns True if the specified path is tracked by svn. False otherwise.
	#
	def is_tracked(self, file_path):
		args = ["svn", "info", self.full_path(file_path)]
		return not bool(exec_silent(args))

	#
	# Returns full system path to the specified path relative to repository
	# root path.
	#
	def full_path(self, path):
		return os.path.join(self.root_path, path)


	def svn_path(self, path):
		return os.path.join("^", path)


	def merge(self, src_dir, dest_dir, reintegrate = False):
		os.chdir(self.full_path(dest_dir))

		args = ["svn", "merge"]
		if reintegrate:
			args.append("--reintegrate")

		args.append(self.svn_path(src_dir))
		exec_silent(args)


	def remove(self, path):
		exec_silent(["svn", "remove", self.full_path(path)])


	def tag(self, src_branch, tag_branch, tag_msg):
		self.branch(src_branch, tag_branch)
		self.commit(tag_msg)


	def __assert_svn_repo(self, path):
		retval = exec_silent(["svn", "info"])
		if retval != 0:
			raise Exception("'" + path \
				+ "' is not valid svn repository.")
