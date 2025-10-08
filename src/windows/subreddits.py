import gi

gi.require_versions({"Gtk": "4.0"})


from gi.repository import Gtk

from services import Reddit
from utils import _
from utils.common import (
	add_style_context,
	create_cursor,
	load_css,
	load_image,
	set_current_window,
)
from windows.home import HomeWindow


class SubredditsWindow(Gtk.ApplicationWindow):
	"""Window for displaying user's subscribed subreddits.

	This class provides a window interface to display the list of subreddits
	the authenticated user is subscribed to. It interacts with the main
	application window to allow navigation and selection of subreddits.
	"""

	def __init__(self, home_window: HomeWindow, api: Reddit) -> None:
		"""Initialises the subreddits window.

		Args:
			home_window (HomeWindow): Reference to the main application window
			api (Reddit): Reddit API service instance

		Attributes:
			home_window (HomeWindow): Reference to the home window
			api (Reddit): Reddit API service instance
			css_provider (Gtk.CssProvider): CSS provider for styling
			cursor (Gdk.Cursor): Cursor style for interactive elements
			subreddits (dict | None): List of subreddits the user is subscribed to
			subreddit_boxes (list): List of subreddit box widgets for filtering
		"""
		set_current_window("subreddits", self)
		super().__init__(application=home_window.application)

		self.home_window = home_window
		self.api = api
		self.css_provider = load_css("/assets/styles/subreddits.css")
		self.cursor = create_cursor("pointer")
		self.subreddits = None
		self.subreddit_boxes = []

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
		if entry_buffer.get_length() == 0:
			for box in self.subreddit_boxes:
				row = getattr(box, "row", None)
				if not row:
					continue
				row.set_visible(True)

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
		# TODO Implement subreddit switching logic

	async def render_page(self, subreddits_btn: Gtk.Button | None = None) -> None:
		"""Renders the subreddits window content.

		Constructs the UI elements to display the list of subscribed subreddits,
		including a search entry and a list box containing subreddit entries.
		"""
		spinner = Gtk.Spinner(
			spinning=True, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER
		)
		self.home_window.clamp.set_child(spinner)

		self.subreddits = await self.api.retrieve_subscribed_subreddits()

		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			margin_top=20,
			margin_bottom=20,
			spacing=20,
		)

		buffer = Gtk.EntryBuffer()
		buffer.connect("inserted-text", self.__on_inserted_text)
		buffer.connect_after("deleted-text", self.__on_deleted_text)
		entry = Gtk.Entry(
			buffer=buffer,
			placeholder_text=_("Search"),
			css_classes=["search-entry"],
			width_request=300,
			primary_icon_name="xyz.daimones.Telex.search",
		)
		box.append(entry)

		listbox = Gtk.ListBox(css_classes=["listbox"])
		add_style_context(listbox, self.css_provider)

		for subreddit in self.subreddits["json"]["data"]["children"]:
			row = Gtk.ListBoxRow()
			subreddit_box = Gtk.Box(
				orientation=Gtk.Orientation.HORIZONTAL,
				spacing=10,
				cursor=self.cursor,
			)
			subreddit_icon = load_image(
				"/assets/images/reddit-placeholder.png",
				_("Subreddit placeholder"),
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

		box.append(listbox)
		self.home_window.clamp.set_child(box)

		self.home_window.titlebar_controller.add_home_button()

		if subreddits_btn:
			subreddits_btn.set_sensitive(True)
