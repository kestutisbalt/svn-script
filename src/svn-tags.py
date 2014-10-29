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
from exceptions import Exception
from optparse import OptionParser

import svn_utils

COLOR_RED = "\033[31m"
COLOR_RESET = "\033[0m"


def main():
	opt_parser = OptionParser()
	opt_parser.add_option("-l", "--last-tag", \
		help = "Show only last tag name.", action = "store_true")

	(options, args) = opt_parser.parse_args();

	try:
		svn_base_dir = svn_utils.find_svn_base_dir()
		tags_dir = find_tags_dir(svn_base_dir)
		tags = find_tags(tags_dir)

		tags = sort_tags_desc(tags)

		if options.last_tag:
			print tags[0]["name"]
		else:
			print_tags(tags)
	except Exception, e:
		print_error(str(e))


def print_error(err_msg):
	print COLOR_RED + err_msg + COLOR_RESET


def print_tags(tags):
	print "Tags (latest first):"
	for t in tags:
		print "\t" + t["name"]

#
# Sort tags in descending order by their revision number: newest first.
#
def sort_tags_desc(tags):
	sorted_tags = tags[:]
	sorted_tags.sort(key = lambda tag : tag["revision"], reverse = True)
	return sorted_tags


def find_tags(tags_dir):
	output = subprocess.check_output(["svn", "list", tags_dir])
	lines = output.split("\n")
	lines.remove("")

	tags = []
	for tag_name in lines:
		tag_info = {}
		tag_info["name"] = tag_name[:-1];
		tag_info["revision"] = find_tag_revision(tags_dir, tag_name)
		tags.append(tag_info)

	return tags


def find_tag_revision(tags_dir, tag_name):
	tag_path = os.path.join(tags_dir, tag_name)
	output = subprocess.check_output(["svn", "log", tag_path, "--limit=1"])
	lines = output.split("\n")
	revision_info = lines[1].split(" |")
	return revision_info[0]


def find_tags_dir(svn_base_dir):
	tags_dir = "tags"
	files = os.listdir(svn_base_dir)
	if not tags_dir in files:
		raise Exception("SVN base dir does not have 'tags' dir.")

	return os.path.join(svn_base_dir, tags_dir)


main()
