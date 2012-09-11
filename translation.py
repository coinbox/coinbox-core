#!/usr/bin/python

# Based on: http://babel.edgewall.org/wiki/Documentation/0.9/cmdline.html
# Interface to the babel translation tools
# First, write_map, then extract, init, (edit the po file in ./locale/<locale>/LC_MESSAGES/<domain>.po),
#        compile, and after changes in the .pot file (if any) update.

import subprocess

def get_domain(mod):
    if mod == "":
        return "main"
    else:
        return "mod_%s" % (mod,)

def do_extract(mod):
    domain = get_domain(mod)
    
    subprocess.call(["pybabel", "extract",
                     "--output=./locale/%s.pot" % (domain,),
                     "--mapping=./locale/%s.map" % (domain,),
                     "--project=coinbox",
                     "--version=1.0",
                     "./"])

def do_init(mod, locale):
    domain = get_domain(mod)
    
    subprocess.call(["pybabel", "init",
                     "--domain=%s" % (domain,),
                     "--input-file=./locale/%s.pot" % (domain,),
                     "--output-dir=./locale",
                     "--locale=%s" % (locale,)])

def do_compile(mod, locale):
    domain = get_domain(mod)
    
    subprocess.call(["pybabel", "compile",
                     "--domain=%s" % (domain,),
                     "--directory=./locale",
                     "--locale=%s" % (locale,),
                     "--input-file=./locale/%s/LC_MESSAGES/%s.po" % (locale, domain,)])

def do_update(mod, locale):
    domain = get_domain(mod)
    
    subprocess.call(["pybabel", "update",
                     "--domain=%s" % (domain,),
                     "--input-file=./locale/%s.pot" % (domain,),
                     "--output-dir=./locale",
                     "--locale=%s" % (locale,)])

def write_map_for_module(mod):
    domain = get_domain(mod)
    if mod == "":
        with open("./locale/%s.map" % (domain,), "w") as f:
            f.write("""# Extraction from Python source files
[python: app/*.py]
# Only one level down in the tree structure, to not include modules
# Maybe that's not even necessary
[python: app/*/*.py]

    """)
    else:
        with open("./locale/%s.map" % (domain,), "w") as f:
            f.write("""# Extraction from Python source files
[python: app/mod/%s/**.py]

    """ % (mod,))

if __name__ == "__main__":
    options = {"write_map": write_map_for_module,
               "extract": do_extract,
               "init": do_init,
               "compile": do_compile,
               "update": do_update}
    
    for i, s in enumerate(options):
        print i, "-", s 
    
    opt = None
    while opt not in options:
        opt = raw_input("What do you want to do?")

    mod = raw_input("Which module?(leave empty if not a module)")
    args = [mod]
    
    if opt in ("init", "compile", "update"):
        locale = raw_input("What locale?")
        args.append(locale)

    options[opt](*args)
    
    print "Done."
