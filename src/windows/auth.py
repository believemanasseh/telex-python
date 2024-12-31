"""Application's entry window class. Contains authentication/authorisation logic.

This module provides:
- AuthWindow: base window class for authentication
"""

import os

import gi

gi.require_versions({"Adw": "1", "Gtk": "4.0", "WebKit": "6.0"})

from http import HTTPStatus

from gi.repository import Adw, Gtk, WebKit

from utils.common import add_style_context, load_css, load_image
from utils.services import AWSClient, Reddit

from .home import HomeWindow


class AuthWindow(Gtk.ApplicationWindow):
	"""Window class for authentication and authorization."""

	__gtype_name__ = "AuthWindow"

	def __init__(self, application, **kwargs) -> None:
		"""Initialises authentication window.

		Create and style login/register buttons
		"""
		self.css_provider = load_css("/assets/styles/auth.css")

		start_box = Gtk.Box(halign=True, orientation=Gtk.Orientation.HORIZONTAL)
		start_box.append(
			Gtk.Button(icon_name="xyz.daimones.Telex.reload", tooltip_text="Reload")
		)

		end_box = Gtk.Box(halign=True, orientation=Gtk.Orientation.HORIZONTAL)
		end_box.append(
			Gtk.Button(icon_name="xyz.daimones.Telex.search", tooltip_text="Search")
		)

		popover_child = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		grid = Gtk.Grid()
		grid.insert_row(0)
		grid.insert_column(0)
		grid.insert_column(1)

		user_profile_img = load_image(
			"/assets/images/reddit-placeholder.png",
			"placeholder",
			css_classes=["user-profile-img"],
		)
		add_style_context(user_profile_img, self.css_provider)
		grid.attach(user_profile_img, 0, 0, 50, 50)

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		box.append(Gtk.Label(label="u/believemanasseh"))
		box.append(Gtk.Label(label="38 karma"))
		grid.attach(box, 1, 0, 100, 100)

		popover_child.append(grid)

		menu_labels = ["View Profile", "Preferences", "Log Out"]
		for label in menu_labels:
			menu_btn = Gtk.Button(
				label=label,
				css_classes=["menu-btn"],
				hexpand=True,
				width_request=200,
			)
			add_style_context(menu_btn, self.css_provider)
			popover_child.append(menu_btn)

		end_box.append(
			Gtk.MenuButton(
				icon_name="xyz.daimones.Telex.profile",
				tooltip_text="Profile",
				popover=Gtk.Popover(child=popover_child),
			)
		)

		header_bar = Gtk.HeaderBar(decoration_layout="close,maximize,minimize")
		header_bar.pack_start(start_box)
		header_bar.pack_end(end_box)

		super().__init__(
			application=application,
			default_height=600,
			default_width=600,
			title="Telex",
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
		add_style_context(self.reddit_btn, self.css_provider)
		self.box.append(self.reddit_btn)
		self.reddit_btn.connect("clicked", self.__on_render_page)

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
				self.box.set_visible(False)

				home_window = HomeWindow(base_window=self, api=self.reddit_api)
				home_window.render_page()

	def __on_close_webview(self, _widget: WebKit.WebView) -> None:
		"""Handler for WebView widget's close event."""
		self.box.set_opacity(1.0)

	def __on_render_page(self, _widget: Gtk.Widget) -> None:
		"""Renders oauth page.

		Authorisation request on-behalf of application user.
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
