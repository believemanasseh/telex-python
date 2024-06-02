"""Copyright 2022 believemanasseh.

Window class for app's homepage
"""

import gi

gi.require_version("Gtk", "4.0")


from gi.repository import Gtk


class HomeWindow:
	"""Base class for homepage."""

	def __init__(self, base_window: Gtk.ApplicationWindow, base_box: Gtk.Box):
		"""Maximises base application window and styles base box widget."""
		self.base = base_window
		self.box = base_box
		self.css_provider = Gtk.CssProvider()
		self.css_provider.load_from_data(
			"""
			.box {
				padding: 30px 0px;
			}

			.post-container {
				background-color: #a3a2a0;
				color: #000000;
				border-radius: 15px;
			}
		"""
		)
		self.box.set_valign(Gtk.Align.START)
		self.box.get_style_context().add_provider(
			self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)
		self.base.maximize()

	def render_page(self):
		"""Renders homepage."""
		post_container = Gtk.Box(
			css_classes=["post-container"],
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=10,
			width_request=800,
			height_request=150,
			halign=Gtk.Align.CENTER,
			valign=Gtk.Align.CENTER,
		)
		post_container.get_style_context().add_provider(
			self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)
		self.box.append(post_container)
