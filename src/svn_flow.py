#!/usr/bin/python

import os
from optparse import OptionParser
from sys import stdin
from sys import stdout

import svn_utils
import console_utils
from svn import Svn


#
# Returns exit code.
#
def main():
	retval = 0

	opt_parser = OptionParser()
	(options, args) = opt_parser.parse_args();

	if len(args) > 0:
		svn_flow = SvnFlow()

		cmd = args[0]
		if cmd == "init":
			svn_flow.init()

		elif cmd == "test":
			retval = svn_flow.test()

		elif cmd == "feature":
			funcs = {"start" : svn_flow.feature_start, \
				"finish" : svn_flow.feature_finish, \
				"list" : svn_flow.feature_list,\
				"help" : on_cmd_feature_help}
			on_cmd_branch(args[1:], funcs)

		elif cmd == "release":
			funcs = {"start" : svn_flow.release_start, \
				"finish" : svn_flow.release_finish, \
				"list" : svn_flow.release_list,\
				"help" : on_cmd_release_help}
			on_cmd_branch(args[1:], funcs)

		else:
			retval = 1
			console_utils.print_error("Unknown command: " + cmd)
	else:
		print "Usage:"
		print ("\tsvn-flow init - initializes svn repository to work "
			"with svn-flow.")

	return retval


def on_cmd_branch(args, branch_functions):
	if len(args) < 1:
		cmd = "help"
	else:
		cmd = args[0]

	try:
		if cmd == "start":
			if len(args) < 2:
				raise Exception("Release name must be specified.")
			branch_functions["start"](args[1])

		elif cmd == "finish":
			if len(args) < 2:
				raise Exception("Release name must be specified.")
			branch_functions["finish"](args[1])

		elif cmd == "list":
			branch_functions["list"]()

		elif cmd == "help":
			branch_functions["help"]()

		else:
			raise Exception("Unknown command: " + cmd)

	except Exception, e:
		console_utils.print_error(str(e))
		branch_functions["help"]()


def on_cmd_release_help():
	print "Usage:"
	print ("\tsvn-flow release start <name> - creates new branch off "
		"develop named branches/release/<name>.")
	print ("\tsvn-flow release finish <name> - merges branches/release<name> "
		"back to develop.")
	print "\tsvn-flow release list - lists all release branches."
	print "\tsvn-flow release help - prints this help message."


def on_cmd_feature_help():
	print "Usage:"
	print ("\tsvn-flow feature start <name> - creates new branch off "
		"develop named branches/feature/<name>.")
	print ("\tsvn-flow feature finish <name> - merges branches/feature<name> "
		"back to develop.")
	print "\tsvn-flow feature list - lists all feature branches."
	print "\tsvn-flow feature help - prints this help message."


def log(msg):
	print msg


class SvnFlow:
	def __init__(self):
		self.svn = Svn(svn_utils.find_svn_root_path())

		self.trunk_dir = "trunk"
		self.tags_dir = "tags"
		self.branches_dir = "branches"
		self.develop_branch = os.path.join(self.branches_dir, "develop")
		self.feature_dir = os.path.join(self.branches_dir, "feature")
		self.release_dir = os.path.join(self.branches_dir, "release")
		self.hotfix_dir = os.path.join(self.branches_dir, "hotfix")

		self.branch_dir_by_type = {"feature" : self.feature_dir, \
			"release" : self.release_dir, \
			"hotfix" : self.hotfix_dir}


	def init(self):
		self.__create_dir(self.trunk_dir)
		self.__create_dir(self.branches_dir)
		self.__create_dir(self.tags_dir)

		self.__create_develop_branch()

		self.__create_dir(self.feature_dir)
		self.__create_dir(self.release_dir)
		self.__create_dir(self.hotfix_dir)

		self.svn.update_all()


	#
	# Returns 0 if no errors were encountered. Otherwise 1 is returned.
	#
	def test(self):
		retval = 0

		retval = self.__test_dir("trunk") or retval
		retval = self.__test_dir("tags") or retval

		retval = self.__test_dir(self.branches_dir) or retval

		retval = self.__test_dir(self.feature_dir) or retval
		retval = self.__test_dir(self.release_dir) or retval
		retval = self.__test_dir(self.hotfix_dir) or retval

		return retval


	def feature_start(self, name):
		self.__branch_start(name, "feature", self.develop_branch)


	def feature_finish(self, name):
		feature_branch = os.path.join(self.feature_dir, name)
		self.__raise_if_dir_invalid(feature_branch)

		self.svn.update_all()
		self.svn.merge(feature_branch, self.develop_branch,
			reintegrate = True)
		self.__commit_and_log("Merged feature '" + name + "' to develop.")

		self.svn.remove(feature_branch)
		self.__commit_and_log("Removed feature '" + name + "' branch.")
		self.svn.update_all()


	def feature_list(self):
		self.__branch_list("feature")


	def release_start(self, name):
		self.__branch_start(name, "release", self.develop_branch)


	def release_finish(self, name):
		release_branch = os.path.join(self.release_dir, name)
		self.__raise_if_dir_invalid(release_branch)

		self.svn.update_all()
		self.svn.merge(release_branch, self.trunk_dir)
		self.__commit_and_log("Merged release '" + name + "' to trunk.")

		self.svn.update_all()
		tag_branch = os.path.join(self.tags_dir, name)
		tag_message = self.__get_tag_message()
		self.svn.tag(self.trunk_dir, tag_branch, tag_message)

		self.svn.update_all()
		self.svn.merge(release_branch, self.develop_branch,
			reintegrate = True)
		self.__commit_and_log("Merged release '" + name + "' to develop.")

		self.svn.remove(release_branch)
		self.__commit_and_log("Removed release '" + name + "' branch.")
		self.svn.update_all()


	def release_list(self):
		self.__branch_list("release")


	def __branch_list(self, branch_type):
		branches = self.svn.list(self.branch_dir_by_type[branch_type])
		if len(branches) < 1:
			print "No " + branch_type +" branches are present."
		else:
			print branch_type + " branches:"
			for b in branches:
				print "\t" + b[:-1]


	def __branch_start(self, name, branch_type, branch_off):
		branch_dir = self.branch_dir_by_type[branch_type]
		branch = os.path.join(branch_dir, name)
		if os.path.exists(self.svn.full_path(branch)):
			raise Exception(branch_type + " branch '" + branch \
				+ "' already exists.")

		self.svn.update_all()
		self.svn.branch(branch_off, branch)
		self.__commit_and_log("Created " + branch_type + " branch '" \
			+ name + "'.");
		self.svn.update_all()


	#
	# Reads tag message from stdin and returns the result.
	#
	def __get_tag_message(self):
		stdout.write("Tag message: ")
		return stdin.readline()[:-1]


	def __test_dir(self, dir_path):
		retval = 0

		try:
			self.__raise_if_dir_invalid(dir_path)
			self.__raise_if_not_exists(dir_path)

			log(dir_path + " [" + console_utils.text_green("OK") \
				+ "]")
		except Exception, e:
			log(dir_path + " [" + console_utils.text_red("FAIL") \
				+ "]")
			console_utils.print_error(str(e))
			retval = 1

		return retval


	def __create_dir(self, dir_path):
		self.__raise_if_dir_invalid(dir_path)

		full_path = self.svn.full_path(dir_path)
		if not os.path.exists(full_path):
			self.svn.mkdir(dir_path)
			self.__commit_and_log("Created directory '" \
				+ dir_path + "'.")
		else:
			log("Directory '" + dir_path + "' exists. Skipping.")


	def __create_develop_branch(self):
		self.__raise_if_dir_invalid(self.develop_branch)

		full_path = self.svn.full_path(self.develop_branch)
		if not os.path.exists(full_path):
			self.svn.branch(self.trunk_dir, self.develop_branch)
			self.__commit_and_log("Created 'develop' branch.")
		else:
			log("Branch 'develop' exists. Skipping")


	def __commit_and_log(self, msg):
		os.chdir(self.svn.root_path)
		self.svn.commit(msg)
		log(msg)


	def __raise_if_dir_invalid(self, dir_path):
		full_path = self.svn.full_path(dir_path)

		if os.path.exists(full_path) and not self.svn.is_tracked(dir_path):
			raise Exception("'" + dir_path + "' is not tracked by SVN.")

		if self.svn.is_tracked(dir_path) and not os.path.isdir(full_path):
			raise Exception("'" + dir_path + "' is not a directory.")


	def __raise_if_not_exists(self, path):
		full_path = self.svn.full_path(path)
		if not os.path.exists(full_path):
			raise Exception("'" + full_path + "' does not exist.")


exit(main())
