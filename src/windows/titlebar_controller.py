"""Titlebar controller implementation for the Reddit client application.

This module manages the application's header bar/titlebar functionality, including:

- Dynamic header bar content management for different views
- Post sorting controls with dropdown menu
- Search functionality access
- User profile menu and actions
- Navigation controls (back button, reload)
- Consistent styling across header elements

The module maintains the header bar state and provides smooth transitions
between different views while keeping a consistent user interface.

Classes:
	TitlebarController: Main class managing header bar content and behavior
"""

import gi

import store

gi.require_versions({"Gtk": "4.0", "Adw": "1", "Gio": "2.0", "GLib": "2.0"})


from gi.repository import Adw, Gtk

from services import Reddit
from utils import _
from utils.common import add_style_context, load_css, load_image
from utils.constants import SortType

from .auth import AuthWindow
from .home import HomeWindow


class TitlebarController:
	"""Controls and manages the application header bar functionality.

	Provides complete header bar management including dynamic content updates,
	navigation controls, sorting options, and user profile features. Handles
	transitions between different views while maintaining state and providing
	a consistent user experience.
	"""

	from .post_detail import PostDetailWindow

	def __init__(self, header_bar: Adw.HeaderBar, home_window: HomeWindow, api: Reddit):
		"""Initialize the header bar controller.

		Sets up the header bar controller with necessary references and
		initializes the base state for managing header bar content.

		Args:
			header_bar (Adw.HeaderBar): The application header bar to manage
			home_window (HomeWindow): Reference to the main application window
			api (Reddit): Reddit API service for data operations

		Attributes:
			header_bar (Adw.HeaderBar): Main header bar widget
			api (Reddit): Reddit API service instance
			home_window (HomeWindow): Reference to main window
			css_provider (Gtk.CssProvider): Styling provider
			start_box (Gtk.Box): Left-side header container
			end_box (Gtk.Box): Right-side header container
			back_btn (Gtk.Button): Navigation back button
			home_btn (Gtk.Button): Home navigation button
			user_data (dict): User profile data retrieved from Reddit API
			profile_data (dict): User profile data for specific categories
		"""
		self.header_bar = header_bar
		self.api = api
		self.home_window = home_window
		self.css_provider = load_css("/assets/styles/home.css")
		self.start_box: Gtk.Box | None = None
		self.end_box: Gtk.Box | None = None
		self.back_btn: Gtk.Button | None = None
		self.home_btn: Gtk.Button | None = None
		self.user_data = None
		self.profile_data = None

		self.home_window.application.loop.create_task(self.retrieve_user_data())

	async def retrieve_user_data(self) -> None:
		"""Fetches user profile data from Reddit API.

		Retrieves the current user's profile information including
		display name and karma points. This data is used to populate
		the profile menu in the header bar.
		"""
		self.user_data = await self.api.retrieve_user_details()
		store.current_user = self.user_data["json"]["name"]

	def setup_titlebar(self) -> None:
		"""Customises the application headerbar.

		Adds buttons and menus to the header bar including reload button,
		sort menu button with popover, search button, and profile menu
		button with popover containing user information and account options.
		"""
		# Left─side |reload|
		self.start_box = Gtk.Box(halign=True, orientation=Gtk.Orientation.HORIZONTAL)
		reload_btn = Gtk.Button(
			icon_name="xyz.daimones.Telex.reload",
			margin_start=5,
			tooltip_text=_("Reload"),
		)
		reload_btn.connect("clicked", self.__on_reload_clicked)
		self.start_box.append(reload_btn)
		self.header_bar.pack_start(self.start_box)

		# Right─side |sort|search|profile|
		self.end_box = Gtk.Box(halign=True, orientation=Gtk.Orientation.HORIZONTAL)

		# Sort menu button
		menu_btn_child = self.add_menu_button_child()
		popover_child = self.add_sort_popover_child()
		self.end_box.append(
			Gtk.MenuButton(
				child=menu_btn_child,
				tooltip_text=_("Sort posts"),
				popover=Gtk.Popover(child=popover_child),
				margin_end=5,
			)
		)

		# Search
		self.end_box.append(
			Gtk.Button(
				icon_name="xyz.daimones.Telex.search",
				margin_end=5,
				tooltip_text=_("Search"),
			)
		)

		# Profile popover
		popover_child = self.add_profile_popover_child()
		self.end_box.append(
			Gtk.MenuButton(
				icon_name="xyz.daimones.Telex.profile",
				tooltip_text=_("Profile"),
				popover=Gtk.Popover(child=popover_child),
				margin_end=5,
			)
		)

		self.header_bar.pack_end(self.end_box)

	def inject_post_detail(self, post_detail_window: PostDetailWindow) -> None:
		"""Injects the post detail view into the header bar.

		Adds a back button to the header bar for navigation and
		removes the existing sort and search buttons.
		"""
		self.post_detail_window = post_detail_window

	def add_back_button(self) -> Gtk.Button:
		"""Inserts a single back-arrow button at the left of the header."""
		self.back_btn = Gtk.Button(
			name="back",
			icon_name="xyz.daimones.Telex.arrow-pointing-left",
			tooltip_text=_("Back to Home"),
			margin_start=5,
		)
		self.back_btn.connect("clicked", self.__on_home_clicked)
		self.header_bar.pack_start(self.back_btn)
		return self.back_btn

	def add_home_button(self) -> Gtk.Button:
		"""Inserts a home button at the left of the header."""
		self.home_btn = Gtk.Button(
			name="home",
			icon_name="xyz.daimones.Telex.homepage",
			tooltip_text=_("Home"),
			margin_start=5,
		)
		self.home_btn.connect("clicked", self.__on_home_clicked)
		self.header_bar.pack_start(self.home_btn)
		return self.home_btn

	def add_profile_popover_child(self) -> Gtk.Box:
		"""Creates profile popover child widget.

		Creates a box containing the user profile information (profile picture,
		username, karma) and menu options (View Profile, Subreddits, Settings,
		About, Log Out) for the profile popover menu.

		Returns:
			Gtk.Box: Container with profile info and menu options
		"""
		popover_child = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

		grid = Gtk.Grid(column_spacing=30)
		grid.insert_row(0)
		grid.insert_column(0)
		grid.insert_column(1)

		user_profile_img = load_image(
			"/assets/images/reddit-placeholder.png",
			"placeholder",
			css_classes=["user-profile-img"],
		)
		add_style_context(user_profile_img, self.css_provider)
		grid.attach(user_profile_img, 0, 0, 1, 1)

		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			valign=Gtk.Align.CENTER,
			halign=Gtk.Align.CENTER,
		)
		display_name = self.user_data["json"]["subreddit"]["display_name_prefixed"]
		total_karma = self.user_data["json"]["total_karma"]
		box.append(Gtk.Label(label=_("%s") % display_name, halign=Gtk.Align.START))
		box.append(Gtk.Label(label=_("%d karma") % total_karma, halign=Gtk.Align.START))
		grid.attach(box, 1, 0, 1, 1)

		popover_child.append(grid)

		menu_labels = [
			_("View Profile"),
			_("Subreddits"),
			_("Preferences"),
			_("About"),
			_("Log Out"),
		]

		for label in menu_labels:
			if "Log" in label:
				menu_btn = Gtk.Button(
					label=label,
					css_classes=["menu-btn-logout"],
					margin_top=5,
					hexpand=True,
				)
				menu_btn.connect("clicked", self.__on_logout_clicked)
			else:
				menu_btn = Gtk.Button(
					label=label, css_classes=["menu-btn"], margin_top=5, hexpand=True
				)
				if "About" in label:
					menu_btn.connect(
						"clicked", self.home_window.application.on_about_action
					)

				if "Preferences" in label:
					menu_btn.connect(
						"clicked", self.home_window.application.on_prefs_action
					)

				if "Profile" in label:
					menu_btn.connect("clicked", self.__on_view_profile_clicked)

			if menu_btn.get_child():
				menu_btn.get_child().set_halign(Gtk.Align.START)

			add_style_context(menu_btn, self.css_provider)
			popover_child.append(menu_btn)

		return popover_child

	def add_sort_popover_child(self) -> Gtk.Box:
		"""Creates sort popover child widget.

		Creates a box containing radio buttons for post sorting options
		(Hot, New, Rising, etc.) allowing the user to change the post
		sort order.

		Returns:
			Gtk.Box: Container with post sorting options as radio buttons
		"""
		popover_child = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

		active = store.current_sort == SortType.BEST
		best_check_btn = Gtk.CheckButton(
			active=active,
			name=str(SortType.BEST.value),
			label=_("%s") % store.post_sort_type[SortType.BEST.value],
		)
		best_check_btn.connect("toggled", self.__on_check_btn_toggled)

		active = store.current_sort == SortType.NEW
		new_check_btn = Gtk.CheckButton(
			active=active,
			name=str(SortType.NEW.value),
			label=_("%s") % store.post_sort_type[SortType.NEW.value],
		)
		new_check_btn.set_group(best_check_btn)
		new_check_btn.connect("toggled", self.__on_check_btn_toggled)

		active = store.current_sort == SortType.HOT
		hot_check_btn = Gtk.CheckButton(
			active=active,
			name=str(SortType.HOT.value),
			label=_("%s") % store.post_sort_type[SortType.HOT.value],
		)
		hot_check_btn.set_group(best_check_btn)
		hot_check_btn.connect("toggled", self.__on_check_btn_toggled)

		active = store.current_sort == SortType.TOP
		top_check_btn = Gtk.CheckButton(
			active=active,
			name=str(SortType.TOP.value),
			label=_("%s") % store.post_sort_type[SortType.TOP.value],
		)
		top_check_btn.set_group(hot_check_btn)
		top_check_btn.connect("toggled", self.__on_check_btn_toggled)

		active = store.current_sort == SortType.RISING
		rising_check_btn = Gtk.CheckButton(
			active=active,
			name=str(SortType.RISING.value),
			label=_("%s") % store.post_sort_type[SortType.RISING.value],
		)
		rising_check_btn.set_group(top_check_btn)
		rising_check_btn.connect("toggled", self.__on_check_btn_toggled)

		popover_child.append(best_check_btn)
		popover_child.append(new_check_btn)
		popover_child.append(hot_check_btn)
		popover_child.append(top_check_btn)
		popover_child.append(rising_check_btn)

		return popover_child

	def add_menu_button_child(self) -> Gtk.Box:
		"""Creates menu button child widget.

		Creates a box containing the sort menu button's label showing the
		current sort type and a dropdown icon to indicate it's expandable.

		Returns:
			Gtk.Box: Container with sort button label and dropdown icon
		"""
		menu_btn_child = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			halign=Gtk.Align.CENTER,
			valign=Gtk.Align.CENTER,
		)

		grid = Gtk.Grid(column_spacing=30)
		grid.insert_row(0)
		grid.insert_column(0)
		grid.insert_column(1)

		label = Gtk.Label(
			label=_("%s") % store.post_sort_type[store.current_sort],
			css_classes=["menu-btn-label"],
		)
		grid.attach(label, 0, 0, 1, 1)

		image = Gtk.Image(icon_name="xyz.daimones.Telex.sort-down")
		grid.attach(image, 1, 0, 1, 1)

		menu_btn_child.append(grid)

		add_style_context(label, self.css_provider)

		return menu_btn_child

	def __on_reload_clicked(self, _widget: Gtk.Button) -> None:
		"""Handles reload button click events.

		Reloads the current page by fetching the latest data from Reddit
		and re-rendering the page with the updated content.

		Args:
			_widget (Gtk.Button): The reload button that was clicked

		Returns:
			None: This method does not return a value.
		"""
		if store.current_window == "post_detail":
			self.home_window.application.loop.create_task(
				self.post_detail_window.render_page()
			)
		else:
			self.home_window.application.loop.create_task(
				self.home_window.render_page(setup_titlebar=False)
			)

	def __on_check_btn_toggled(self, widget: Gtk.CheckButton) -> None:
		"""Handles radio button click events for sorting options.

		Updates the current sort category based on the selected radio button
		and reloads the page with the new sorting option.

		Args:
			widget (Gtk.CheckButton): The radio button that was clicked

		Returns:
			None: This method does not return a value.
		"""
		if widget.get_active():
			store.current_sort = int(widget.get_name())
			self.__on_reload_clicked(widget)
			self.header_bar.remove(self.start_box)
			self.header_bar.remove(self.end_box)
			self.setup_titlebar()

	def __on_home_clicked(self, button: Gtk.Button) -> None:
		"""Handles home button click events.

		Returns to the home view by restoring the HomeWindow view
		and clearing the current scrolled window view.

		Args:
			button (Gtk.Button): The button that triggered the event

		Returns:
			None: This method does not return a value.
		"""
		self.header_bar.remove(button)
		self.home_btn = None
		self.back_btn = None
		store.back_btn_set = False

		if self.home_window.scrolled_window.get_child():
			self.home_window.scrolled_window.set_child(None)

		self.home_window.application.loop.create_task(
			self.home_window.render_page(setup_titlebar=False, set_current_window=True)
		)

	def __on_logout_clicked(self, button: Gtk.Button) -> None:
		"""Handles logout button click events.

		Logs out the user by:
		- Clearing the access token from AWS Secrets
		- Closing existing application window
		- Restoring the auth screen with login button

		Args:
			button (Gtk.Button): The button that triggered the event

		Returns:
			None: This method does not return a value.
		"""
		button.set_sensitive(False)
		self.home_window.base.aws_client.delete_secret("telex-access-token")
		self.home_window.base.close()
		AuthWindow(application=self.home_window.application).present()

	def __on_view_profile_clicked(self, button: Gtk.Button) -> None:
		"""Handles view profile button click events.

		Opens the user profile window to display the user's Reddit profile
		and settings.

		Args:
			button (Gtk.Button): The button that triggered the event

		Returns:
			None: This method does not return a value.
		"""
		button.set_sensitive(False)

		from windows.profile import ProfileWindow

		profile_window = ProfileWindow(base_window=self.home_window, api=self.api)
		self.home_window.application.loop.create_task(
			profile_window.render_page(view_profile_btn=button)
		)
