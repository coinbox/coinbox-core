PYTHON = `which python2 python | head -n 1`
PIP = `which pip`

COINBOX_TMP = ./tmp-modules
COINBOX_TARGET = ./coinbox-install

GIT_BASE_URL = https://github.com/coinbox/coinbox-mod-
GIT_BRANCH = master
INSTALL_MODULES = "base config installer currency auth customer stock sales taxes"

PIP_INSTALL = $(PIP) install ---target ${COINBOX_TARGET}

all:
		@echo Installing from requirements file...
		${PIP_INSTALL} -r ./requirements.txt

install:
		@echo Installing Coinbox-pos only
		${PIP_INSTALL} .

develop:
		@echo Installing Coinbox-pos only (in develop mode)
		${PIP_INSTALL} .

install-modules:
		@echo Installing selected Coinbox-mod-*
		mkdir -p ${COINBOX_TMP}
		for mod in ${INSTALL_MODULES}; do \
			@echo Installing Coinbox-mod-${mod} ; \
			mkdir -p ${COINBOX_TMP}/${mod}-${GIT_BRANCH} ; \
		    wget -O ${COINBOX_TMP}/${mod}.zip ${GIT_BASE_URL}${mod}/archive/${GIT_BRANCH}.zip ; \
		    unzip ${COINBOX_TMP}/${mod}.zip -d ${COINBOX_TMP}/${mod}-${GIT_BRANCH} ; \
		    ${PIP_INSTALL} ${COINBOX_TMP}/${mod}-${GIT_BRANCH} ; \
		    done ;
		rm -rf ${COINBOX_TMP}
		    
develop-modules:
		@echo Installing selected Coinbox-mod-* (in develop mode)
		mkdir -p ${COINBOX_TMP}
		for mod in ${INSTALL_MODULES}; do \
			@echo Installing Coinbox-mod-${mod} (in develop mode) ; \
			mkdir -p ${COINBOX_TMP}/${mod}-${GIT_BRANCH} ; \
		    wget -O ${COINBOX_TMP}/${mod}.zip ${GIT_BASE_URL}${mod}/archive/${GIT_BRANCH}.zip ; \
		    unzip ${COINBOX_TMP}/${mod}.zip -d ${COINBOX_TMP}/${mod}-${GIT_BRANCH} ; \
		    ${PIP_INSTALL} -e ${COINBOX_TMP}/${mod}-${GIT_BRANCH} ; \
		    done ;
