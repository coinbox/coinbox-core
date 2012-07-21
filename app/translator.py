import app
import gettext

app.config.set_default('locale', 'use', '1')
app.config.set_default('locale', 'localedir', './locale')
app.config.set_default('locale', 'languages', '')
app.config.set_default('locale', 'fallback', '1')
app.config.set_default('locale', 'codeset', '')

class TranslatorBuilder(object):
    def __init__(self, localedir=None, languages=None, class_=None, fallback=None, codeset=None):
        self.tr = Translator()
        
        self.localedir = localedir
        self.languages = languages
        self.class_ = class_
        self.fallback = fallback
        self.codeset = codeset
    
    def add(self, module_name, domain=None, localedir=None, languages=None, class_=None, fallback=True, codeset=None):
        module_tr = ModuleTranslator(domain=domain if domain is not None else self.default_domain(module_name),
                                     localedir=localedir if localedir is not None else self.localedir,
                                     languages=languages if languages is not None else self.languages,
                                     class_=class_ if class_ is not None else self.class_,
                                     fallback=fallback if fallback is not None else self.fallback,
                                     codeset=codeset if codeset is not None else self.codeset)
        setattr(self.tr, module_name, module_tr)
    
    def install(self):
        main_tr = ModuleTranslator(domain="main", localedir=self.localedir, languages=self.languages,
                                     class_=self.class_, fallback=self.fallback, codeset=self.codeset)
        self.tr._ = main_tr._
        app.tr = self.tr
    
    def default_domain(self, module_name):
        return 'mod_%s' % (module_name,)

class DummyTranslatorBuilder(object):
    def __init__(self, localedir=None, languages=None, class_=None, fallback=None, codeset=None):
        self.tr = Translator()
    
    def add(self, module_name, domain=None, localedir=None, languages=None, class_=None, fallback=True, codeset=None):
        setattr(self.tr, module_name, Translator())
    
    def install(self):
        app.tr = self.tr

class Translator(object):
    def _(self, message):
        return message

class ModuleTranslator(object):
    def __init__(self, domain, localedir=None, languages=None, class_=None, fallback=None, codeset=None):
        self.translation = gettext.translation(domain, localedir, languages, class_, fallback, codeset)
    
    def _(self, message):
        return self.translation.ugettext(message)
