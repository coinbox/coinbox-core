import cbpos
import gettext

cbpos.config.set_default('locale', 'use', True)
cbpos.config.set_default('locale', 'languages', list())
cbpos.config.set_default('locale', 'fallback', True)
cbpos.config.set_default('locale', 'codeset', '')

class TranslatorBuilder(object):
    """
    Helper class to create a GlobalTranslator and install it in the
    cbpos namespace with the gettext translators for the respective
    modules.
    """
    
    def __init__(self, localedir=None, languages=None, class_=None, fallback=None, codeset=None):
        self.tr = GlobalTranslator()
        
        self.localedir = localedir
        self.languages = languages
        self.class_ = class_
        self.fallback = fallback
        self.codeset = codeset
    
    def add(self, module_name, domain=None, localedir=None, languages=None, class_=None, fallback=True, codeset=None):
        """
        Create and regitser a module translator to the global translator
        given the appropriate parameters for the gettext translator.
        """
        module_tr = ModuleTranslator(domain=domain if domain is not None else self.default_domain(module_name),
                                     localedir=localedir if localedir is not None else self.localedir,
                                     languages=languages if languages is not None else self.languages,
                                     class_=class_ if class_ is not None else self.class_,
                                     fallback=fallback if fallback is not None else self.fallback,
                                     codeset=codeset if codeset is not None else self.codeset)
        self.register(module_name, module_tr)
    
    def add_main(self):
        """
        Create and register a default translator to the global translator
        using the default parameters passed on creation of the class.
        """
        main_tr = ModuleTranslator(domain="coinbox_main",
                                   localedir=self.localedir,
                                   languages=self.languages,
                                   class_=self.class_,
                                   fallback=self.fallback,
                                   codeset=self.codeset)
        self.register_main(main_tr)
    
    def install(self):
        """
        Install the global translator object to the main package as "cbpos.tr"
        """
        self.add_main()
        cbpos.tr = self.tr
    
    def default_domain(self, module_name):
        """
        Returns the default gettext domain name for modules 
        """
        return 'coinbox_mod_%s' % (module_name,)
    
    def register(self, module_name, translator):
        """
        Adds a translator entry to the global translator for a module under "tr.{mod_name}_"
        """
        setattr(self.tr, module_name + '_', translator)
    
    def register_main(self, translator):
        """
        Adds a translator entry to the global translator for the main translator under "tr._"
        """
        setattr(self.tr, '_', translator)

class DummyTranslatorBuilder(TranslatorBuilder):
    """
    A dummy translator builder which generates a global translator that only returns the same input.
    """
    def dummy_gettext(self, message):
        return message

    def add(self, module_name, domain=None, localedir=None, languages=None, class_=None, fallback=True, codeset=None):
        self.register(module_name, self.dummy_gettext)
    
    def add_main(self):
        self.register_main(self.dummy_gettext)

class GlobalTranslator(object):
    pass

class ModuleTranslator(object):
    """
    A proxy to the appropriate gettext function call for translation.
    """
    def __init__(self, domain, localedir=None, languages=None, class_=None, fallback=None, codeset=None):
        self.translation = gettext.translation(domain, localedir, languages, class_, fallback, codeset)
    
    def __call__(self, message):
        return self.translation.ugettext(message)
