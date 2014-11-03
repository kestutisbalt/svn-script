#
# This module holds utility functions related to console.
#

import os
import subprocess

COLOR_RED = "\033[31m"
COLOR_GREEN = "\033[32m"
COLOR_RESET = "\033[0m"


def print_error(err_msg):
	print COLOR_RED + err_msg + COLOR_RESET


def text_green(text):
	return COLOR_GREEN + text + COLOR_RESET


def text_red(text):
	return COLOR_RED + text + COLOR_RESET


#
# Silently executes shell command with the specified arguments.
# Returns what the executed program returned.
#
def exec_silent(args):
	fnull = open(os.devnull, "w")
	return subprocess.call(args, stdout = fnull, stderr = fnull)
