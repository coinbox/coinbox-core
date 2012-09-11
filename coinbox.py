#!/usr/bin/python
import sys, logging

app = None
try:
    import app
    app.run()
except KeyboardInterrupt:
    pass
except Exception as e:
    if not app:
        raise
    logging.error('An error stopped the application')
    logging.exception(e)
finally:
    if app is not None:
        app.terminate()
    sys.exit()
