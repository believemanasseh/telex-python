"""Copyright 2022 believemanasseh.

Window class for app's homepage
"""

import gi

gi.require_version("Gtk", "4.0")


from gi.repository import Gtk

from utils.common import generate_image, load_css


class HomeWindow:
	"""Base class for homepage."""

	def __init__(self, base_window: Gtk.ApplicationWindow, base_box: Gtk.Box):
		"""Maximises base application window and styles base box widget."""
		self.base = base_window
		self.box = base_box
		self.css_provider = load_css("/src/assets/styles/home.css")
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
		)
		post_container.get_style_context().add_provider(
			self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)
		self.box.append(post_container)

		# Add upvote and downvote buttons to navigation box
		navigation_box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL, spacing=10, css_classes=["icon-box"]
		)
		navigation_box.get_style_context().add_provider(
			self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)

		upvote_btn = Gtk.Button(icon_name="upvote-btn")
		navigation_box.append(upvote_btn)

		likes_count = Gtk.Label(label=7020, css_classes=["likes-count"])
		likes_count.get_style_context().add_provider(
			self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)
		navigation_box.append(likes_count)

		downvote_btn = Gtk.Button(icon_name="downvote-btn")
		navigation_box.append(downvote_btn)

		post_container.append(navigation_box)

		# Add image to post container
		post_image_box = Gtk.Box(
			css_classes=["post-image-box"],
		)
		post_image = generate_image(
			"/src/assets/images/light.jpg", "Light", ["post-image"], self.css_provider
		)
		post_image_box.append(post_image)

		post_container.append(post_image_box)
