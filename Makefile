PYTHON = `which python2 python | head -n 1`
PIP = pip
PIP_INSTALL = $(PIP) install
PIP_DEVELOP = $(PIP_INSTALL) -e
PIP_REQUIRE = $(PIP_INSTALL) -r
PIP_UPGRADE_OPTION = --upgrade

COINBOX_TMP = ./coinbox-install

COINBOX_GIT_BASE_URL = https://github.com/coinbox
COINBOX_GIT_BRANCH = master
COINBOX_INSTALL_MODULES = base config installer currency auth customer stock sales taxes
COINBOX_UPGRADE = 0

ifneq (${COINBOX_UPGRADE}, 0)
	PIP_INSTALL += $(PIP_UPGRADE_OPTION)
	PIP_DEVELOP += $(PIP_UPGRADE_OPTION)
	# Do not add it to PIP_REQUIRE
	# PIP_REQUIRE += $(PIP_UPGRADE_OPTION)
endif

all: install install-modules

install-requirements:
		@echo "Installing from requirements file..."
		${PIP_REQUIRE} ./requirements.txt

install:
		@echo "Installing Coinbox-pos only..."
		${PIP_INSTALL} .

install-git:
		@echo "Installing Coinbox-pos only using git (in develop mode)..."
		${PIP_INSTALL} git+${COINBOX_GIT_BASE_URL}/coinbox-core@${COINBOX_GIT_BRANCH}#egg=Coinbox-pos

develop:
		@echo "Installing Coinbox-pos only (in develop mode)..."
		${PIP_DEVELOP} .

develop-git:
		@echo "Installing Coinbox-pos only using git (in develop mode)..."
		${PIP_DEVELOP} git+${COINBOX_GIT_BASE_URL}/coinbox-core@${COINBOX_GIT_BRANCH}#egg=Coinbox-pos

install-modules: install-modules-zip

install-modules-zip:
		@echo "Installing selected Coinbox-mod-* using zip..."
		@echo ${COINBOX_INSTALL_MODULES}
		mkdir -p ${COINBOX_TMP}
		for mod in ${COINBOX_INSTALL_MODULES}; do \
			wget -O ${COINBOX_TMP}/$${mod}.zip ${COINBOX_GIT_BASE_URL}/coinbox-mod-$${mod}/archive/${COINBOX_GIT_BRANCH}.zip ; \
			unzip ${COINBOX_TMP}/$${mod}.zip -d ${COINBOX_TMP} ; \
			${PIP_INSTALL} ${COINBOX_TMP}/coinbox-mod-$${mod}-${COINBOX_GIT_BRANCH} ; \
			done ;
		rm -rf ${COINBOX_TMP}

install-modules-git:
		@echo "Installing selected Coinbox-mod-* using git..."
		@echo ${COINBOX_INSTALL_MODULES}
		for mod in ${COINBOX_INSTALL_MODULES}; do \
			${PIP_INSTALL} git+${COINBOX_GIT_BASE_URL}/coinbox-mod-$${mod}@${COINBOX_GIT_BRANCH}#egg=Coinbox-mod-$${mod} ; \
			done ;

develop-modules: develop-modules-git

develop-modules-zip:
		@echo "Installing selected Coinbox-mod-* using zip (in develop mode)..."
		@echo ${COINBOX_INSTALL_MODULES}
		mkdir -p ${COINBOX_TMP}
		for mod in ${COINBOX_INSTALL_MODULES}; do \
			wget -O ${COINBOX_TMP}/$${mod}.zip ${COINBOX_GIT_BASE_URL}/coinbox-mod-$${mod}/archive/${COINBOX_GIT_BRANCH}.zip ; \
			unzip ${COINBOX_TMP}/$${mod}.zip -d ${COINBOX_TMP} ; \
			${PIP_DEVELOP} ${COINBOX_TMP}/coinbox-mod-$${mod}-${COINBOX_GIT_BRANCH} ; \
			done ;

develop-modules-git:
		@echo "Installing selected Coinbox-mod-* using git (in develop mode)..."
		@echo ${COINBOX_INSTALL_MODULES}
		for mod in ${COINBOX_INSTALL_MODULES}; do \
			${PIP_DEVELOP} git+${COINBOX_GIT_BASE_URL}/coinbox-mod-$${mod}@${COINBOX_GIT_BRANCH}#egg=Coinbox-mod-$${mod} ; \
			done ;
