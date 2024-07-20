"""Copyright 2022 believemanasseh.

Window class for app's homepage
"""

import gi

gi.require_version("Gtk", "4.0")


from gi.repository import Gtk

from utils.common import load_css, load_image


class HomeWindow:
	"""Base class for homepage."""

	def __init__(self, base_window: Gtk.ApplicationWindow, base_box: Gtk.Box):
		"""Maximises base application window and styles base box widget."""
		self.base = base_window
		self.box = base_box
		self.css_provider = load_css("/assets/styles/home.css")
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

		likes_count = Gtk.Label(label=6000, css_classes=["likes-count"])
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
		post_image = load_image(
			"/assets/images/light.jpg", "Light", ["post-image"], self.css_provider
		)
		post_image_box.append(post_image)

		post_container.append(post_image_box)

		# Add post title and necessary metadata
		post_detail_box = Gtk.Box(css_classes=["post-detail-box"])
		post_title = Gtk.Text(text="Post Title", css_classes=["post-title"])
		post_title.get_style_context().add_provider(
			self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)
		post_detail_box.append(post_title)
		post_container.append(post_detail_box)
