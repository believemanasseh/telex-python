"""Profile window module for the Telex application.

This module provides the ProfileWindow class which handles user profile
management and settings within the Telex application interface.
"""

import logging

import gi
import httpx

import store

gi.require_versions({"Gtk": "4.0", "Adw": "1"})


from gi.repository import Gtk

from services import Reddit
from utils import _
from utils.common import (
	add_style_context,
	add_style_contexts,
	create_cursor,
	get_submission_time,
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
			about_data (dict): Stores about data for the user profile.
			profile_data (dict): Stores detailed profile data for the user.
			css_provider (Gtk.CssProvider): CSS styles provider for the window.
			cursor (Gtk.Cursor): Custom cursor for clickable elements in the window.
			main_content (Gtk.Box): Main content area for displaying profile information.
			tabs_hbox (Gtk.Box): Horizontal box containing profile tabs.
			box (Gtk.Box): Vertical box for layout of the profile window.
		"""
		set_current_window("profile", self)
		super().__init__(application=base_window.application)

		self.application = base_window.application
		self.base = base_window
		self.api = api
		self.about_data = None
		self.profile_data = None
		self.css_provider = load_css("/assets/styles/profile.css")
		self.cursor = create_cursor("pointer")
		self.main_content = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=10,
			margin_top=20,
			margin_bottom=20,
			width_request=1000,
		)

	async def fetch_data(self, category: str) -> dict[str, int | dict]:
		"""Fetches user profile data from Reddit API.

		Args:
			category (str): The category of profile data to fetch.

		Returns:
			dict[str, int | dict]: The user profile data retrieved from the API.

		Raises:
			httpx.RequestError: If the request to the Reddit API fails.
		"""
		try:
			return await self.api.retrieve_profile_details(store.current_user, category)
		except httpx.RequestError as e:
			msg = "Failed to fetch user profile data"
			raise httpx.RequestError(msg) from e

	def load_actions_box(
		self, score: int, num_of_comments: int | None = None, alt_reply: bool = False
	) -> Gtk.Box:
		"""Creates a horizontal box for action buttons related to comments or posts.

		Args:
			score (int): The score of the comment or post.
			num_of_comments (int, optional): The number of comments associated with post.
			alt_reply (bool, optional): If True, uses an alternative reply button style.

		Returns:
			Gtk.Box: A box containing action buttons for comments.
		"""
		actions_box = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=12,
			valign=Gtk.Align.START,
			halign=Gtk.Align.START,
			margin_top=5,
		)

		# Add upvote/downvote buttons
		vote_box = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=5,
			valign=Gtk.Align.CENTER,
		)
		upvote_btn = Gtk.Button(icon_name="xyz.daimones.Telex.upvote")
		score_label = Gtk.Label(
			label=_("%d") % score,
			css_classes=["comment-score"],
		)
		downvote_btn = Gtk.Button(icon_name="xyz.daimones.Telex.downvote")
		vote_box.append(upvote_btn)
		vote_box.append(score_label)
		vote_box.append(downvote_btn)
		actions_box.append(vote_box)

		# Add reply button
		hbox = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=2,
			css_classes=["comments-box"],
		)
		if alt_reply:
			comments_image = load_image(
				"/assets/images/comments.png",
				"Comments",
				css_classes=["comment-avatar"],
				css_provider=self.css_provider,
			)
			comments_label = Gtk.Label(label=_("%d") % num_of_comments)
			hbox.append(comments_image)
			hbox.append(comments_label)
			actions_box.append(hbox)
		else:
			comments_image = load_image(
				"/assets/images/comments.png",
				"Comments",
				css_classes=["comment-avatar"],
				css_provider=self.css_provider,
			)
			comments_label = Gtk.Label(label=_("Reply"))
		hbox.append(comments_image)
		hbox.append(comments_label)
		actions_box.append(hbox)

		add_style_contexts([hbox], self.css_provider)

		return actions_box

	def load_comment(
		self,
		subreddit_name: str,
		link_title: str,
		body: str,
		score: int,
		date: str,
	) -> Gtk.Box:
		"""Loads a single comment item into the profile overview.

		Args:
			subreddit_name (str): The name of the subreddit where the comment was made.
			link_title (str): The title of the link associated with the comment.
			body (str): The content of the comment.
			score (int): The score of the comment.
			date (str): The creation time of the comment.

		Returns:
			Gtk.Box: A GTK box containing the formatted comment item.
		"""
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=5,
			css_classes=[
				"comment-item-dark"
				if self.application.settings.get_boolean("dark-mode")
				else "comment-item"
			],
			width_request=1000,
			margin_bottom=10,
		)

		# Add comment subreddit
		subreddit_label = Gtk.Label(
			label=_("%s") % subreddit_name,
			css_classes=["comment-subreddit"],
			halign=Gtk.Align.START,
			margin_bottom=3,
		)
		box.append(subreddit_label)

		# Add comment title
		title_label = Gtk.Label(
			label=_("%s") % link_title,
			css_classes=["comment-title"],
			halign=Gtk.Align.START,
			margin_bottom=3,
		)
		box.append(title_label)

		# Add comment author and date
		temp = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5, margin_bottom=5)
		author_label = Gtk.Label(
			label=_("%s") % store.current_user,
			css_classes=["comment-author"],
			tooltip_text=_("Comment author"),
		)
		date_label = Gtk.Label(
			label=_("commented %s") % date,
			css_classes=["comment-date"],
			tooltip_text=_("Comment date"),
		)
		temp.append(author_label)
		temp.append(date_label)
		box.append(temp)

		# Add comment body
		body_label = Gtk.Label(
			label=_("%s") % body,
			css_classes=["comment-body"],
			halign=Gtk.Align.START,
		)
		box.append(body_label)

		actions_box = self.load_actions_box(score)

		box.append(actions_box)

		add_style_contexts(
			[
				box,
				subreddit_label,
				title_label,
				temp,
				body_label,
				author_label,
				date_label,
			],
			self.css_provider,
		)

		return box

	def load_post(
		self,
		subreddit_name: str,
		title: str,
		selftext: str,
		score: int,
		num_of_comments: int,
		date: str,
	) -> Gtk.Box:
		"""Loads a single post item into the profile overview.

		Args:
			subreddit_name (str): The name of the subreddit where the post was made.
			title (str): The title of the post.
			selftext (str): The content of the post.
			score (int): The score of the post.
			num_of_comments (int): The number of comments on the post.
			date (str): The creation date of the post.

		Returns:
			Gtk.Box: A GTK box containing the formatted post item.
		"""
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=5,
			css_classes=[
				"post-item-dark"
				if self.application.settings.get_boolean("dark-mode")
				else "post-item"
			],
			width_request=1000,
			margin_bottom=10,
		)

		# Add subreddit and date labels
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, margin_bottom=3, spacing=5)
		subreddit_label = Gtk.Label(
			label=_("%s") % subreddit_name,
			css_classes=["post-subreddit"],
			halign=Gtk.Align.START,
		)
		date_label = Gtk.Label(label=_("%s") % date, css_classes=["post-date"])
		hbox.append(subreddit_label)
		hbox.append(date_label)
		box.append(hbox)

		# Add post title label
		title_label = Gtk.Label(
			label=_("%s") % title,
			css_classes=["post-title"],
			halign=Gtk.Align.START,
			margin_bottom=3,
		)
		box.append(title_label)

		# Add selftext label
		selftext_label = Gtk.Label(
			label=_("%s") % selftext,
			css_classes=["post-selftext"],
			wrap=True,
			margin_bottom=3,
		)
		box.append(selftext_label)

		# Add actions box
		actions_box = self.load_actions_box(
			score=score, num_of_comments=num_of_comments, alt_reply=True
		)
		box.append(actions_box)

		add_style_contexts(
			[box, hbox, subreddit_label, title_label, date_label], self.css_provider
		)

		return box

	def create_overview_content(self) -> Gtk.Box:
		"""Creates the overview tab content."""
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=10,
			margin_top=20,
			margin_bottom=20,
			width_request=1000,
		)

		for child in self.profile_data["json"]["data"]["children"]:
			subreddit_name = child["data"]["subreddit_name_prefixed"]
			date = get_submission_time(child["data"]["created_utc"])
			score = child["data"]["score"]

			if child["kind"] == "t1":
				link_title = child["data"]["link_title"]
				body = child["data"]["body"]

				item_box = self.load_comment(
					subreddit_name=subreddit_name,
					link_title=link_title,
					body=body,
					score=score,
					date=date,
				)
			elif child["kind"] == "t3":
				selftext = child["data"]["selftext"]
				title = child["data"]["title"]
				num_of_comments = child["data"]["num_comments"]
				item_box = self.load_post(
					subreddit_name=subreddit_name,
					title=title,
					selftext=selftext,
					score=score,
					num_of_comments=num_of_comments,
					date=date,
				)

			box.append(item_box)

		return box

	def create_posts_content(self) -> Gtk.Box:
		"""Creates the posts (including upvoted and downvoted) tab content."""
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=10,
			margin_top=20,
			margin_bottom=20,
			width_request=1000,
		)

		for child in self.profile_data["json"]["data"]["children"]:
			subreddit_name = child["data"]["subreddit_name_prefixed"]
			title = child["data"]["title"]
			num_of_comments = child["data"]["num_comments"]
			score = child["data"]["score"]
			selftext = child["data"]["selftext"]
			date = get_submission_time(child["data"]["created_utc"])

			post_box = self.load_post(
				subreddit_name=subreddit_name,
				title=title,
				selftext=selftext,
				score=score,
				num_of_comments=num_of_comments,
				date=date,
			)

			box.append(post_box)

		return box

	def create_comments_content(self) -> Gtk.Box:
		"""Creates the comments tab content."""
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=10,
			margin_top=20,
			margin_bottom=20,
			width_request=1000,
		)

		for child in self.profile_data["json"]["data"]["children"]:
			subreddit_name = child["data"]["subreddit_name_prefixed"]
			date = get_submission_time(child["data"]["created_utc"])
			score = child["data"]["score"]
			link_title = child["data"]["link_title"]
			body = child["data"]["body"]

			comment_box = self.load_comment(
				subreddit_name=subreddit_name,
				link_title=link_title,
				body=body,
				score=score,
				date=date,
			)

			box.append(comment_box)

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
		tab_name = widget.get_name()

		# Disable other tab buttons
		parent = widget.get_parent()
		if parent:
			for child in parent.observe_children():
				if isinstance(child, Gtk.Label) and child.get_name() != tab_name:
					child.set_sensitive(False)

		# Update CSS classes
		if self.current_tab_widget:
			self.current_tab_widget.remove_css_class("current-tab")
		widget.add_css_class("current-tab")

		self.current_tab_widget = widget

		if self.main_content and self.main_content.get_parent() == self.box:
			self.box.remove(self.main_content)
			self.loading_spinner = Gtk.Spinner(spinning=True, halign=Gtk.Align.CENTER)
			self.box.append(self.loading_spinner)

		self.application.loop.create_task(self.render_tab_content(tab_name, widget))

	async def render_tab_content(self, tab_name: str, widget: Gtk.Label) -> None:
		"""Renders the content for the specified tab.

		Args:
			tab_name (str): The name of the tab to render (e.g., 'overview', 'submitted').
			widget (Gtk.Label): The label widget that was clicked to change the tab.

		Returns:
			None: This method does not return a value.
		"""
		self.profile_data = await self.fetch_data(tab_name)

		match tab_name:
			case "overview":
				self.main_content = self.create_overview_content()
				store.current_profile_tab = "overview"
			case "submitted":
				self.main_content = self.create_posts_content()
				store.current_profile_tab = "submitted"
			case "comments":
				self.main_content = self.create_comments_content()
				store.current_profile_tab = "comments"
			case "upvoted":
				self.main_content = self.create_posts_content()
				store.current_profile_tab = "upvoted"
			case "downvoted":
				self.main_content = self.create_posts_content()
				store.current_profile_tab = "downvoted"
			case _:
				logging.info("Tab not found")
				raise ValueError(_("Unknown tab name: {}").format(tab_name))

		# Re-enable other tab buttons
		parent = widget.get_parent()
		if parent:
			for child in parent.observe_children():
				if isinstance(child, Gtk.Label) and child.get_name() != tab_name:
					child.set_sensitive(True)

		if self.main_content:
			self.box.remove(self.loading_spinner)
			self.box.append(self.main_content)

	async def render_page(self, view_profile_btn: Gtk.Button | None = None) -> None:
		"""Renders the profile page.

		This method fetches the user profile data and constructs the UI
		for the profile window. It includes user information, tabs for
		overview, posts, comments, upvoted, and downvoted content.
		It sets up the main content area and adds it to the scrolled window
		of the base window.

		Args:
			view_profile_btn (Gtk.Button, optional): The button to view the profile.

		Returns:
			None: This method does not return a value.
		"""
		spinner = Gtk.Spinner(
			spinning=True, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER
		)
		self.base.clamp.set_child(spinner)

		self.about_data = await self.fetch_data("about")

		self.profile_data = await self.fetch_data(store.current_profile_tab)

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
			"Reddit placeholder",
			css_classes=["user-avatar"],
			css_provider=self.css_provider,
			tooltip_text="User avatar",
		)

		hbox.append(user_img)

		# Create a vertical box for user information
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			valign=Gtk.Align.CENTER,
			halign=Gtk.Align.START,
			spacing=5,
		)
		profile_name = Gtk.Label(
			label=_("%s") % self.about_data["json"]["data"]["name"],
			css_classes=["profile-name"],
		)
		profile_display_name = Gtk.Label(
			label=_("%s")
			% self.about_data["json"]["data"]["subreddit"]["display_name_prefixed"],
			css_classes=["profile-display-name"],
			halign=Gtk.Align.START,
		)
		box.append(profile_name)
		box.append(profile_display_name)

		hbox.append(box)
		vbox.append(hbox)

		self.tabs_hbox = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=10,
			halign=Gtk.Align.START,
			valign=Gtk.Align.START,
			width_request=1000,
		)

		tabs = [
			_("Overview"),
			_("Posts"),
			_("Comments"),
			_("Upvoted"),
			_("Downvoted"),
		]

		for tab in tabs:
			is_dark = self.application.settings.get_boolean("dark-mode")
			is_current = store.current_profile_tab == tab.lower()
			css_classes = ["profile-tab-dark" if is_dark else "profile-tab"]

			tab_widget = Gtk.Label(
				label=tab,
				name=tab.lower(),
				css_classes=css_classes,
				cursor=self.cursor,
			)

			if tab == "Posts":
				tab_widget.set_name("submitted")
				is_current = store.current_profile_tab == "submitted"

			tab_widget.set_tooltip_text(_("Click to view {}").format(tab.lower()))

			if is_current:
				tab_widget.add_css_class("current-tab")
				self.current_tab_widget = tab_widget

			click_controller = Gtk.GestureClick()
			click_controller.connect(
				"pressed",
				lambda gesture, n_press, x, y, widget=tab_widget: self.__on_tab_clicked(
					gesture, n_press, x, y, widget
				),
			)
			tab_widget.add_controller(click_controller)
			self.tabs_hbox.append(tab_widget)

			add_style_context(tab_widget, self.css_provider)

		vbox.append(self.tabs_hbox)

		if store.current_profile_tab == "overview":
			self.box = Gtk.Box(
				orientation=Gtk.Orientation.VERTICAL,
				spacing=10,
				halign=Gtk.Align.CENTER,
				valign=Gtk.Align.START,
				width_request=1000,
			)
			self.main_content = self.create_overview_content()
			self.box.append(self.main_content)
			vbox.append(self.box)

		self.base.clamp.set_child(vbox)

		add_style_contexts([profile_name, profile_display_name], self.css_provider)

		self.base.titlebar_controller.add_home_button()

		if view_profile_btn:
			view_profile_btn.set_sensitive(True)
