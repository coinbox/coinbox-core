import sys, traceback, StringIO
import app

def log(level, message):
    if app.config['app', 'log']:
        if level == 'ERROR':
            print >>sys.stderr, '[%s]' % (level,), message
            #raise
            print >>sys.stderr, get_traceback()
        else:
            print '[%s]' % (level,), message

def get_traceback():
    strio = StringIO.StringIO()
    traceback.print_exc(file=strio)
    exc = strio.getvalue()
    strio.close()
    return exc
