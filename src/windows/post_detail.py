"""Post detail view implementation for the Reddit client application.

This module implements the detailed view of Reddit posts and their comments. It handles:

- Fetching and displaying full post content
- Loading and rendering nested comment threads
- Comment voting and reply interactions
- Post metadata display (author, score, timestamp)
- Navigation back to the main feed
- Hierarchical comment display with proper indentation
- Dynamic content loading and formatting

The module provides a rich post viewing experience while maintaining a clean,
native-looking interface consistent with the application's design.

Classes:
    PostDetailWindow: Main window class implementing the post detail view
"""

import gi

import store

gi.require_versions({"Gtk": "4.0", "Adw": "1"})

from gi.repository import Adw, Gtk

from app import Telex
from services import Reddit
from utils import _
from utils.common import (
	add_style_contexts,
	get_submission_time,
	load_css,
	load_image,
	set_current_window,
)
from windows.home import HomeWindow


class PostDetailWindow(Gtk.ApplicationWindow):
	"""Window class for displaying detailed post content and comments.

	This class is responsible for retrieving and displaying a Reddit post's
	detailed content including the post itself and its comment tree. It shows
	the post at the top and nested comments below it with appropriate
	indentation levels to indicate reply hierarchy. Comments include metadata
	such as author, score, and content, along with action buttons.
	"""

	def __init__(
		self,
		application: Telex,
		base_window: HomeWindow,
		api: Reddit,
		post_id: str,
	):
		"""Initialises window for post details.

		Args:
		    application (Adw.Application): The parent GTK application
		    base_window (HomeWindow): Parent window instance containing the main
		        application window
		    api (Reddit): Reddit API instance for fetching post data
		    post_id (str): Unique identifier of the Reddit post to display

		Attributes:
		    base (HomeWindow): Reference to parent window
			api (Reddit): Reddit API instance for data operations
			application (Adw.Application): The parent GTK application
		    css_provider: CSS styles provider for the window
			post_id (str): Unique identifier for the Reddit post
		    box (Gtk.Box): Vertical container for post content
		    clamp (Adw.Clamp): Width constraint container
		"""
		set_current_window("post_detail", self)
		super().__init__(application=application)
		self.base = base_window
		self.api = api
		self.application = application
		self.css_provider = load_css("/assets/styles/post_detail.css")
		self.post_id = post_id
		self.box = Gtk.Box(
			css_classes=["box"],
			orientation=Gtk.Orientation.VERTICAL,
			valign=Gtk.Align.START,
			vexpand=True,
		)
		self.clamp = Adw.Clamp(child=self.box, maximum_size=1000)

		if not store.back_btn_set:
			self.base.titlebar_controller.add_back_button()
			store.back_btn_set = True

		self.base.titlebar_controller.inject_post_detail(self)

	async def fetch_data(self, post_id: str) -> dict[str, int | dict]:
		"""Retrieves post details and comments from Reddit API.

		Calls the Reddit API to get the complete post data and its comment tree
		based on the provided post ID.

		Args:
		    post_id (str): Unique identifier for the Reddit post

		Returns:
		    dict[str, int | dict]: Post and comments data dictionary
		"""
		return await self.api.retrieve_comments(post_id)

	def load_comments(
		self, parent_box: Gtk.Box, comment_data: dict, nesting_level: int = 0
	) -> None:
		"""Loads and renders comments recursively with proper nesting.

		Creates UI components for each comment including author information,
		comment content, score, and action buttons. Recursively processes reply
		chains with increased indentation to visually represent the comment hierarchy.

		Args:
		    parent_box (Gtk.Box): Container to add the comment widgets to
		    comment_data (dict): Comment data dictionary containing content and metadata
		    nesting_level (int, optional): Comment nesting level. 0 for top-level comments
		"""
		if "kind" not in comment_data or comment_data["kind"] != "t1":
			return  # Skip if not a comment

		data = comment_data.get("data", {})

		if "author" not in data or data.get("author") is None:
			return  # Skip deleted comments

		author = data["author"]
		body = data["body"]
		score = data.get("score", 0)

		# Create comment container with proper indentation
		comment_box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			valign=Gtk.Align.START,
			vexpand=True,
			spacing=8,
			margin_start=nesting_level * 30,
			margin_bottom=15,
			css_classes=[
				"comment-box-dark"
				if self.application.settings.get_boolean("dark-mode")
				else "comment-box"
			],
		)

		# Create header box for author and metadata
		header_box = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=8,
			valign=Gtk.Align.START,
			halign=Gtk.Align.START,
		)

		# Add user avatar
		avatar = load_image(
			"/assets/images/reddit-placeholder.png",
			"User avatar",
			css_classes=["comment-avatar"],
			css_provider=self.css_provider,
		)
		header_box.append(avatar)

		# Add author name
		author_label = Gtk.Label(
			label=_("%s") % author,
			halign=Gtk.Align.START,
			css_classes=["comment-author"],
		)
		header_box.append(author_label)

		# Add score
		score_label = Gtk.Label(
			label=_("· %d points") % score,
			halign=Gtk.Align.START,
			css_classes=[
				"comment-score-dark"
				if self.application.settings.get_boolean("dark-mode")
				else "comment-score"
			],
		)
		header_box.append(score_label)

		# Add body text
		body_label = Gtk.Label(
			label=_("%s") % body,
			halign=Gtk.Align.START,
			max_width_chars=160,
			wrap=True,
			css_classes=["comment-body"],
		)

		# Add actions bar
		actions_box = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=12,
			valign=Gtk.Align.START,
			halign=Gtk.Align.START,
			margin_top=5,
		)

		# Add reply button
		reply_button = Gtk.Button(
			label=_("Reply"),
			css_classes=["comment-action-button"],
		)
		actions_box.append(reply_button)

		# Add upvote/downvote buttons
		vote_box = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=5,
			valign=Gtk.Align.CENTER,
		)
		upvote_btn = Gtk.Button(icon_name="xyz.daimones.Telex.upvote")
		downvote_btn = Gtk.Button(icon_name="xyz.daimones.Telex.downvote")
		vote_box.append(upvote_btn)
		vote_box.append(downvote_btn)
		actions_box.append(vote_box)

		# Assemble comment box
		comment_box.append(header_box)
		comment_box.append(body_label)
		comment_box.append(actions_box)

		# Add comment to parent box
		parent_box.append(comment_box)

		# Add style contexts
		add_style_contexts(
			[comment_box, author_label, body_label, score_label, avatar, reply_button],
			self.css_provider,
		)

		# Process replies recursively if they exist
		replies_data = data.get("replies", {})
		if replies_data and "data" in replies_data:
			children = replies_data["data"].get("children", [])
			for reply in children:
				self.load_comments(parent_box, reply, nesting_level + 1)

	async def render_page(self):
		"""Renders the post detail page with post content and comments.

		Builds the complete UI for the post detail view including:
		- The post itself (reusing components from HomeWindow)
		- A comments header
		- The nested comment tree with proper indentation

		This method sets up the viewport and makes the content visible in the
		scrolled window from the base HomeWindow instance.
		"""
		data = await self.fetch_data(self.post_id)
		post_data = data["json"][0]["data"]["children"][0]

		post_container = Gtk.Box(
			css_classes=[
				"post-container-dark"
				if self.application.settings.get_boolean("dark-mode")
				else "post-container"
			],
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=10,
			width_request=1000,
			visible=True,
		)

		self.box.append(post_container)

		vote_btns_box = self.base.add_vote_buttons(post_data["data"]["score"])
		post_container.append(vote_btns_box)

		post_image_box = self.base.add_post_image()
		post_container.append(post_image_box)

		post_metadata_box = self.base.add_post_metadata(
			post_data["data"]["title"],
			post_data["data"]["subreddit_name_prefixed"],
			post_data["data"]["author"],
			post_data["data"]["num_comments"],
			get_submission_time(post_data["data"]["created_utc"]),
		)
		post_container.append(post_metadata_box)

		self.base.viewport.set_child(self.clamp)
		self.base.scrolled_window.set_child(self.base.viewport)

		# Create a comments section header
		comments_header = Gtk.Label(
			label="Comments",
			halign=Gtk.Align.START,
			margin_top=20,
			margin_bottom=10,
			margin_start=10,
			css_classes=["comments-header"],
		)
		self.box.append(comments_header)

		# Create a comments container
		comments_container = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=10,
			valign=Gtk.Align.START,
			halign=Gtk.Align.CENTER,
			width_request=1000,
		)
		self.box.append(comments_container)
		add_style_contexts(
			[self.box, post_container, comments_header, comments_container],
			self.css_provider,
		)

		# Load comments
		comments_data = data["json"][1]["data"]["children"]
		for comment in comments_data:
			self.load_comments(comments_container, comment, 0)
