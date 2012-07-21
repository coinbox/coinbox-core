#!/usr/bin/python
# -*- coding: utf-8 -*-

import gettext
import os

"""
Steps: (maybe 1- needs to be changed
1- xgettext --language=Python test.py
2- msginit -l fr-FR messages.pot
3- nano fr-FR.po
4- mkdir fr-FR
5- mkdir fr-FR/LC_MESSAGES
6- msgfmt fr-FR.po -o fr-FR/LC_MESSAGES/domain.mo
"""

tr = gettext.translation('domain', os.path.abspath('./locale'), languages=['fr-FR'], fallback=False)
_ = tr.ugettext

print _("some value")

print "that same value"

class Something:
    def __init__(self):
        print _("something else")

print 'ew'
print Something()