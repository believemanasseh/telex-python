"""Copyright 2022 believemanasseh.

Application's entry window class. Contains authentication/authorisation logic.
"""

import os

import gi

gi.require_versions({"Gtk": "4.0", "WebKit": "6.0"})
from http import HTTPStatus

from gi.repository import Adw, Gtk, WebKit

from utils.common import add_style_context, load_css
from utils.services import AWSClient, Reddit

from .home import HomeWindow


class AuthWindow(Gtk.ApplicationWindow):
	"""Window class for authentication and authorization."""

	__gtype_name__ = "AuthWindow"

	def __init__(self, application, **kwargs) -> None:
		"""Initialises authentication window.

		Create and style login/register buttons
		"""
		start_box = Gtk.Box(halign=True, orientation=Gtk.Orientation.HORIZONTAL)
		start_box.append(
			Gtk.Button(icon_name="xyz.daimones.Telex.reload", tooltip_text="Reload")
		)

		end_box = Gtk.Box(halign=True, orientation=Gtk.Orientation.HORIZONTAL)
		end_box.append(
			Gtk.Button(icon_name="xyz.daimones.Telex.search", tooltip_text="Search")
		)
		end_box.append(
			Gtk.Button(icon_name="xyz.daimones.Telex.profile", tooltip_text="Profile")
		)

		header_bar = Gtk.HeaderBar(decoration_layout="close,maximize,minimize")
		header_bar.pack_start(start_box)
		header_bar.pack_end(end_box)

		super().__init__(
			application=application,
			default_height=600,
			default_width=600,
			title="",
			titlebar=header_bar,
			icon_name="reddit-icon",
			**kwargs,
		)

		self.reddit_api = Reddit()
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
		css_provider = load_css("/assets/styles/auth.css")
		add_style_context(self.reddit_btn, css_provider)
		self.box.append(self.reddit_btn)
		self.reddit_btn.connect("clicked", self.on_render_page)

	def __on_load_changed(self, widget: WebKit.WebView, event: WebKit.LoadEvent) -> None:
		"""Handler for uri load change signals.

		Args:
		  widget: web view instance
		  event: on_load event
		"""
		uri = widget.get_uri()

		# Retrieve access token
		if "code=" in uri and event == WebKit.LoadEvent.FINISHED:
			widget.set_visible(False)  # closes the WebView widget
			start_index = uri.index("code=") + len("code=")
			end_index = uri.index("#")
			auth_code = uri[start_index:end_index]
			res = self.reddit_api.generate_access_token(auth_code)

			if res["status_code"] == HTTPStatus.OK:
				access_token = res["json"]["access_token"]
				self.reddit_api.inject_token(access_token)
				self.aws_client.create_secret("telex-access-token", access_token)

				self.dialog.close()
				self.box.remove(self.reddit_btn)
				self.box.set_opacity(1.0)
				self.box.set_visible(False)

				home_window = HomeWindow(base_window=self, api=self.reddit_api)
				home_window.render_page()

	def on_render_page(self, _widget: Gtk.Widget) -> None:
		"""Renders oauth page.

		Authorisation request on-behalf of application user.
		"""
		self.dialog = Adw.MessageDialog(
			transient_for=self,
			default_height=400,
			default_width=400,
			visible=True,
			titlebar=Adw.HeaderBar(show_title=False),
		)
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
