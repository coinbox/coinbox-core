#!/usr/bin/python
import sys, os, logging

# Make symbolic links work
os.chdir(os.path.dirname(os.path.realpath(__file__)))

app = None
try:
    import cbpos
    cbpos.run()
except KeyboardInterrupt:
    pass
except Exception as e:
    logging.error('An error stopped the application')
    logging.exception(e)
finally:
    logging.info('Exiting...')
    if app is not None:
        cbpos.terminate()
    sys.exit()
