"""New post window module for the Telex application.

This module provides:
- NewPostWindow: Main window for creating new Reddit post.
"""

import gi

from utils.common import add_style_contexts, load_css

gi.require_versions({"Adw": "1", "Gio": "2.0", "GObject": "2.0", "Gtk": "4.0"})

from gi.repository import Adw, Gtk

MAX_CHAR = 300


class NewPostDialog(Adw.Dialog):
	"""New Post window for Telex application."""

	def __init__(self, **kwargs):
		"""Initialise the New Post window."""
		super().__init__(**kwargs)

		self.css_provider = load_css("/assets/styles/new_post.css")

		# Set dialog properties
		self.set_content_height(500)
		self.set_content_width(600)
		self.set_title("New Post")

		notebook = Gtk.Notebook(page=0)

		# Add title input field for text, images and link tab pages
		labels = ["Text", "Images", "Link"]
		for label in labels:
			child_box = Gtk.Box(
				halign=Gtk.Align.CENTER,
				orientation=Gtk.Orientation.VERTICAL,
				margin_bottom=0,
			)
			buffer = Gtk.TextBuffer()
			buffer.connect("insert-text", self.__on_insert_text)
			widget = Gtk.TextView(
				buffer=buffer,
				css_classes=["title-input"],
				width_request=500,
				wrap_mode=Gtk.WrapMode.CHAR,
				height_request=30,
				left_margin=5,
				top_margin=5,
				right_margin=5,
				bottom_margin=5,
			)
			title_label = Gtk.Label(
				label="Title:",
				margin_top=10,
				halign=Gtk.Align.START,
				css_classes=["title-label"],
			)
			child_box.append(title_label)
			child_box.append(widget)
			notebook.append_page(
				child=child_box,
				tab_label=Gtk.Label(label=label),
			)

			add_style_contexts([widget, title_label], self.css_provider)

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

	def __on_insert_text(
		self, text_buffer: Gtk.TextBuffer, _location: Gtk.TextIter, _text: str, _len: int
	):
		"""Handles insert text events for TextView widget.

		Sets maximum text length that can be stored in the buffer.

		Args:
			text_buffer (Gtk.TextBuffer): The buffer that triggered the event
			_location (Gtk.TextIter): The position to insert text in textbuffer
			_text (str): UTF-8 text to be inserted
			_len (int): The length of the inserted text in bytes

		Returns:
			None: This method does not return a value.
		"""
		if text_buffer.get_char_count() >= MAX_CHAR:
			text_buffer.stop_emission_by_name("insert-text")
