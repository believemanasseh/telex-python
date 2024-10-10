"""Copyright 2022 believemanasseh.

Window class for app's homepage
"""

import gi

gi.require_version("Gtk", "4.0")


from gi.repository import Gtk, Pango

from utils.common import (
	add_style_context,
	add_style_contexts,
	append_all,
	create_cursor,
	load_css,
	load_image,
)
from utils.services import Reddit


class HomeWindow:
	"""Base class for homepage."""

	def __init__(
		self, base_window: Gtk.ApplicationWindow, base_box: Gtk.Box, api: Reddit
	):
		"""Maximises base application window and styles base box widget."""
		self.base = base_window
		self.box = base_box
		self.api = api
		self.cursor = create_cursor("pointer")
		self.css_provider = load_css("/assets/styles/home.css")
		self.box.set_valign(Gtk.Align.START)
		add_style_context(self.box, self.css_provider)
		self.data = self.__fetch_data("new")
		self.base.maximize()

	def render_page(self):
		"""Renders homepage."""
		post_container = Gtk.Box(
			css_classes=["post-container"],
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=10,
		)
		add_style_context(post_container, self.css_provider)

		self.box.append(post_container)

		vote_btns_box = self.__add_vote_buttons()
		post_container.append(vote_btns_box)

		post_image_box = self.__add_post_image()
		post_container.append(post_image_box)

		post_metadata_box = self.__add_post_metadata()
		post_container.append(post_metadata_box)

	def __get_categories(self):
		"""Return all Reddit post categories."""
		return [
			"new",
			"popular",
			"random",
			"sort",
			"top",
			"rising",
			"hot",
			"controversial",
		]

	def __fetch_data(self, category) -> dict[str, int | dict] | None:
		return self.api.retrieve_listings(category)

	def __add_post_image(self) -> Gtk.Box:
		"""Add post image."""
		post_image_box = Gtk.Box(
			css_classes=["post-image-box"], cursor=self.cursor, height_request=100
		)
		add_style_context(post_image_box, self.css_provider)

		post_image = load_image(
			"/assets/images/light.jpg", "Light", ["post-image"], self.css_provider
		)
		post_image_box.append(post_image)

		return post_image_box

	def __add_vote_buttons(self) -> Gtk.Box:
		"""Add likes count and upvote/downvote buttons."""
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL, spacing=10, css_classes=["icon-box"]
		)
		add_style_context(box, self.css_provider)

		upvote_btn = Gtk.Button(
			icon_name="xyz.daimones.Telex.upvote-btn", cursor=self.cursor
		)
		box.append(upvote_btn)

		likes_count = Gtk.Label(label="6000", css_classes=["likes-count"])
		add_style_context(likes_count, self.css_provider)
		box.append(likes_count)

		downvote_btn = Gtk.Button(
			icon_name="xyz.daimones.Telex.downvote-btn", cursor=self.cursor
		)
		box.append(downvote_btn)

		return box

	def __add_post_metadata(self) -> Gtk.Box:
		"""Add widgets for post metadata (e.g. post title, post user, post subreddit)."""
		post_metadata_box = Gtk.Box(
			css_classes=["post-metadata-box"],
			orientation=Gtk.Orientation.VERTICAL,
			valign=Gtk.Align.CENTER,
			halign=Gtk.Align.START,
		)
		add_style_context(post_metadata_box, self.css_provider)

		post_title = Gtk.Label(
			label="This is the first post from the Reddit API client and whatever the #",
			css_classes=["post-title"],
			wrap=True,
			hexpand=True,
			wrap_mode=Pango.WrapMode.CHAR,
			cursor=self.cursor,
		)
		add_style_context(post_title, self.css_provider)
		post_metadata_box.append(post_title)
		post_box = Gtk.Box(margin_top=5, orientation=Gtk.Orientation.HORIZONTAL)
		post_time = Gtk.Label(
			label="submitted 23 hours ago by ",
			css_classes=["post-metadata"],
			halign=Gtk.Align.START,
			margin_top=5,
		)

		post_user = Gtk.Label(
			label="FriendlyBabyFrog ",
			css_classes=["post-user"],
			cursor=self.cursor,
			margin_top=5,
		)
		add_style_context(post_user, self.css_provider)

		post_text = Gtk.Label(label="to ", css_classes=["post-metadata"], margin_top=5)
		add_style_contexts([post_time, post_text], self.css_provider)

		post_subreddit = Gtk.Label(
			label="r/mildlyinteresting",
			css_classes=["post-subreddit"],
			cursor=self.cursor,
			margin_top=5,
		)
		add_style_context(post_subreddit, self.css_provider)

		append_all(post_box, [post_time, post_user, post_text, post_subreddit])

		post_metadata_box.append(post_box)

		post_action_btns_box = self.__add_action_btns()

		post_metadata_box.append(post_action_btns_box)

		return post_metadata_box

	def __add_action_btns(self) -> Gtk.Box:
		"""Add widgets for action buttons (e.g. share, save, crosspost, etc)."""
		post_action_btns_box = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL,
			halign=Gtk.Align.START,
			margin_top=5,
		)
		post_comments = Gtk.Label(
			label="3274 comments ",
			css_classes=["post-action-btn"],
			cursor=self.cursor,
			margin_top=5,
		)

		post_share = Gtk.Label(
			label="share ",
			css_classes=["post-action-btn"],
			cursor=self.cursor,
			margin_top=5,
		)

		post_save = Gtk.Label(
			label="save ",
			css_classes=["post-action-btn"],
			cursor=self.cursor,
			margin_top=5,
		)

		post_hide = Gtk.Label(
			label="hide ",
			css_classes=["post-action-btn"],
			cursor=self.cursor,
			margin_top=5,
		)

		post_report = Gtk.Label(
			label="report ",
			css_classes=["post-action-btn"],
			cursor=self.cursor,
			margin_top=5,
		)

		post_crosspost = Gtk.Label(
			label="crosspost ",
			css_classes=["post-action-btn"],
			cursor=self.cursor,
			margin_top=5,
		)

		add_style_contexts(
			[
				post_comments,
				post_share,
				post_save,
				post_hide,
				post_report,
				post_crosspost,
			],
			self.css_provider,
		)
		post_action_btns_box.append(post_comments)
		post_action_btns_box.append(post_share)
		post_action_btns_box.append(post_save)
		post_action_btns_box.append(post_hide)
		post_action_btns_box.append(post_report)
		post_action_btns_box.append(post_crosspost)

		return post_action_btns_box
