"""Copyright 2022 believemanasseh.

Window class for app's homepage
"""
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class HomeWindow(Gtk.ApplicationWindow):
    """Base class for homepage."""

    def __init__(self, *args, **kwargs):
        """Initialises homepage window."""
        super().__init__(*args, **kwargs)

    def render_page(self):
        """Renders homepage."""
        text = Gtk.Text(text="Welcome to Telex!", css_name="text")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            b"""
            #text {
                background-color: #000000;
                color: #FFFFFF;
            }
        """,
        )
        box.get_style_context().add_provider(
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
        self.set_child(box)
        box.append(text)
        box.set_visible(True)
