#!/usr/bin/python

# Based on: http://babel.edgewall.org/wiki/Documentation/0.9/cmdline.html
# Interface to the babel translation tools
# First, write_map, then extract, init, (edit the po file in ./locale/<locale>/LC_MESSAGES/<domain>.po),
#        compile, and after changes in the .pot file (if any) update.

class Translator(object):
    def __init__(self):
        self.locale_dir = './locale'
        self.project = 'coinbox'
        self.version = '1.0'
    
    def domain(self, mod):
        if mod == "":
            return "main"
        else:
            return "mod_%s" % (mod,)
    
    def path(self, mod):
        if mod == "":
            return './'
            return os.path.dirname(cbpos.__file__)
        else:
            return os.path.dirname(cbpos.modules.by_name(mod).path)

    def execute(self, command, *args, **kwargs):
        popen = ["pybabel", command]
        for kw, arg in kwargs.iteritems():
            popen.append('--{}={}'.format(kw.replace('_', '-'), arg))
        popen.extend(args)
        return subprocess.call(popen)
        
        """
        from babel.messages.frontend import CommandLineInterface
        cli = CommandLineInterface()
        cli._configure_logging(logging.ERROR)
        return getattr(cli, popen[1])(popen[2:]) # or cli.run(popen[1:])
        """

    def extract(self, mod):
        domain = self.domain(mod)
        path = self.path(mod)
        
        self.execute("extract", path,
             output=self.locale_dir+'/'+domain+'.pot',
             mapping=self.locale_dir+'/'+domain+'.map',
             project=self.project, version=self.version)

    def init(self, mod, locale):
        domain = self.domain(mod)
        
        self.execute("init", domain=domain,
            input_file=self.locale_dir+'/'+domain+'.pot',
            output_dir=self.locale_dir,
            locale=locale)

    def compile(self, mod, locale):
        domain = self.domain(mod)
        
        self.execute("compile", domain=domain,
            directory=self.locale_dir,
            locale=locale,
            input_file=self.locale_dir+'/'+locale+'/LC_MESSAGES/'+domain+'.po')

    def update(self, mod, locale):
        domain = self.domain(mod)
        
        self.execute("update", domain=domain,
            input_file=self.locale_dir+'/'+domain+'.pot',
            output_dir=self.locale_dir,
            locale=locale)

    def write_map(self, mod):
        domain = self.domain(mod)
        
        if mod == "":
            with open("%s/%s.map" % (self.locale_dir, domain,), "w") as f:
                f.write("""
[ignore: cbpos/mod/*/**.py]
# Extraction from Python source files
[python: cbpos/**.py]""")
        else:
            with open("%s/%s.map" % (self.locale_dir, domain,), "w") as f:
                f.write("""# Extraction from Python source files
[python: **.py]""")
    
    def main(self):
        options = ["write_map", "extract", "init", "compile", "update"]
        
        mod = raw_input("Which module are you working on?(leave empty for core)")
        
        if mod != '' and cbpos.modules.by_name(mod) is None:
            print 'No such module!'
            return None
        
        while True:
            args = [mod]
            for i, opt in enumerate(options):
                print i, "-", opt
            
            opt = raw_input("What do you want to do?")
            try:
                opt = options[int(opt)]
            except (IndexError, TypeError, ValueError):
                pass
            if opt in ("init", "compile", "update"):
                locale = raw_input("What locale?")
                args.append(locale)
            try:
                func = getattr(self, opt)
            except AttributeError:
                break
            func(*args)
            print 'Done.'
        
        print 'Done with this module.'
        
        return self.main()

if __name__ == "__main__":
    import sys, os
    sys.path.append(os.getcwd())
    import cbpos, os, subprocess, logging
    try:
        Translator().main()
    except KeyboardInterrupt:
        print
        print 'Yalla... Exiting!'
