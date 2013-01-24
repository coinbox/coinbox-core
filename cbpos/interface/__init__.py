import cbpos

from .root import MenuRoot
from .item import MenuItem
from .menu import Menu

from .action import Action

cbpos.config.set_default('menu', 'show_empty_root_items', '')
cbpos.config.set_default('menu', 'show_disabled_items', '')
