"""Application's entry window class. Contains authentication/authorisation logic.

This module provides:
- AuthWindow: base window class for authentication
"""

import os
from http import HTTPStatus

import gi
from gi.repository import Adw, Gtk, WebKit

from services import AWSClient, Reddit
from utils.common import add_style_context, load_css

gi.require_versions({"Adw": "1", "Gtk": "4.0", "WebKit": "6.0"})


class AuthWindow(Gtk.ApplicationWindow):
    """Window class for authentication and authorization."""

    __gtype_name__ = "AuthWindow"

    def __init__(self, application, **kwargs) -> None:
        """Initialises authentication window."""
        self.css_provider = load_css("/assets/styles/auth.css")

        self.header_bar = Adw.HeaderBar(
            decoration_layout="close,maximize,minimize", show_back_button=True
        )

        super().__init__(
            application=application,
            default_height=600,
            default_width=600,
            title="Telex",
            titlebar=self.header_bar,
            icon_name="reddit-icon",
            **kwargs,
        )
        self.api = Reddit()
        self.aws_client = AWSClient()
        self.box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=20,
            css_classes=["box"],
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
        )
        self.set_child(self.box)
        self.reddit_btn = Gtk.Button(
            label="Continue with Reddit",
            name="reddit-btn",
            css_classes=["reddit-btn"],
            width_request=200,
        )
        add_style_context(self.reddit_btn, self.css_provider)
        self.box.append(self.reddit_btn)
        self.reddit_btn.connect("clicked", self.__on_render_page)

    def __on_load_changed(
        self, widget: WebKit.WebView, event: WebKit.LoadEvent
    ) -> None:
        """Handler for URI load change signals.

        Processes the authorization callback from Reddit's OAuth flow.
        When the authorization code is received, it exchanges it for an access token,
        stores the token, and initializes the home window.

        Args:
            widget (WebKit.WebView): The web view instance handling the OAuth flow
            event (WebKit.LoadEvent): The load event type that triggered this handler
        """
        from windows.home import HomeWindow

        uri = widget.get_uri()

        # Retrieve access token
        if "code=" in uri and event == WebKit.LoadEvent.FINISHED:
            widget.set_visible(False)  # closes the WebView widget
            start_index = uri.index("code=") + len("code=")
            end_index = uri.index("#")
            auth_code = uri[start_index:end_index]
            res = self.api.generate_access_token(auth_code)

            if res["status_code"] == HTTPStatus.OK:
                access_token = res["json"]["access_token"]
                self.api.inject_token(access_token)
                self.aws_client.create_secret("telex-access-token", access_token)

                self.dialog.close()

                self.box.remove(self.reddit_btn)
                self.box.set_visible(False)

                home_window = HomeWindow(base_window=self, api=self.api)
                home_window.render_page()

    def __on_close_webview(self, _widget: WebKit.WebView) -> None:
        """Handler for WebView widget's close event.

        Restores the opacity of the main authorization box when the
        WebView dialog is closed.

        Args:
            _widget (WebKit.WebView): The web view that was closed
        """
        self.box.set_opacity(1.0)

    def __on_render_page(self, _widget: Gtk.Widget) -> None:
        """Renders OAuth page for Reddit authorization.

        Creates a dialog with a WebView that loads Reddit's OAuth page,
        allowing the user to authorize the application to access their
        Reddit account.

        Args:
            _widget (Gtk.Widget): The button widget that triggered this handler
        """
        self.dialog = Gtk.MessageDialog(
            transient_for=self,
            default_height=400,
            default_width=400,
            visible=True,
            titlebar=Adw.HeaderBar(),
        )
        self.dialog.connect("close-request", self.__on_close_webview)

        uri = WebKit.URIRequest(uri=os.getenv("AUTHORISATION_URL", ""))
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
