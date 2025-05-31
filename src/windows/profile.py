"""Profile window module for the Telex application.

This module provides the ProfileWindow class which handles user profile
management and settings within the Telex application interface.
"""

import gi
import httpx

import store

gi.require_versions({"Gtk": "4.0", "Adw": "1"})


from gi.repository import Adw, Gtk

from services import Reddit
from utils import _
from utils.common import (
	add_style_contexts,
	create_cursor,
	load_css,
	load_image,
	set_current_window,
)
from windows.home import HomeWindow


class ProfileWindow(Gtk.ApplicationWindow):
	"""ProfileWindow class for managing user profile settings."""

	def __init__(self, base_window: HomeWindow, api: Reddit) -> None:
		"""Initialises the Profile Window.

		This window is used to display and manage user profile settings.
		It inherits from Gtk.ApplicationWindow and is designed to be part of
		the Telex application. The window can be used to render user profile
		data and allow users to update their settings.

		Args:
			base_window (HomeWindow): The base window instance for the application.
			api (Reddit): The Reddit API instance for user data operations.

		Attributes:
			application (Adw.Application): The parent GTK application.
			base (HomeWindow): Reference to the base window instance.
			api (Reddit): Reddit API instance for data operations.
			data (dict): Stores user profile data fetched from the API.
			css_provider (Gtk.CssProvider): CSS styles provider for the window.
			cursor (Gtk.Cursor): Custom cursor for clickable elements in the window.
		"""
		set_current_window("profile", self)
		super().__init__(application=base_window.application)

		self.application = base_window.application
		self.base = base_window
		self.api = api
		self.data = None
		self.css_provider = load_css("/assets/styles/profile.css")
		self.cursor = create_cursor("pointer")

	async def fetch_data(self) -> None:
		"""Fetches user profile data from Reddit API.

		This method retrieves the user profile data for the specified username
		and stores it in the `data` attribute. It can be used to populate the
		profile window with user information.
		"""
		try:
			return await self.api.retrieve_profile_details(store.current_user, "about")
		except httpx.RequestError as e:
			msg = "Failed to fetch user profile data"
			raise httpx.RequestError(msg) from e

	def create_overview_page(self) -> Gtk.Box:
		"""Creates the overview tab content."""
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=10,
			margin_start=20,
			margin_end=20,
			margin_top=20,
			margin_bottom=20,
		)
		box.append(Gtk.Label(label="User overview will be displayed here."))
		return box

	def create_posts_page(self) -> Gtk.Box:
		"""Creates the posts tab content."""
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=10,
			margin_start=20,
			margin_end=20,
			margin_top=20,
			margin_bottom=20,
		)
		box.append(Gtk.Label(label="Posts will be displayed here."))
		return box

	def create_comments_page(self) -> Gtk.Box:
		"""Creates the comments tab content."""
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=10,
			margin_start=20,
			margin_end=20,
			margin_top=20,
			margin_bottom=20,
		)
		box.append(Gtk.Label(label="Comments will be displayed here."))
		return box

	def create_upvoted_page(self) -> Gtk.Box:
		"""Creates the upvoted posts tab content."""
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=10,
			margin_start=20,
			margin_end=20,
			margin_top=20,
			margin_bottom=20,
		)
		box.append(Gtk.Label(label="Upvoted posts will be displayed here."))
		return box

	def create_downvoted_page(self) -> Gtk.Box:
		"""Creates the downvoted posts tab content."""
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=10,
			margin_start=20,
			margin_end=20,
			margin_top=20,
			margin_bottom=20,
		)
		box.append(Gtk.Label(label="Downvoted posts will be displayed here."))
		return box

	def __on_tab_clicked(
		self,
		_gesture: Gtk.GestureClick,
		_n_press: int,
		_x: float,
		_y: float,
		widget: Gtk.Label,
	) -> None:
		"""Handles tab click events to change the active tab.

		Args:
			_gesture (Gtk.GestureClick): The click gesture that triggered the event.
			_n_press (int): The number of times the label has been pressed.
			_x (float): The x-coordinate of the click event.
			_y (float): The y-coordinate of the click event.
			widget (Gtk.Widget): The label widget that was clicked.

		Returns:
			None: This method does not return a value.
		"""
		tab_name = widget.get_label().lower()

		# Update CSS classes
		if self.current_tab_widget:
			self.current_tab_widget.remove_css_class("current-tab")
		widget.add_css_class("current-tab")

		self.current_tab_widget = widget

		if self.main_content.get_parent() == self.box:
			self.box.remove(self.main_content)

		if tab_name == "overview":
			self.main_content = self.create_overview_page()
			store.current_profile_tab = "overview"
		elif tab_name == "posts":
			self.main_content = self.create_posts_page()
			store.current_profile_tab = "posts"
		elif tab_name == "comments":
			self.main_content = self.create_comments_page()
			store.current_profile_tab = "comments"
		elif tab_name == "upvoted":
			self.main_content = self.create_upvoted_page()
			store.current_profile_tab = "upvoted"
		elif tab_name == "downvoted":
			self.main_content = self.create_downvoted_page()
			store.current_profile_tab = "downvoted"

		self.box.append(self.main_content)
		self.application.loop.create_task(self.render_page(add_home_btn=False))

	async def render_page(self, add_home_btn: bool = True) -> None:
		"""Renders the profile page.

		This method fetches the user profile data and constructs the UI
		for the profile window. It includes user information, tabs for
		overview, posts, comments, upvoted, and downvoted content.
		It sets up the main content area and adds it to the scrolled window
		of the base window.

		Args:
			add_home_btn (bool): Whether to add a home button to the title bar.
				Default is True, which adds the home button.

		Returns:
			None: This method does not return a value.
		"""
		self.data = await self.fetch_data()

		self.base.scrolled_window.set_child(None)

		vbox = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=20,
			margin_start=20,
			margin_end=20,
			margin_top=50,
			margin_bottom=20,
			width_request=1000,
		)

		# Create a horizontal box for user avatar and name
		hbox = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=10,
			margin_bottom=20,
			width_request=1000,
		)

		user_img = load_image(
			"/assets/images/reddit-placeholder.png",
			_("Reddit placeholder"),
			css_classes=["user-avatar"],
			css_provider=self.css_provider,
		)
		user_img.set_tooltip_text(_("User avatar"))
		user_img.set_size_request(100, 100)

		hbox.append(user_img)

		# Create a vertical box for user information
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			valign=Gtk.Align.CENTER,
			halign=Gtk.Align.START,
			spacing=5,
		)
		name = self.data["json"]["data"]["name"]
		display_name = self.data["json"]["data"]["subreddit"]["display_name_prefixed"]
		profile_name = Gtk.Label(label=_("%s") % name, css_classes=["profile-name"])
		profile_display_name = Gtk.Label(
			label=_("%s") % display_name,
			css_classes=["profile-display-name"],
			halign=Gtk.Align.START,
		)
		box.append(profile_name)
		box.append(profile_display_name)

		add_style_contexts([profile_name, profile_display_name], self.css_provider)

		hbox.append(box)
		vbox.append(hbox)

		self.tabs_hbox = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=10,
			halign=Gtk.Align.START,
			valign=Gtk.Align.START,
			width_request=1000,
		)

		labels = [
			_("Overview"),
			_("Posts"),
			_("Comments"),
			_("Upvoted"),
			_("Downvoted"),
		]

		for label in labels:
			is_dark = self.application.settings.get_boolean("dark-mode")
			is_current = store.current_profile_tab == label.lower()

			css_classes = ["profile-tab-dark" if is_dark else "profile-tab"]

			label_widget = Gtk.Label(
				label=label,
				css_classes=css_classes,
				cursor=self.cursor,
			)
			label_widget.set_tooltip_text(_("Click to view {}").format(label.lower()))

			if is_current:
				label_widget.add_css_class("current-tab")
				self.current_tab_widget = label_widget

			click_controller = Gtk.GestureClick()
			click_controller.connect(
				"pressed",
				lambda gesture, n_press, x, y, widget=label_widget: self.__on_tab_clicked(
					gesture, n_press, x, y, widget
				),
			)
			label_widget.add_controller(click_controller)
			self.tabs_hbox.append(label_widget)
			add_style_contexts([label_widget], self.css_provider)

		vbox.append(self.tabs_hbox)

		if store.current_profile_tab == "overview":
			self.box = Gtk.Box(
				orientation=Gtk.Orientation.VERTICAL,
				spacing=10,
				halign=Gtk.Align.CENTER,
				valign=Gtk.Align.START,
				width_request=1000,
			)
			self.main_content = self.create_overview_page()
			self.box.append(self.main_content)

		vbox.append(self.box)

		clamp = Adw.Clamp(child=vbox, maximum_size=1000)
		viewport = Gtk.Viewport()
		viewport.set_child(clamp)

		self.base.scrolled_window.set_child(viewport)

		if add_home_btn:
			self.base.titlebar_controller.add_home_button()

		self.base.titlebar_controller.processing_click = False
