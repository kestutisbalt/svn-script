#!/usr/bin/python

import os
from optparse import OptionParser

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
			on_cmd_feature(svn_flow, args[1:])

		else:
			retval = 1
			console_utils.print_error("Unknown command: " + cmd)
	else:
		print "Usage:"
		print ("\tsvn-flow init - initializes svn repository to work "
			"with svn-flow.")

	return retval


def on_cmd_feature(svn_flow, args):
	if len(args) < 1:
		cmd = "help"
	else:
		cmd = args[0]

	try:
		if cmd == "start":
			if len(args) < 2:
				raise Exception("Feature name must be specified.")
			svn_flow.feature_start(args[1])

		elif cmd == "finish":
			if len(args) < 2:
				raise Exception("Feature name must be specified.")
			svn_flow.feature_finish(args[1])

		elif cmd == "list":
			svn_flow.feature_list()

		elif cmd == "help":
			on_cmd_feature_help()

		else:
			raise Exception("Unknown command: " + cmd)

	except Exception, e:
		console_utils.print_error(str(e))
		on_cmd_feature_help()


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
		feature_branch = os.path.join(self.feature_dir, name)
		if os.path.exists(self.svn.full_path(feature_branch)):
			raise Exception("Feature branch '" + feature_branch \
				+ "' already exists.")

		self.svn.update_all()
		self.svn.branch(self.develop_branch, feature_branch)
		self.__commit_and_log("Created feature branch '" + name + "'.");
		self.svn.update_all()


	def feature_finish(self, name):
		feature_branch = os.path.join(self.feature_dir, name)
		self.__raise_if_dir_invalid(feature_branch)

		self.svn.update_all()
		self.svn.merge(feature_branch, self.develop_branch)
		self.__commit_and_log("Merged feature '" + name + "' to develop.")

		self.svn.remove(feature_branch)
		self.__commit_and_log("Removed feature '" + name + "' branch.")
		self.svn.update_all()


	def feature_list(self):
		features = self.svn.list(self.feature_dir)
		if len(features) < 1:
			print "No feature branches are present."
		else:
			print "Feature branches:"
			for f in features:
				print "\t" + f[:-1]


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
