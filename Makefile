SRC_DIR = src

INSTALL_LIB_DIR = /usr/local/lib/svn-utils
INSTALL_BIN_DIR = /usr/local/bin


all:
	@echo "Usage:"
	@echo "\tmake install - installs scripts to the system."
.PHONY: all


install:
	sudo mkdir -p $(INSTALL_LIB_DIR)
	sudo cp $(SRC_DIR)/*.py $(INSTALL_LIB_DIR)/
	sudo ln -sf $(INSTALL_LIB_DIR)/svn_flow.py $(INSTALL_BIN_DIR)/svn-flow
	sudo ln -sf $(INSTALL_LIB_DIR)/svn_tags.py $(INSTALL_BIN_DIR)/svn-tags
.PHONY: install
