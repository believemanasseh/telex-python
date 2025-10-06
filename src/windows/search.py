"""Module for the SearchWindow class.

This module defines the SearchWindow class, which provides a user interface for searching
Reddit content. It integrates with the main application window and the post detail window
to display search results and navigate to detailed views of selected subreddits or users.

Classes:
	SearchWindow: Main window class implementing the search functionality.
"""

import gi

gi.require_versions({"Gtk": "4.0"})


from gi.repository import Gtk

from services import Reddit
from utils.common import add_style_context, add_style_contexts, load_css, load_image
from windows.home import HomeWindow


class SearchWindow(Gtk.ApplicationWindow):
	"""Window for searching Reddit content.

	This class provides a window interface for searching Reddit subreddits and users. It
	interacts with the main application window and the post detail view to display
	search results and navigate to detailed views of selected subreddits/users.
	"""

	def __init__(
		self,
		home_window: HomeWindow,
		api: Reddit,
		query: str,
	) -> None:
		"""Initialises the search window.

		Args:
		    home_window (HomeWindow): Reference to the main application window
		    post_detail_window (PostDetailWindow): Reference to the post detail view
		    api (Reddit): Reddit API service instance
			query (str): The search query string

		Attributes:
			home_window (HomeWindow): Reference to the home window
			post_detail_window (PostDetailWindow): Reference to the post detail window
			api (Reddit): Reddit API service instance
			css_provider (Gtk.CssProvider): CSS provider for styling
			subreddits (dict | None): List of subreddits the user is subscribed to
			user_profiles (dict | None): List of user profiles the user follows
		"""
		super().__init__(application=home_window.application)

		self.home_window = home_window
		self.api = api
		self.query = query
		self.css_provider = load_css("/assets/styles/search.css")
		self.subreddits = None
		self.user_profiles = None

		self.home_window.application.loop.create_task(
			self.retrieve_subreddits_and_users(query=self.query)
		)

	async def retrieve_subreddits_and_users(self, query) -> None:
		"""Fetches list of subreddits the user is subscribed to.

		Args:
			query (str): Search query to filter subreddits

		Returns:
			dict[str, int | dict] | None: Response containing status code and subreddit data
		"""
		res = await self.api.retrieve_subreddits(query=query)
		self.subreddits = res["json"]["data"]["children"]
		res = await self.api.retrieve_user_profiles(query=query)
		self.user_profiles = res["json"]["data"]["children"]
		self.display_subreddit_results()

	def display_subreddit_results(self) -> None:
		"""Displays the subreddit search results in the search window.

		Creates a list of subreddits matching the search query and displays
		them in the window.
		"""
		listbox = Gtk.ListBox(margin_top=20, margin_bottom=20)

		for subreddit in self.subreddits:
			row = Gtk.ListBoxRow()
			box = Gtk.Box(
				orientation=Gtk.Orientation.HORIZONTAL,
				spacing=10,
				margin_top=5,
				margin_bottom=5,
				margin_start=5,
				margin_end=5,
			)
			subreddit_icon = load_image(
				"/assets/images/reddit-placeholder.png",
				"placeholder",
				css_classes=["subreddit-icon"],
			)
			box.append(subreddit_icon)

			subreddit_info = Gtk.Box(
				orientation=Gtk.Orientation.VERTICAL,
				halign=Gtk.Align.START,
			)
			subreddit_title = Gtk.Label(
				label=subreddit["data"]["title"],
				halign=Gtk.Align.START,
				css_classes=["subreddit-title"],
			)
			subreddit_name = Gtk.Label(
				label=subreddit["data"]["display_name_prefixed"],
				halign=Gtk.Align.START,
			)
			add_style_contexts([subreddit_icon, subreddit_title], self.css_provider)
			subreddit_info.append(subreddit_title)
			subreddit_info.append(subreddit_name)

			box.append(subreddit_info)
			row.set_child(box)
			listbox.append(row)

		self.home_window.clamp.set_child(listbox)

	def display_user_profile_results(self) -> None:
		"""Displays the user profile search results in the search window.

		Creates a list of user profiles matching the search query and displays
		them in the window.
		"""
		listbox = Gtk.ListBox(margin_top=20, margin_bottom=20)

		for user in self.user_profiles:
			row = Gtk.ListBoxRow()
			box = Gtk.Box(
				orientation=Gtk.Orientation.HORIZONTAL,
				spacing=10,
				margin_top=5,
				margin_bottom=5,
				margin_start=5,
				margin_end=5,
			)
			user_icon = load_image(
				"/assets/images/reddit-placeholder.png",
				"placeholder",
				css_classes=["user-icon"],
			)
			add_style_context(user_icon, self.css_provider)
			box.append(user_icon)

			user_info = Gtk.Box(
				orientation=Gtk.Orientation.VERTICAL,
				halign=Gtk.Align.START,
			)
			user_name = Gtk.Label(
				label=f"u/{user['data']['name']}", halign=Gtk.Align.START
			)
			user_info.append(user_name)

			box.append(user_info)
			row.set_child(box)
			listbox.append(row)

		self.home_window.clamp.set_child(listbox)
