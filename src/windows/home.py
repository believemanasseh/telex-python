"""Copyright 2022 believemanasseh.

Window class for app's homepage
"""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class HomeWindow:
	"""Base class for homepage."""

	def __init__(self, base_window: Gtk.ApplicationWindow):
		"""Maximises base application window."""
		self.base = base_window
		self.base.maximize()

	def render_page(self):
		"""Renders homepage."""
		post_container = Gtk.Box(
			name="post-container",
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=10,
			width_request=800,
			height_request=150,
			halign=Gtk.Align.CENTER,
			valign=Gtk.Align.START,
			hexpand=False,
			vexpand=False,
		)
		css_provider = Gtk.CssProvider()
		css_provider.load_from_data(
			"""
			#post-container {
				background-color: whitesmoke;
				color: #000000;
				margin: 10px 0px;
				border-radius: 15px;
			}
		"""
		)
		post_container.get_style_context().add_provider(
			css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)
		self.base.set_child(post_container)
