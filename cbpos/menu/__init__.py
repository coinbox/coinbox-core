import cbpos

from .root import MenuRoot
from .item import MenuItem
from .menu import Menu

cbpos.config.set_default('menu', 'show_empty_root_items', '')
cbpos.config.set_default('menu', 'show_disabled_items', '')

main = None

def init():
    """
    Create the main Menu instance to be used in the main frame.
    """
    global main
    main = Menu()
