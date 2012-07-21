#!/usr/bin/python
import sys

app = None
try:
    import app
    app.run()
except KeyboardInterrupt:
    sys.exit()
except Exception as e:
    if not app:
        raise
    app.log('ERROR', 'An error stopped the application')
finally:
    if app is not None:
        app.terminate()
