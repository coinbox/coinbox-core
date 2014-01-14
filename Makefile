PYTHON = `which python2 python | head -n 1`
PIP = `which pip`

COINBOX_TMP = ./tmp-modules
COINBOX_TARGET = ./coinbox-install

GIT_BASE_URL = https://github.com/coinbox
GIT_BRANCH = setup
INSTALL_MODULES = `echo base config installer currency auth customer stock sales taxes`

PIP_INSTALL = $(PIP) install

all:
		@echo "Installing from requirements file..."
		${PIP_INSTALL} -r ./requirements.txt

install:
		@echo "Installing Coinbox-pos only..."
		${PIP_INSTALL} .

develop:
		@echo "Installing Coinbox-pos only (in develop mode)..."
		${PIP_INSTALL} .

install-modules:
		@echo "Installing selected Coinbox-mod-*..."
		@echo ${INSTALL_MODULES}
		mkdir -p ${COINBOX_TMP}
		for mod in ${INSTALL_MODULES}; do \
			wget -O ${COINBOX_TMP}/$${mod}.zip ${GIT_BASE_URL}/coinbox-mod-$${mod}/archive/${GIT_BRANCH}.zip ; \
			unzip ${COINBOX_TMP}/$${mod}.zip -d ${COINBOX_TMP} ; \
			${PIP_INSTALL} ${COINBOX_TMP}/coinbox-mod-$${mod}-${GIT_BRANCH} ; \
			done ;
		rm -rf ${COINBOX_TMP}
			
develop-modules:
		@echo "Installing selected Coinbox-mod-* (in develop mode)..."
		@echo ${INSTALL_MODULES}
		mkdir -p ${COINBOX_TMP}
		for mod in ${INSTALL_MODULES}; do \
			wget -O ${COINBOX_TMP}/$${mod}.zip ${GIT_BASE_URL}/coinbox-mod-$${mod}/archive/${GIT_BRANCH}.zip ; \
			unzip ${COINBOX_TMP}/$${mod}.zip -d ${COINBOX_TMP} ; \
			${PIP_INSTALL} ${COINBOX_TMP}/coinbox-mod-$${mod}-${GIT_BRANCH} ; \
			done ;
