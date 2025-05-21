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

import logging
import sys
from collections.abc import Callable
from typing import Any

import gi

gi.require_versions({"Gtk": "4.0", "Adw": "1", "Gio": "2.0"})

from gi.repository import Adw, Gio, Gtk

from windows.auth import AuthWindow

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("telex.log")],
)


class Telex(Adw.Application):
	"""The main application singleton class."""

	def __init__(self) -> None:
		"""Initialises application and signal handlers."""
		super().__init__(
			application_id="xyz.daimones.Telex",
			flags=Gio.ApplicationFlags.FLAGS_NONE,
		)
		self.create_action("quit", self.on_quit_action, ["<primary>q"])
		self.create_action("about", self.on_about_action)

	def do_activate(self):
		"""Called when the application is activated.

		We raise the application's main window, creating it if
		necessary.

		Returns:
		    None: This method does not return a value.
		"""
		win = self.props.active_window
		if not win:
			win = AuthWindow(application=self)
		win.present()

	def on_quit_action(self, _action, _param) -> None:
		"""Callback for app.quit action.

		Called when the quit action is triggered through the UI or keyboard shortcut.

		Args:
		    _action: The Gio.SimpleAction that was activated
		    _param: Parameter passed to the action (None in this case)

		Returns:
		    None: This method does not return a value.
		"""
		self.quit()

	def on_about_action(self, _action, _param) -> None:
		"""Callback for the app.about action.

		Creates and displays the application's about dialog.

		Args:
		    _action: The Gio.SimpleAction that was activated
		    _param: Parameter passed to the action (None in this case)

		Returns:
		    None: This method does not return a value.
		"""
		about = Gtk.AboutDialog(version="1.0", authors=["Illucid Mind"])
		about.present()

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


def main(_version) -> int:
	"""The application's entry point.

	Creates and runs the main Telex application.

	Args:
	    _version: The version of the application

	Returns:
	    int: The application exit code
	"""
	logging.info("Starting Telex application")
	logging.info("Version: %s", _version)
	logging.info("Python version: %s", sys.version)
	logging.info("GTK version: %d.%d", Gtk.get_major_version(), Gtk.get_minor_version())
	logging.info("PyGObject version: %s", gi.__version__)
	app = Telex()
	return app.run(sys.argv)


if __name__ == "__main__":
	main("0.1.0")
