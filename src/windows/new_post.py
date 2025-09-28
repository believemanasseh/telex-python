"""New post window module for the Telex application.

This module provides:
- NewPostWindow: Main window for creating new Reddit post.
"""

import gi

gi.require_versions({"Adw": "1", "Gio": "2.0", "GObject": "2.0", "Gtk": "4.0"})

from gi.repository import Adw, Gtk


class NewPostDialog(Adw.Dialog):
	"""New Post window for Telex application."""

	def __init__(self, **kwargs):
		"""Initialise the New Post window."""
		super().__init__(**kwargs)

		# Set dialog properties
		self.set_content_height(500)
		self.set_content_width(600)
		self.set_title("New Post")

		notebook = Gtk.Notebook(page=0)

		# Insert tab page for texts
		text_child = Gtk.Box(vexpand=True, halign=Gtk.Align.CENTER)
		text_child.append(Gtk.Label(label="Texts will be here"))
		notebook.append_page(
			child=text_child,
			tab_label=Gtk.Label(label="Text"),
		)

		# Insert tab page for images
		image_child = Gtk.Box(vexpand=True, halign=Gtk.Align.CENTER)
		image_child.append(Gtk.Label(label="Images will be here"))
		notebook.append_page(
			child=image_child,
			tab_label=Gtk.Label(label="Images"),
		)

		# Insert tab page for links
		link_child = Gtk.Box(vexpand=True, halign=Gtk.Align.CENTER)
		link_child.append(Gtk.Label(label="Links will be here"))
		notebook.append_page(child=link_child, tab_label=Gtk.Label(label="Link"))

		button = Gtk.Button(
			icon_name="xyz.daimones.Telex.close",
			halign=Gtk.Align.END,
			margin_end=5,
			margin_top=5,
		)
		button.connect("clicked", lambda _: self.close())

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		box.append(button)
		box.append(notebook)

		self.set_child(box)
