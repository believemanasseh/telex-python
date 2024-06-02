"""Copyright 2022 believemanasseh.

Application's entry window class. Contains authentication/authorisation logic.
"""

import os

import gi

gi.require_versions({"Gtk": "4.0", "WebKit": "6.0"})
from http import HTTPStatus

from gi.repository import Gtk, WebKit

from utils.services import Reddit

from .home import HomeWindow


class AuthWindow(Gtk.ApplicationWindow):
	"""Window class for authentication and authorization."""

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
		self.box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=10,
			css_classes=["box"],
			halign=Gtk.Align.CENTER,
			valign=Gtk.Align.CENTER,
		)
		self.set_child(self.box)
		self.reddit_btn = Gtk.Button(
			label="Continue with Reddit", name="reddit-btn", width_request=200
		)
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
		self.reddit_btn.connect("clicked", self.on_render_page)

	def __on_load_changed(self, widget: WebKit.WebView, event: WebKit.LoadEvent):
		"""Handler for uri load change signals.

		Args:
		  widget: web view instance
		  event: on_load event
		"""
		uri = widget.get_uri()

		# Retrieve access token
		if "code=" in uri and event == WebKit.LoadEvent.FINISHED:
			widget.set_visible(False)  # close the WebView widget
			start_index = uri.index("code=") + len("code=")
			end_index = uri.index("#")
			auth_code = uri[start_index:end_index]
			res = self.reddit_api.generate_access_token(auth_code)
			if res["status_code"] == HTTPStatus.OK:
				access_token = res["json"]["access_token"]
				os.environ["ACCESS_TOKEN"] = access_token
				self.dialog.close()
				self.box.remove(self.reddit_btn)
				home_window = HomeWindow(base_window=self, base_box=self.box)
				home_window.render_page()

	def on_render_page(self, _widget: Gtk.Widget):
		"""Renders oauth page.

		Authorisation request on-behalf of application user.
		"""
		self.dialog = Gtk.Dialog(
			transient_for=self, default_height=400, default_width=400, visible=True
		)
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
