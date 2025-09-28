"""Copyright 2022.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

SPDX-License-Identifier: GPL-3.0-or-later
"""

import asyncio
import logging
import sys
from collections.abc import Callable
from typing import Any

import gi
from dotenv import load_dotenv

import store

gi.require_versions({"Gtk": "4.0", "Adw": "1", "Gio": "2.0", "GLib": "2.0"})

from gi.events import GLibEventLoopPolicy
from gi.repository import Adw, GLib, Gio, Gtk

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("telex.log")],
)


class Telex(Adw.Application):
	"""The main application singleton class."""

	def __init__(self) -> None:
		"""Initialises application and signal handlers.

		Creates the main application instance, sets up the GLib event loop
		policy, and registers application actions. The application is
		designed to be a singleton, ensuring only one instance runs at a time.

		Attributes:
			loop (asyncio.AbstractEventLoop): The event loop for the application
		"""
		super().__init__(
			application_id="xyz.daimones.Telex",
			flags=Gio.ApplicationFlags.FLAGS_NONE,
		)
		self.create_action("quit", self.on_quit_action, ["<primary>q"])
		self.create_action("about", self.on_about_action, ["<primary>a"])
		self.create_action("prefs", self.on_prefs_action, ["<primary>p"])

		logging.info("Setting GLib event loop policy")
		policy = GLibEventLoopPolicy()
		asyncio.set_event_loop_policy(policy)
		self.loop = policy.get_event_loop()

		# Get style manager and set initial theme
		self.settings = Gio.Settings("xyz.daimones.Telex")
		style_manager = Adw.StyleManager.get_default()
		style_manager.connect(
			"notify::dark",
			lambda _, __: self.__update_container_styles(style_manager.get_dark()),
		)
		if self.settings.get_boolean("dark-mode"):
			style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
		else:
			style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

	def do_activate(self):
		"""Called when the application is activated.

		We raise the application's main window, creating it if
		necessary.

		Returns:
			None: This method does not return a value.
		"""
		win = self.props.active_window
		if not win:
			from windows.auth import AuthWindow

			win = AuthWindow(application=self)
		win.present()

	def on_quit_action(
		self, _action: Gio.SimpleAction, _param: GLib.Variant | None = None
	) -> None:
		"""Callback for app.quit action.

		Called when the quit action is triggered through the UI or keyboard shortcut.

		Args:
			_action: The Gio.SimpleAction that was activated
			_param: Parameter passed to the action

		Returns:
			None: This method does not return a value.
		"""
		self.quit()

	def on_about_action(
		self, widget: Gio.SimpleAction | Gtk.Button, _param: GLib.Variant | None = None
	) -> None:
		"""Callback for the app.about action.

		Creates and displays the application's about dialog.

		Args:
			widget: The widget that triggered the action
			_param: Parameter passed to the action

		Returns:
			None: This method does not return a value.
		"""
		if isinstance(widget, Gtk.Button):
			widget.set_sensitive(False)

		about = Gtk.AboutDialog(
			version="0.1.0",
			authors=["Illucid Mind"],
			program_name="Telex",
			comments="A modern Reddit client",
			copyright="© 2025 Illucid Mind",
			license_type=Gtk.License.GPL_3_0,
			website="https://telex.diamones.xyz",
			logo_icon_name="xyz.daimones.Telex.logo",
		)
		about.present()

		if isinstance(widget, Gtk.Button):
			about.connect("close-request", lambda _: widget.set_sensitive(True))

	def on_prefs_action(
		self, _action: Gio.SimpleAction, _param: GLib.Variant | None = None
	) -> None:
		"""Callback for the app.prefs action.

		Creates and displays the application's preferences window.

		Args:
			_action: The Gio.SimpleAction that was activated
			_param: Parameter passed to the action

		Returns:
			None: This method does not return a value.
		"""
		from windows.preferences import PreferencesWindow

		prefs_window = PreferencesWindow(
			transient_for=self.props.active_window, settings=self.settings
		)
		prefs_window.present()

	def __update_container_styles(self, is_dark: bool) -> None:
		"""Update post container styles based on theme.

		Updates the CSS classes of post containers to match the current theme
		by toggling between 'post-container' and 'post-container-dark'.

		Args:
			is_dark (bool): Whether the current theme is dark mode or not.

		Returns:
			None: This method does not return a value.
		"""
		if store.auth_window:
			logging.info("Updating auth window styles")
			for child in store.auth_window.box.observe_children():
				if isinstance(child, Gtk.Button):
					current_classes = child.get_css_classes()
					if any(cls.startswith("reddit-btn") for cls in current_classes):
						child.remove_css_class("reddit-btn")
						child.remove_css_class("reddit-btn-dark")
						child.add_css_class(
							"reddit-btn-dark" if is_dark else "reddit-btn"
						)

		if store.home_window:
			logging.info("Updating home window styles")
			for child in store.home_window.box.observe_children():
				if isinstance(child, Gtk.Box):
					current_classes = child.get_css_classes()
					if any(cls.startswith("post-container") for cls in current_classes):
						child.remove_css_class("post-container")
						child.remove_css_class("post-container-dark")
						child.add_css_class(
							"post-container-dark" if is_dark else "post-container"
						)

		if store.post_detail_window:
			logging.info("Updating post detail window styles")
			for child in store.post_detail_window.box.observe_children():
				if isinstance(child, Gtk.Box):
					current_classes = child.get_css_classes()
					if any(cls.startswith("post-container") for cls in current_classes):
						child.remove_css_class("post-container")
						child.remove_css_class("post-container-dark")
						child.add_css_class(
							"post-container-dark" if is_dark else "post-container"
						)

					if any(cls.startswith("comment-box") for cls in current_classes):
						child.remove_css_class("comment-box")
						child.remove_css_class("comment-box-dark")
						child.add_css_class(
							"comment-box-dark" if is_dark else "comment-box"
						)

					if any(cls.startswith("comment-score") for cls in current_classes):
						child.remove_css_class("comment-score")
						child.remove_css_class("comment-score-dark")
						child.add_css_class(
							"comment-score-dark" if is_dark else "comment-score"
						)

		if store.profile_window:
			logging.info("Updating profile window styles")
			for child in store.profile_window.tabs_hbox.observe_children():
				current_classes = child.get_css_classes()
				if isinstance(child, Gtk.Label) and any(
					cls.startswith("profile-tab") for cls in current_classes
				):
					child.remove_css_class("profile-tab")
					child.remove_css_class("profile-tab-dark")
					child.add_css_class("profile-tab-dark" if is_dark else "profile-tab")

			for child in store.profile_window.main_content.observe_children():
				current_classes = child.get_css_classes()
				if any(cls.startswith("post-item") for cls in current_classes):
					child.remove_css_class("post-item")
					child.remove_css_class("post-item-dark")
					child.add_css_class("post-item-dark" if is_dark else "post-item")

				if any(cls.startswith("comment-item") for cls in current_classes):
					child.remove_css_class("comment-item")
					child.remove_css_class("comment-item-dark")
					child.add_css_class(
						"comment-item-dark" if is_dark else "comment-item"
					)

	def create_action(
		self,
		name: str,
		callback: Callable[[Any, Any], None],
		shortcuts: list | None = None,
	) -> None:
		"""Add an application action.

		Creates a new Gio.SimpleAction, connects it to a callback function,
		and adds it to the application with optional keyboard shortcuts.

		Args:
			name: The name of the action
			callback: The function to be called when the action is activated
			shortcuts: Optional list of keyboard accelerators (e.g. ["<primary>q"])

		Returns:
			None: This method does not return a value.
		"""
		action = Gio.SimpleAction.new(name, None)
		action.connect("activate", callback)
		self.add_action(action)
		if shortcuts:
			self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version) -> int:
	"""The application's entry point.

	Creates and runs the main Telex application.

	Args:
		version: The version of the application

	Returns:
		int: The application exit code
	"""
	load_dotenv()
	logging.info("Starting Telex application")
	logging.info("Version: %s", version)
	logging.info("Python version: %s", sys.version)
	logging.info(
		"GTK version: %d.%d.%d",
		Gtk.get_major_version(),
		Gtk.get_minor_version(),
		Gtk.get_micro_version(),
	)
	logging.info("PyGObject version: %s", gi.__version__)

	app = Telex()
	return app.run(sys.argv)


if __name__ == "__main__":
	main("0.1.0")
