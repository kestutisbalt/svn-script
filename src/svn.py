import os
import subprocess


#
# This class wraps svn command line tool.
#
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

	#
	# Returns full system path to the specified path relative to repository
	# root path.
	#
	def full_path(self, path):
		return os.path.join(self.root_path, path)


	def merge(self, src_dir, dest_dir, reintegrate = False):
		os.chdir(self.full_path(dest_dir))

		args = ["svn", "merge"]
		if reintegrate:
			args.append("--reintegrate")

		args.append(self.full_path(src_dir))
		subprocess.call(args)


	def remove(self, path):
		subprocess.call(["svn", "remove", self.full_path(path)])
