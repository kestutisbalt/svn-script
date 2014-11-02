SRC_DIR = $(CURDIR)/src

INSTALL_LIB_DIR = /usr/local/lib/svn-utils
INSTALL_BIN_DIR = /usr/local/bin

BUILD_DIR ?= $(CURDIR)/build
DEB_OUT_DIR = $(BUILD_DIR)/deb


all:
	@echo "Usage:"
	@echo "\tmake install - installs scripts to the system."
.PHONY: all


install:
	sudo mkdir -p $(INSTALL_LIB_DIR)
	sudo cp $(SRC_DIR)/*.py $(INSTALL_LIB_DIR)/
	sudo cp $(SRC_DIR)/*.sh $(INSTALL_LIB_DIR)/
	sudo ln -sf $(INSTALL_LIB_DIR)/svn_flow.py $(INSTALL_BIN_DIR)/svn-flow
	sudo ln -sf $(INSTALL_LIB_DIR)/svn_tags.py $(INSTALL_BIN_DIR)/svn-tags
	sudo ln -sf $(INSTALL_LIB_DIR)/svn_clean.sh $(INSTALL_BIN_DIR)/svn-clean
.PHONY: install


deb:
	mkdir -p $(DEB_OUT_DIR)
	ln -sf $(CURDIR)/deb/README.debian $(DEB_OUT_DIR)/README.debian
	ln -sf $(SRC_DIR)/*.py $(DEB_OUT_DIR)/
	ln -sf $(SRC_DIR)/*.sh $(DEB_OUT_DIR)/
	ln -sf $(INSTALL_LIB_DIR)/svn_flow.py $(DEB_OUT_DIR)/svn-flow
	ln -sf $(INSTALL_LIB_DIR)/svn_tags.py $(DEB_OUT_DIR)/svn-tags
	ln -sf $(INSTALL_LIB_DIR)/svn_clean.sh $(DEB_OUT_DIR)/svn-clean
	cd $(DEB_OUT_DIR) ; equivs-build --full $(CURDIR)/deb/svn-utils
.PHONY: deb


clean:
	rm -rf $(BUILD_DIR)
.PHONY: clean
