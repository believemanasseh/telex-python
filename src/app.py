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

import sys
from collections.abc import Callable
from typing import Any

import gi

gi.require_versions({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Adw, Gio, Gtk

from windows import AuthWindow


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
		self.create_action("preferences", self.on_preferences_action)

	def do_activate(self):
		"""Called when the application is activated.

		We raise the application's main window, creating it if
		necessary.
		"""
		win = self.props.active_window
		if not win:
			win = AuthWindow(application=self)
		win.present()

	def on_quit_action(self, _action, _pspec) -> None:
		"""Callback for app.quit action."""
		self.quit()

	def on_about_action(self, _widget, _) -> None:
		"""Callback for the app.about action."""
		about = Gtk.AboutDialog(version="1.0", authors=["Believe Manasseh"])
		about.present()

	def on_preferences_action(self, _widget, _) -> None:
		"""Callback for the app.preferences action."""

	def create_action(
		self,
		name: str,
		callback: Callable[[Any, Any], None],
		shortcuts: list | None = None,
	) -> None:
		"""Add an application action.

		Args:
		  name: the name of the action
		  callback: the function to be called when the action is activated
		  shortcuts: an optional list of accelerators
		"""
		action = Gio.SimpleAction.new(name, None)
		action.connect("activate", callback)
		self.add_action(action)
		if shortcuts:
			self.set_accels_for_action(f"app.{name}", shortcuts)


def main(_version) -> int:
	"""The application's entry point."""
	app = Telex()
	return app.run(sys.argv)
