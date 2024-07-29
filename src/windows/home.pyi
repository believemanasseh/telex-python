from _typeshed import Incomplete
from gi.repository import Gtk
from ..utils.services import Reddit 

class HomeWindow:
    base: Incomplete
    box: Incomplete
    api: Incomplete
    cursor: Incomplete
    css_provider: Incomplete
    def __init__(self, base_window: Gtk.ApplicationWindow, base_box: Gtk.Box, api: Reddit) -> None: ...
    def render_page(self) -> None: ...
