from .home import HomeWindow as HomeWindow
from _typeshed import Incomplete
from gi.repository import Gtk

class AuthWindow(Gtk.ApplicationWindow):
    __gtype_name__: str
    reddit_api: Incomplete
    azure_client: Incomplete
    box: Incomplete
    reddit_btn: Incomplete
    def __init__(self, application, **kwargs) -> None: ...
    dialog: Incomplete
    def on_render_page(self, _widget: Gtk.Widget): ...
