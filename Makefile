PYTHON = `which python2 python | head -n 1`
PIP = `which pip`

COINBOX_TMP = ./coinbox-install

GIT_BASE_URL = https://github.com/coinbox
GIT_BRANCH = master
INSTALL_MODULES = `echo base config installer currency auth customer stock sales taxes`

PIP_INSTALL = $(PIP) install

all: develop install-modules

install-requirements:
		@echo "Installing from requirements file..."
		${PIP_INSTALL} -r ./requirements.txt

install:
		@echo "Installing Coinbox-pos only..."
		${PIP_INSTALL} .

install-git:
		@echo "Installing Coinbox-pos only using git (in develop mode)..."
		${PIP_INSTALL} git+${GIT_BASE_URL}/coinbox-core@${GIT_BRANCH}#egg=Coinbox-pos

develop:
		@echo "Installing Coinbox-pos only (in develop mode)..."
		${PIP_INSTALL} -e .

develop-git:
		@echo "Installing Coinbox-pos only using git (in develop mode)..."
		${PIP_INSTALL} -e git+${GIT_BASE_URL}/coinbox-core@${GIT_BRANCH}#egg=Coinbox-pos

install-modules: install-modules-zip

install-modules-zip:
		@echo "Installing selected Coinbox-mod-* using zip..."
		@echo ${INSTALL_MODULES}
		mkdir -p ${COINBOX_TMP}
		for mod in ${INSTALL_MODULES}; do \
			wget -O ${COINBOX_TMP}/$${mod}.zip ${GIT_BASE_URL}/coinbox-mod-$${mod}/archive/${GIT_BRANCH}.zip ; \
			unzip ${COINBOX_TMP}/$${mod}.zip -d ${COINBOX_TMP} ; \
			${PIP_INSTALL} ${COINBOX_TMP}/coinbox-mod-$${mod}-${GIT_BRANCH} ; \
			done ;
		rm -rf ${COINBOX_TMP}

install-modules-git:
		@echo "Installing selected Coinbox-mod-* using git..."
		@echo ${INSTALL_MODULES}
		for mod in ${INSTALL_MODULES}; do \
			${PIP_INSTALL} git+${GIT_BASE_URL}/coinbox-mod-$${mod}@${GIT_BRANCH}#egg=Coinbox-mod-$${mod} ; \
			done ;

develop-modules: develop-modules-git

develop-modules-zip:
		@echo "Installing selected Coinbox-mod-* using zip (in develop mode)..."
		@echo ${INSTALL_MODULES}
		mkdir -p ${COINBOX_TMP}
		for mod in ${INSTALL_MODULES}; do \
			wget -O ${COINBOX_TMP}/$${mod}.zip ${GIT_BASE_URL}/coinbox-mod-$${mod}/archive/${GIT_BRANCH}.zip ; \
			unzip ${COINBOX_TMP}/$${mod}.zip -d ${COINBOX_TMP} ; \
			${PIP_INSTALL} -e ${COINBOX_TMP}/coinbox-mod-$${mod}-${GIT_BRANCH} ; \
			done ;

develop-modules-git:
		@echo "Installing selected Coinbox-mod-* using git (in develop mode)..."
		@echo ${INSTALL_MODULES}
		for mod in ${INSTALL_MODULES}; do \
			${PIP_INSTALL} -e git+${GIT_BASE_URL}/coinbox-mod-$${mod}@${GIT_BRANCH}#egg=Coinbox-mod-$${mod} ; \
			done ;
