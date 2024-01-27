"""Copyright 2022 believemanasseh.

Application's entry window class. Contains logic for login and registration
"""
import os

import gi

gi.require_versions({"Gtk": "4.0", "WebKit": "6.0"})
from http import HTTPStatus

from gi.repository import Gtk, WebKit

from utils.services import Reddit

from .home import HomeWindow


class AuthWindow(Gtk.ApplicationWindow):
    """Authentication window for registration and login."""

    __gtype_name__ = "AuthWindow"

    def __init__(self, application, **kwargs):
        """Initialises authentication window.

        Create and style login/register buttons
        """
        super().__init__(
            application=application,
            title="Telex",
            default_height=600,
            default_width=600,
            icon_name="reddit-icon",
            **kwargs,
        )
        self.reddit_api = Reddit()
        self.dialog = Gtk.Dialog(
            transient_for=self,
            visible=True,
            default_height=400,
            default_width=400,
        )
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
                border: 1px solid #000000;
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

    def __on_load_changed(self, widget: WebKit.WebView, event: WebKit.LoadEvent):
        """Handler for uri load change signals."""
        uri = widget.get_uri()

        def on_change(widget: WebKit.WebView, event: WebKit.LoadEvent):
            if "code=" in uri and event == WebKit.LoadEvent.FINISHED:
                widget.set_visible(False)
                start_index = uri.index("code=") + len("code=")
                end_index = uri.index("#")
                auth_code = uri[start_index:end_index]
                res = self.reddit_api.generate_access_token(auth_code)
                if res["status_code"] == HTTPStatus.OK:
                    self.dialog.close()

        if "login" in uri and event == WebKit.LoadEvent.FINISHED:
            login_uri = WebKit.URIRequest(uri=uri)
            web_view = WebKit.WebView(visible=True)
            web_view.load_request(login_uri)
            web_view.connect("load-changed", on_change)

    def __on_render_homepage(self, _widget: Gtk.Widget, _window: Gtk.Window):
        """Renders homepage window."""
        home_window = HomeWindow()
        home_window.render_page()

    def on_render_page(self, _widget: Gtk.Widget):
        """Renders oauth page.

        Authorisation request on-behalf of application user.
        """
        uri = WebKit.URIRequest(uri=os.getenv("AUTHORISATION_URL"))
        settings = WebKit.Settings(
            allow_modal_dialogs=True,
            enable_fullscreen=False,
            enable_javascript=True,
            enable_media=True,
        )
        web_view = WebKit.WebView(visible=True, settings=settings)
        web_view.connect("load-changed", self.__on_load_changed)
        web_view.load_request(uri)
        self.box.set_opacity(0.5)
        self.dialog.set_child(web_view)
