"""Copyright 2022 believemanasseh.

Application's entry window class. Contains logic for login and registration
"""
import os

from gi.repository import Gio, Gtk

from .home import HomeWindow


class AuthWindow(Gtk.ApplicationWindow):
    """Authentication window for registration and login."""

    __gtype_name__ = "AuthWindow"

    def __init__(self, application, **kwargs):
        """Initialises authentication window.

        Create and style login/register buttons
        """
        super().__init__(application=application, **kwargs)
        self.set_title("Telex")
        self.set_default_size(300, 600)
        self.set_icon_name("reddit-icon")
        self.stack = Gtk.Stack()
        self.box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            width_request=200,
        )
        self.set_child(self.box)
        self.box.set_halign(Gtk.Align.CENTER)
        self.box.set_valign(Gtk.Align.CENTER)
        self.reddit_btn = Gtk.Button(label="Continue with Reddit", name="reddit-btn")
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            """
            #reddit-btn {
                background-color: #FFFFFF;
                color: #000000;
            }
        """
        )
        self.reddit_btn.get_style_context().add_provider(
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
        self.box.append(self.reddit_btn)
        self.stack.add_child(self.box)
        self.reddit_btn.connect("clicked", self.on_render_page)

    def __on_render_homepage(self, _widget: Gtk.Widget, _window: Gtk.Window):
        """Renders homepage window."""
        home_window = HomeWindow()
        home_window.render_page()

    def on_render_page(self, _widget: Gtk.Widget):
        """Renders oauth page.

        Authorisation request on-behalf of application user.
        """
        self.box.set_visible(False)
        cancellable = Gio.Cancellable.new()
        cancellable.connect(self.__on_render_homepage)
        uri_launcher = Gtk.UriLauncher.new(os.getenv("AUTHORISATION_URL"))
        uri_launcher.launch(Gtk.Window.new(), cancellable, self.__on_render_homepage)
