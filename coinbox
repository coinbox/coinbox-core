#!/usr/bin/env python

from __future__ import division

import sys, os, logging

cbpos = None
retcode = 0
try:
    import cbpos
    from cbpos.bootstrap import bootstrap
    bootstrap()
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
