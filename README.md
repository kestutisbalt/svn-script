svn-script
==========

Various scripts to work with subversion.

svn-flow
--------

Works only with subversion 1.7.


svn-tags
--------

Works only with subversion 1.7.


### Installation

svn utilities might be installed with install script or Debian package. The
recommended way is to build Debian package and then install it.

Install script simply copies the neccessary files to appropriate locations:

	make install


#### With Debian package

To build Debian package you need equivs-build program. It's in equivs package:

	$ sudo apt-get install equivs

Then simply run

	$ make deb

This creates debian package to ./build/deb. Then install it:

	$ sudo dpkg -i ./build/deb/svn-utils-*.deb


TODO
----

- [ ] Rename project to svn-utils.
- [+] Add branch listing script: lists dir in `$repo/branches`.
- [ ] Colored diff: 'svn diff | vim -'. Could be 'svn-cdiff' command or so.
- [ ] Bash auto completion.
- [+] Build debian package.
- [ ] Add tests.
- [ ] Versioning.
