"""New Post dialog implementation for Telex application.

The module provides a dialog window for creating new posts in the Telex
application, allowing users to input text, upload images, or add links.
It includes input validation, file selection, and dynamic UI updates.

Features:
- Title and body text input
- Image upload and preview
- Link input
- Tabbed interface for different post types

Classes:
	NewPostDialog: Main dialog class for creating new posts
"""

import gi

from utils.common import add_style_contexts, load_css

gi.require_versions(
	{"Adw": "1", "Gio": "2.0", "GObject": "2.0", "Gtk": "4.0", "Pango": "1.0"}
)

from gi.repository import Adw, Gtk, Pango

MAX_CHAR = 300


class NewPostDialog(Adw.Dialog):
	"""New Post dialog for Telex application."""

	def __init__(self, **kwargs):
		"""Initialise the New Post dialog."""
		super().__init__(**kwargs)

		self.css_provider = load_css("/assets/styles/new_post.css")
		self.media_list = []
		self.media = []

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
				margin_bottom=30,
				vexpand=True,
			)
			box = Gtk.Box(margin_top=20)
			title_label = Gtk.Label(
				label="Title",
				halign=Gtk.Align.START,
				css_classes=["title-label"],
			)
			asterisk_label = Gtk.Label(
				label="*", css_classes=["asterisk-label"], margin_bottom=5
			)
			box.append(title_label)
			box.append(asterisk_label)
			buffer = Gtk.TextBuffer()
			buffer.connect("insert-text", self.__on_insert_text)
			text_widget = Gtk.TextView(
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
			child_box.append(box)
			child_box.append(text_widget)

			if label in {"Text", "Link"}:
				# Add body text and link input field
				box = Gtk.Box(margin_top=20)
				body_link_label = Gtk.Label(
					label="Body text (optional)" if label == "Text" else "Link URL",
					halign=Gtk.Align.START,
					css_classes=["body-label"],
				)
				box.append(body_link_label)
				if label == "Link":
					asterisk_label = Gtk.Label(
						label="*", css_classes=["asterisk-label"], margin_bottom=5
					)
					box.append(asterisk_label)

				buffer = Gtk.TextBuffer()

				body_widget = Gtk.TextView(
					buffer=buffer,
					css_classes=["body-input"],
					width_request=500,
					wrap_mode=Gtk.WrapMode.CHAR,
					left_margin=5,
					top_margin=5,
					right_margin=5,
					bottom_margin=5,
				)

				clamp = Adw.Clamp(
					child=body_widget,
					maximum_size=250,
					orientation=Gtk.Orientation.VERTICAL,
				)
				viewport = Gtk.Viewport(child=clamp)
				scrolled_window = Gtk.ScrolledWindow(
					child=viewport,
					hscrollbar_policy=Gtk.PolicyType.NEVER,
					vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
					height_request=250 if label == "Text" else 30,
				)

				child_box.append(box)
				child_box.append(scrolled_window)
			else:
				parent = Gtk.Window()
				button = Gtk.Button(label="Choose File…", margin_top=10, margin_bottom=10)
				button.connect("clicked", self.__on_upload_clicked, parent, child_box)
				child_box.append(button)

			notebook.append_page(
				child=child_box,
				tab_label=Gtk.Label(label=label),
			)

			add_style_contexts(
				[text_widget, title_label, asterisk_label, body_widget, body_link_label],
				self.css_provider,
			)

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

		Limits the number of characters in the title input field to MAX_CHAR.

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

	def __on_upload_clicked(
		self, _button: Gtk.Button, parent: Gtk.Window, child_box: Gtk.Box
	):
		"""Handles file upload button click event.

		Opens a file chooser dialog to select a file.

		Args:
			_button (Gtk.Button): The button that was clicked
			parent (Gtk.Window): The parent window for the file chooser dialog
			child_box (Gtk.Box): The box to add the selected image preview

		Returns:
			None: This method does not return a value.
		"""
		dialog = Gtk.FileChooserNative(
			title="Select a file",
			transient_for=parent,
			action=Gtk.FileChooserAction.OPEN,
			accept_label="_Open",
			cancel_label="_Cancel",
		)
		dialog.connect("response", self.__on_file_dialog_response, child_box)
		dialog.show()

	def __on_file_dialog_response(
		self, dialog: Gtk.FileChooserNative, response: int, child_box: Gtk.Box
	):
		"""Handles file chooser dialog response event.

		If the user accepted the dialog, retrieves the selected file path and
		displays a preview of the image in the provided box.

		Args:
			dialog (Gtk.FileChooserNative): The file chooser dialog
			response (int): The response ID from the dialog
			child_box (Gtk.Box): The box to add the selected image preview

		Returns:
			None: This method does not return a value.
		"""
		if response == Gtk.ResponseType.ACCEPT:
			filename = dialog.get_file().get_path()
			if filename:
				picture_clamp = Adw.Clamp(maximum_size=40)
				picture = Gtk.Picture.new_for_filename(filename)
				picture.set_halign(Gtk.Align.START)
				picture.set_valign(Gtk.Align.CENTER)
				picture.set_content_fit(Gtk.ContentFit.CONTAIN)
				picture_clamp.set_child(picture)

				label = Gtk.Label(
					label=filename.split("/")[-1],
					hexpand=True,
					halign=Gtk.Align.CENTER,
					ellipsize=Pango.EllipsizeMode.END,
					max_width_chars=30,
				)

				delete_btn = Gtk.Button(
					icon_name="xyz.daimones.Telex.delete",
					halign=Gtk.Align.END,
				)
				delete_btn.connect(
					"clicked",
					lambda _btn: (
						child_box.remove(lbr),
						self.media.remove(filename),
						self.media_list.remove(lbr),
					),
				)

				box = Gtk.Box(
					orientation=Gtk.Orientation.HORIZONTAL,
					spacing=6,
					margin_top=6,
					margin_bottom=6,
					margin_start=6,
					margin_end=6,
				)
				box.append(picture_clamp)
				box.append(label)
				box.append(delete_btn)

				lbr = Gtk.ListBoxRow()
				lbr.set_child(box)

				self.media_list.append(lbr)
				self.media.append(filename)

				for media in self.media_list:
					child_box.append(media)

		dialog.destroy()
