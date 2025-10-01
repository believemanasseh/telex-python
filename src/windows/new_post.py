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

import store

gi.require_versions(
	{"Adw": "1", "Gio": "2.0", "GObject": "2.0", "Gtk": "4.0", "Pango": "1.0"}
)

from gi.repository import Adw, Gtk, Pango

from services import Reddit
from utils.common import add_style_contexts, load_css, load_image

MAX_CHAR = 300


class NewPostDialog(Adw.Dialog):
	"""New Post dialog for Telex application."""

	from app import Telex

	def __init__(self, api: Reddit):
		"""Initialise the New Post dialog.

		Args:
			api (Reddit): Instance of Reddit API handler

		Attributes:
			api (Reddit): Instance of Reddit API handler
			css_provider (Gtk.CssProvider): CSS provider for styling
			media_list (list): List of media file widgets
			media (list): List of media file paths
			subreddits (dict | None): Subreddit data fetched from Reddit API
			subreddit_boxes (list): List of subreddit box widgets for filtering
			spinner (Gtk.Spinner): Spinner widget for loading indication
			menu_btn (Gtk.MenuButton | None): Menu button for subreddit selection
			menu_label (Gtk.Label | None): Label displaying selected subreddit
		"""
		super().__init__()
		self.api = api
		self.css_provider = load_css("/assets/styles/new_post.css")
		self.media_list = []
		self.media = []
		self.subreddits = None
		self.subreddit_boxes = []
		self.menu_btn = None
		self.menu_label = None

		# Set dialog properties
		self.set_content_height(500)
		self.set_content_width(600)
		self.set_title("New Post")
		self.spinner = Gtk.Spinner(
			spinning=True, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER
		)
		self.set_child(self.spinner)

	async def fetch_data(self) -> None:
		"""Retrieves subreddits the user is subscribed to.

		Returns:
			dict[str, int | dict] | None: Response containing status code and listing data
		"""
		return await self.api.retrieve_subreddits()

	def add_input_fields(self, notebook: Gtk.Notebook) -> None:
		"""Adds input fields to the notebook for different post types.

		Creates and configures input fields for title, body text, image upload,
		and link URL, and adds them to the provided notebook.

		Args:
			notebook (Gtk.Notebook): The notebook to add input fields to

		Returns:
			None: This method does not return a value.
		"""
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

	def add_popover_child(self) -> Gtk.Box:
		"""Creates and returns the popover child widget.

		Returns:
			Gtk.Box: The box containing the popover content
		"""
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			margin_top=10,
			margin_bottom=10,
			margin_start=10,
			margin_end=10,
			spacing=6,
		)

		buffer = Gtk.EntryBuffer()
		buffer.connect("inserted-text", self.__on_inserted_text)
		buffer.connect("deleted-text", self.__on_deleted_text)
		entry = Gtk.Entry(
			buffer=buffer,
			placeholder_text="Search",
			css_classes=["search-entry"],
			width_request=300,
			primary_icon_name="xyz.daimones.Telex.search",
		)
		box.append(entry)

		listbox = Gtk.ListBox()

		for subreddit in self.subreddits["json"]["data"]["children"]:
			row = Gtk.ListBoxRow()
			subreddit_box = Gtk.Box(
				orientation=Gtk.Orientation.HORIZONTAL,
				halign=Gtk.Align.CENTER,
				spacing=10,
			)
			subreddit_icon = load_image(
				"/assets/images/reddit-placeholder.png",
				"Subreddit placeholder",
				css_classes=["subreddit-icon"],
				css_provider=self.css_provider,
			)
			vbox = Gtk.Box(
				orientation=Gtk.Orientation.VERTICAL, valign=Gtk.Align.CENTER, spacing=6
			)
			subreddit_title = Gtk.Label(
				label=subreddit["data"]["title"], halign=Gtk.Align.START
			)
			subreddit_name = Gtk.Label(
				label=subreddit["data"]["display_name_prefixed"],
				halign=Gtk.Align.START,
			)
			vbox.append(subreddit_title)
			vbox.append(subreddit_name)
			subreddit_box.append(subreddit_icon)
			subreddit_box.append(vbox)
			row.set_child(subreddit_box)
			listbox.append(row)

			# Store references to labels and row for filtering
			subreddit_box.subreddit_title = subreddit_title
			subreddit_box.subreddit_name = subreddit_name
			subreddit_box.row = row
			self.subreddit_boxes.append(subreddit_box)

			click_controller = Gtk.GestureClick()
			click_controller.connect(
				"pressed",
				lambda gesture,
				n_press,
				x,
				y,
				widget=subreddit_box,
				subreddit_name=subreddit["data"][
					"display_name_prefixed"
				]: self.__on_subreddit_box_clicked(
					gesture, n_press, x, y, widget, subreddit_name
				),
			)
			subreddit_box.add_controller(click_controller)

		scrolled_window = Gtk.ScrolledWindow(
			child=listbox,
			hscrollbar_policy=Gtk.PolicyType.NEVER,
			vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
			height_request=150,
			width_request=200,
		)
		box.append(scrolled_window)

		add_style_contexts([entry, listbox], self.css_provider)

		return box

	def __on_subreddit_box_clicked(
		self,
		_gesture: Gtk.GestureClick,
		_n_press: int,
		_x: float,
		_y: float,
		_widget: Gtk.Box,
		subreddit_name: str,
	):
		"""Handles subreddit box click events.

		Sets the current subreddit in the store, updates the MenuButton label,
		and closes the popover.

		Args:
			_gesture (Gtk.GestureClick): The click gesture that triggered the event
			_n_press (int): Number of presses that triggered the event
			_x (float): x-coordinate of the event
			_y (float): y-coordinate of the event
			_widget (Gtk.Box): The post container widget that was clicked
			subreddit_name (str): The name of the subreddit associated with the widget
		"""
		store.current_subreddit = subreddit_name

		# Update the MenuButton label
		if getattr(self, "menu_label", None):
			self.menu_label.set_label(subreddit_name)

		# Close the popover
		if getattr(self, "menu_btn", None):
			pop = self.menu_btn.get_popover()
			if pop:
				pop.popdown()

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

	def __on_inserted_text(
		self,
		entry_buffer: Gtk.EntryBuffer,
		_position: int,
		_chars: str,
		_n_chars: int,
	):
		"""Handles inserted text events for Entry widget.

		Filters subreddit boxes based on the search query in the entry buffer.

		Args:
			entry_buffer (Gtk.EntryBuffer): The buffer that triggered the event
			_position (int): The position to insert text in entrybuffer
			_chars (str): UTF-8 text to be inserted
			_n_chars (int): The length of the inserted text in bytes

		Returns:
			None: This method does not return a value.
		"""
		for box in self.subreddit_boxes:
			title_label = getattr(box, "subreddit_title", None)
			name_label = getattr(box, "subreddit_name", None)
			row = getattr(box, "row", None)
			if not title_label or not name_label or not row:
				continue
			subreddit_title = title_label.get_label().lower()
			subreddit_name = name_label.get_label().lower()
			row.set_visible(
				entry_buffer.get_text().lower() in subreddit_title
				or entry_buffer.get_text().lower() in subreddit_name
			)

	def __on_deleted_text(
		self, entry_buffer: Gtk.EntryBuffer, _position: int, _n_chars: int
	):
		"""Handles deleted text events for Entry widget.

		Shows all subreddit boxes if the entry buffer is empty.

		Args:
			entry_buffer (Gtk.EntryBuffer): The buffer that triggered the event
			_position (int): The position to delete text in entrybuffer
			_n_chars (int): The length of the deleted text in bytes

		Returns:
			None: This method does not return a value.
		"""
		if entry_buffer.get_length() == 1:
			for box in self.subreddit_boxes:
				row = getattr(box, "row", None)
				if not row:
					continue
				row.set_visible(True)

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
		dialog.connect("response", self.__on_response, child_box)
		dialog.show()

	def __on_response(
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

	async def render_page(self) -> None:
		"""Renders the New Post dialog.

		Returns:
			None: This method does not return a value
		"""
		self.present()

		self.subreddits = await self.fetch_data()

		notebook = Gtk.Notebook(page=0)

		self.add_input_fields(notebook)

		button = Gtk.Button(
			icon_name="xyz.daimones.Telex.close",
			halign=Gtk.Align.END,
			margin_end=5,
			margin_top=5,
		)
		button.connect("clicked", lambda _: self.close())

		popover_child = self.add_popover_child()
		self.menu_label = Gtk.Label(label="Select a subreddit")
		self.menu_btn = Gtk.MenuButton(
			child=self.menu_label,
			popover=Gtk.Popover(child=popover_child),
			margin_top=5,
			margin_end=50,
			hexpand=True,
		)

		grid = Gtk.Grid(column_spacing=30)
		grid.insert_row(0)
		grid.insert_column(0)
		grid.insert_column(1)
		grid.insert_column(2)
		grid.insert_column(3)
		grid.attach(Gtk.Label(width_request=50), 0, 0, 1, 1)  # Spacer
		grid.attach(Gtk.Label(width_request=30), 1, 0, 1, 1)  # Spacer
		grid.attach(self.menu_btn, 2, 0, 1, 1)
		grid.attach(button, 3, 0, 1, 1)

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		box.append(grid)
		box.append(notebook)

		self.set_child(box)
