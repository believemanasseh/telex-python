"""Home window implementation for the Reddit client application.

This module contains the HomeWindow class which implements the main home page
view of the Reddit client. It handles:

- Displaying Reddit posts in a scrollable feed
- Post interaction controls (upvote/downvote, comments, etc.)
- Post sorting and filtering
- Navigation between home feed and post details
- Dynamic data loading and refreshing
- User profile and settings access

Classes:
    HomeWindow: Main window class implementing the home page functionality
"""

import gi

import store

gi.require_versions({"Gtk": "4.0", "Adw": "1", "Pango": "1.0"})

from gi.repository import Adw, Gtk, Pango

from app import Telex
from services import Reddit
from utils import _
from utils.common import (
	add_style_context,
	add_style_contexts,
	append_all,
	create_cursor,
	get_submission_time,
	load_css,
	load_image,
)
from utils.common import (
	set_current_window as set_current_window_func,
)
from windows.auth import AuthWindow


class HomeWindow(Gtk.ApplicationWindow):
	"""Base class for homepage.

	This class is responsible for displaying the home page of the Reddit client.
	It shows a list of Reddit posts with upvote/downvote buttons, post metadata,
	action buttons, and provides navigation to post detail views. It also
	includes functionality for sorting posts, reloading content, and accessing
	user profile options.

	Attributes:
		base (AuthWindow): Reference to the base application window
		api (Reddit): Reference to the Reddit API for data operations
		cursor (Gdk.Cursor): Custom cursor for interactive elements
		css_provider (Gtk.CssProvider): Provider for styling the home page
		data (dict): Fetched Reddit posts data based on current sort category
		scrolled_window (Gtk.ScrolledWindow): Main scrollable container for posts
		viewport (Gtk.Viewport): Viewport containing the posts
	"""

	def __init__(self, application: Telex, base_window: AuthWindow, api: Reddit):
		"""Initialise the Home window with base window and Reddit API.

		This constructor sets up the home window by maximizing the base application window
		and applying styles to the base box widget. It also fetches initial Reddit data.

		Args:
			application (Adw.Application): The parent GTK application
			base_window (AuthWindow): The base application window instance
			api (Reddit): The Reddit API instance for fetching data

		Attributes:
			application: The parent GTK application
			base: The base window reference
			api: The Reddit API reference
			cursor: Custom pointer cursor
			css_provider: CSS styles provider
			data: Fetched Reddit posts data based on current sort category
			box: Main vertical box container for the home page content
			titlebar_controller: Controller for the title bar functionality
			scrolled_window (Gtk.ScrolledWindow): Main scrollable container for posts
			viewport (Gtk.Viewport): Viewport containing the posts
		"""
		set_current_window_func("home", self)
		super().__init__(application=application)
		self.application = application
		self.base = base_window
		self.api = api
		self.cursor = create_cursor("pointer")
		self.css_provider = load_css("/assets/styles/home.css")
		self.box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=20,
			css_classes=["box"],
			halign=Gtk.Align.CENTER,
			valign=Gtk.Align.START,
			hexpand=True,
			vexpand=True,
		)

		from windows.titlebar_controller import TitlebarController

		self.titlebar_controller = TitlebarController(
			header_bar=self.base.header_bar, home_window=self, api=self.api
		)

	async def fetch_data(self, category: str) -> dict[str, int | dict] | None:
		"""Retrieves post listings from Reddit API.

		Args:
			category (str): Category of posts to retrieve (e.g., 'hot', 'new', 'rising')

		Returns:
			dict[str, int | dict] | None: Response containing status code and listing data
		"""
		return await self.api.retrieve_listings(category)

	async def reload_data(self) -> None:
		"""Reloads the data from Reddit API.

		This method fetches the latest posts from the Reddit API and updates
		the displayed content in the home window.
		"""
		category = store.post_sort_type[store.current_sort].lower()
		self.data = await self.fetch_data(category)

	def add_post_image(self) -> Gtk.Box:
		"""Creates a container for a post thumbnail image.

		Creates a Gtk.Box containing the post thumbnail image with appropriate
		styling and layout settings.

		Returns:
			Gtk.Box: Container holding the post thumbnail image
		"""
		post_image_box = Gtk.Box(
			css_classes=["post-image-box"],
			width_request=100,
		)
		add_style_context(post_image_box, self.css_provider)

		post_image = load_image(
			"/assets/images/reddit-placeholder.png",
			_("Reddit placeholder"),
			css_classes=["post-image"],
			css_provider=self.css_provider,
		)
		post_image_box.append(post_image)

		return post_image_box

	def add_vote_buttons(self, score: int) -> Gtk.Box:
		"""Creates upvote/downvote buttons and score display.

		Creates a vertically arranged box with upvote button, score counter,
		and downvote button with appropriate styling.

		Args:
			score (int): The post's current vote score to display

		Returns:
			Gtk.Box: Container with vote buttons and score display
		"""
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL, spacing=10, css_classes=["icon-box"]
		)
		add_style_context(box, self.css_provider)

		upvote_btn = Gtk.Button(icon_name="xyz.daimones.Telex.upvote")
		box.append(upvote_btn)

		score_count = Gtk.Label(label=_("%d") % score, css_classes=["score-count"])
		add_style_context(score_count, self.css_provider)
		box.append(score_count)

		downvote_btn = Gtk.Button(icon_name="xyz.daimones.Telex.downvote")
		box.append(downvote_btn)

		return box

	def add_post_metadata(
		self,
		title: str,
		subreddit_name: str,
		user: str,
		num_of_comments: int,
		submission_time: str,
	) -> Gtk.Box:
		"""Add widgets for post metadata.

		Creates a container with post title, submission time, author username,
		subreddit name, and action buttons for the post.

		Args:
			title (str): The post title text
			subreddit_name (str): The name of the subreddit with prefix (e.g. r/python)
			user (str): The username of the post author
			num_of_comments (int): The number of comments on the post
			submission_time (str): Formatted time since submission

		Returns:
			Gtk.Box: Container with all post metadata widgets arranged vertically
		"""
		post_metadata_box = Gtk.Box(
			css_classes=["post-metadata-box"],
			orientation=Gtk.Orientation.VERTICAL,
			valign=Gtk.Align.CENTER,
			halign=Gtk.Align.START,
		)
		add_style_context(post_metadata_box, self.css_provider)

		post_title = Gtk.Label(
			label=_("%s") % title,
			css_classes=["post-title"],
			wrap=True,
			hexpand=True,
			halign=Gtk.Align.START,
			wrap_mode=Pango.WrapMode.CHAR,
			cursor=self.cursor,
			max_width_chars=90,
		)
		add_style_context(post_title, self.css_provider)
		post_metadata_box.append(post_title)
		post_box = Gtk.Box(margin_top=5, orientation=Gtk.Orientation.HORIZONTAL)
		post_time = Gtk.Label(
			label=_("submitted %s by ") % submission_time,
			css_classes=["post-metadata"],
			halign=Gtk.Align.START,
			margin_top=5,
		)

		post_user = Gtk.Label(
			label=_("%s ") % user,
			css_classes=["post-user"],
			cursor=self.cursor,
			margin_top=5,
		)
		add_style_context(post_user, self.css_provider)

		post_text = Gtk.Label(label=_("to "), css_classes=["post-metadata"], margin_top=5)
		add_style_contexts([post_time, post_text], self.css_provider)

		post_subreddit = Gtk.Label(
			label=_("%s") % subreddit_name,
			css_classes=["post-subreddit"],
			cursor=self.cursor,
			margin_top=5,
		)
		add_style_context(post_subreddit, self.css_provider)

		append_all(post_box, [post_time, post_user, post_text, post_subreddit])

		post_metadata_box.append(post_box)

		post_action_btns_box = self.add_action_btns(num_of_comments)

		post_metadata_box.append(post_action_btns_box)

		return post_metadata_box

	def add_action_btns(self, num_of_comments: int) -> Gtk.Box:
		"""Add widgets for post action buttons.

		Creates a horizontal container with action buttons for the post,
		including comments count, share, save, hide, report, and crosspost.

		Args:
			num_of_comments (int): The number of comments to display in the first button

		Returns:
			Gtk.Box: Horizontal container with all action buttons for the post
		"""
		post_action_btns_box = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL,
			halign=Gtk.Align.START,
			margin_top=5,
		)

		labels = [
			_("%d comment%s ") % (num_of_comments, "s" if num_of_comments > 1 else ""),
			_("share "),
			_("save "),
			_("hide "),
			_("report "),
			_("crosspost "),
		]

		for label in labels:
			post = Gtk.Label(
				label=label,
				css_classes=["post-action-btn"],
				cursor=self.cursor,
				margin_top=5,
			)
			add_style_context(post, self.css_provider)

			post_action_btns_box.append(post)

		return post_action_btns_box

	def __on_box_clicked(
		self,
		_gesture: Gtk.GestureClick,
		_n_press: int,
		_x: float,
		_y: float,
		widget: Gtk.Box,
	):
		"""Handles post click events.

		Opens the post detail view when a post container is clicked by
		retrieving the post ID from the data based on the widget's name
		(which stores the index) and creating a new PostDetailWindow.

		Args:
			_gesture (Gtk.GestureClick): The click gesture that triggered the event
			_n_press (int): Number of presses that triggered the event
			_x (float): x-coordinate of the event
			_y (float): y-coordinate of the event
			widget (Gtk.Box): The post container widget that was clicked
		"""
		from windows.post_detail import PostDetailWindow

		widget.set_sensitive(False)

		index = widget.get_name()
		post_id = self.data["json"]["data"]["children"][int(index)]["data"]["id"]

		post_detail = PostDetailWindow(
			application=self.application,
			base_window=self,
			api=self.api,
			post_id=post_id,
		)
		self.application.loop.create_task(post_detail.render_page())

	async def render_page(
		self, setup_titlebar: bool = True, set_current_window: bool = False
	) -> None:
		"""Creates the main layout for the homepage with a vertical box container.

		Creates a scrollable page layout containing post containers. Each post
		container includes vote buttons, a thumbnail image, and post metadata.
		The page supports vertical scrolling.

		Args:
			setup_titlebar (bool, optional): Whether to setup the window titlebar.
				Defaults to True.
			set_current_window (bool, optional): Whether to set the current window.
				Defaults to False.

		Returns:
			None: This method does not return a value.
		"""
		spinner = Gtk.Spinner(
			spinning=True, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER
		)

		clamp = Adw.Clamp(child=spinner, maximum_size=1000)
		self.viewport = Gtk.Viewport(child=clamp)
		self.scrolled_window = Gtk.ScrolledWindow(
			child=self.viewport,
			hscrollbar_policy=Gtk.PolicyType.NEVER,
			vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
		)
		self.base.set_child(self.scrolled_window)
		self.base.maximize()
		self.base.set_visible(True)

		await self.reload_data()

		self.box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=20,
			css_classes=["box"],
			halign=Gtk.Align.CENTER,
			valign=Gtk.Align.START,
			hexpand=True,
			vexpand=True,
		)

		if set_current_window:
			set_current_window_func("home", self)

		if setup_titlebar:
			self.titlebar_controller.setup_titlebar()

		add_style_context(self.box, self.css_provider)

		for index, data in enumerate(self.data["json"]["data"]["children"]):
			post_container = Gtk.Box(
				css_classes=[
					"post-container-dark"
					if self.application.settings.get_boolean("dark-mode")
					else "post-container"
				],
				orientation=Gtk.Orientation.HORIZONTAL,
				spacing=10,
				name=str(index),
				width_request=1000,
			)
			add_style_context(post_container, self.css_provider)

			click_controller = Gtk.GestureClick()
			click_controller.connect(
				"pressed",
				lambda gesture,
				n_press,
				x,
				y,
				widget=post_container: self.__on_box_clicked(
					gesture, n_press, x, y, widget
				),
			)
			post_container.add_controller(click_controller)

			self.box.append(post_container)

			vote_btns_box = self.add_vote_buttons(data["data"]["score"])
			post_container.append(vote_btns_box)

			post_image_box = self.add_post_image()
			post_container.append(post_image_box)

			post_metadata_box = self.add_post_metadata(
				data["data"]["title"],
				data["data"]["subreddit_name_prefixed"],
				data["data"]["author"],
				data["data"]["num_comments"],
				get_submission_time(data["data"]["created_utc"]),
			)
			post_container.append(post_metadata_box)

			clamp.set_child(self.box)
