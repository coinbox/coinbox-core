hiddenimports = [
    'cbpos.mod.base', 'cbpos.mod.config',
    'cbpos.mod.installer', 'cbpos.mod.auth',
    'cbpos.mod.stock', 'cbpos.mod.currency',
    'cbpos.mod.sales', 'cbpos.mod.customer'
]


def hook(mod):
    import os
    import cbpos
    import cbpos.mod
    mod_path = set(os.path.normcase(os.path.realpath(p)) for p in mod.__path__+cbpos.mod.__path__)
    mod.__path__ = list(mod_path)
    return mod
