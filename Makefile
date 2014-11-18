SRC_DIR = $(CURDIR)/src


INSTALL_LIB_DIR = usr/lib/svn-utils
INSTALL_LIB_PATH = /$(INSTALL_LIB_DIR)
INSTALL_BIN_DIR = usr/bin
INSTALL_BIN_PATH = /$(INSTALL_BIN_DIR)

BUILD_DIR ?= $(CURDIR)/build
VERSION := $(shell git describe --abbrev=0 HEAD --tags)
DEB_OUT_DIR = $(BUILD_DIR)/svn-utils-$(VERSION)


all:
	@echo "Usage:"
	@echo "\tmake install - installs scripts to the system."
	@echo "\tmake deb - creates debian package."
	@echo "\tmake clean - removes build directory."
.PHONY: all


install:
	sudo mkdir -p $(INSTALL_LIB_PATH)
	sudo cp $(SRC_DIR)/*.py $(INSTALL_LIB_PATH)/
	sudo cp $(SRC_DIR)/*.sh $(INSTALL_LIB_PATH)/
	sudo ln -sf $(INSTALL_LIB_PATH)/svn_flow.py $(INSTALL_BIN_PATH)/svn-flow
	sudo ln -sf $(INSTALL_LIB_PATH)/svn_tags.py $(INSTALL_BIN_PATH)/svn-tags
	sudo ln -sf $(INSTALL_LIB_PATH)/svn_clean.sh $(INSTALL_BIN_PATH)/svn-clean
.PHONY: install


deb:
	mkdir -p $(DEB_OUT_DIR)/debian
	cp -Rf $(CURDIR)/deb/* $(DEB_OUT_DIR)/debian/
	mkdir -p $(DEB_OUT_DIR)/$(INSTALL_LIB_DIR)
	mkdir -p $(DEB_OUT_DIR)/$(INSTALL_BIN_DIR)
	cp $(SRC_DIR)/*.py $(DEB_OUT_DIR)/$(INSTALL_LIB_DIR)/
	cp $(SRC_DIR)/*.sh $(DEB_OUT_DIR)/$(INSTALL_LIB_DIR)/
	ln -sf $(INSTALL_LIB_PATH)/svn_flow.py $(DEB_OUT_DIR)/$(INSTALL_BIN_DIR)/svn-flow
	ln -sf $(INSTALL_LIB_PATH)/svn_tags.py $(DEB_OUT_DIR)/$(INSTALL_BIN_DIR)/svn-tags
	ln -sf $(INSTALL_LIB_PATH)/svn_clean.sh $(DEB_OUT_DIR)/$(INSTALL_BIN_DIR)/svn-clean
	cd $(DEB_OUT_DIR) ; dpkg-buildpackage -rfakeroot -uc -us
.PHONY: deb


clean:
	rm -rf $(BUILD_DIR)
.PHONY: clean
