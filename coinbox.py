#!/usr/bin/env python

from __future__ import division

import sys, os, logging

cbpos = None
retcode = 0
try:
    import cbpos
    from cbpos.bootstrap import bootstrap
    # Read the directories from os.environ or None, which uses defaults
    # Could also read from a .ini file for the sake of simplicity
    # For example
    #        C:\Program Files\Coinbox\directories.ini    (depending on sys.executable if frozen)
    #    or  /etc/coinbox/directories.ini    (it would be easily packageable and root owned; and we could expanduser too from there)
    bootstrap(
        config_dir=os.environ.get('COINBOX_CONFIG_DIR', None),
        data_dir=os.environ.get('COINBOX_DATA_DIR', None),
        locale_dir=os.environ.get('COINBOX_LOCALE_DIR', None)
    )
    retcode = cbpos.run()
except KeyboardInterrupt:
    pass
except Exception as e:
    logging.error('An error stopped the application')
    logging.exception(e)
    retcode = 1
finally:
    logging.info('Exiting...')
    try:
        if cbpos is not None:
            cbpos.terminate(retcode)
    except:
        retcode = 1 if retcode == 0 else retcode
        sys.exit(retcode)
