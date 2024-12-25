"""Copyright 2022 believemanasseh.

Window class for app's homepage
"""

import gi

gi.require_version("Gtk", "4.0")


from gi.repository import Adw, Gtk, Pango

from utils.common import (
	add_style_context,
	add_style_contexts,
	append_all,
	create_cursor,
	get_submission_time,
	load_css,
	load_image,
)
from utils.services import Reddit


class HomeWindow:
	"""Base class for homepage."""

	def __init__(self, base_window: Adw.ApplicationWindow, api: Reddit):
		"""Maximises base application window and styles base box widget."""
		self.base = base_window
		self.api = api
		self.cursor = create_cursor("pointer")

		# Fetches data from Reddit
		self.data = self.__fetch_data("new")

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
			css_classes=["post-image-box"],
			width_request=100,
		)
		add_style_context(post_image_box, self.css_provider)

		post_image = load_image(
			"/assets/images/reddit-placeholder.png",
			"Reddit placeholder",
			["post-image"],
			self.css_provider,
		)
		post_image_box.append(post_image)

		return post_image_box

	def __add_vote_buttons(self, score: int) -> Gtk.Box:
		"""Add score count and upvote/downvote buttons."""
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL, spacing=10, css_classes=["icon-box"]
		)
		add_style_context(box, self.css_provider)

		upvote_btn = Gtk.Button(icon_name="xyz.daimones.Telex.upvote")
		box.append(upvote_btn)

		score_count = Gtk.Label(label=f"{score}", css_classes=["score-count"])
		add_style_context(score_count, self.css_provider)
		box.append(score_count)

		downvote_btn = Gtk.Button(icon_name="xyz.daimones.Telex.downvote")
		box.append(downvote_btn)

		return box

	def __add_post_metadata(
		self,
		title: str,
		subreddit_name: str,
		user: str,
		num_of_comments: int,
		submission_time: str,
	) -> Gtk.Box:
		"""Add widgets for post metadata (e.g. post title, post user, post subreddit)."""
		post_metadata_box = Gtk.Box(
			css_classes=["post-metadata-box"],
			orientation=Gtk.Orientation.VERTICAL,
			valign=Gtk.Align.CENTER,
			halign=Gtk.Align.START,
		)
		add_style_context(post_metadata_box, self.css_provider)

		post_title = Gtk.Label(
			label=title,
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
			label=f"submitted {submission_time} by ",
			css_classes=["post-metadata"],
			halign=Gtk.Align.START,
			margin_top=5,
		)

		post_user = Gtk.Label(
			label=f"{user} ",
			css_classes=["post-user"],
			cursor=self.cursor,
			margin_top=5,
		)
		add_style_context(post_user, self.css_provider)

		post_text = Gtk.Label(label="to ", css_classes=["post-metadata"], margin_top=5)
		add_style_contexts([post_time, post_text], self.css_provider)

		post_subreddit = Gtk.Label(
			label=subreddit_name,
			css_classes=["post-subreddit"],
			cursor=self.cursor,
			margin_top=5,
		)
		add_style_context(post_subreddit, self.css_provider)

		append_all(post_box, [post_time, post_user, post_text, post_subreddit])

		post_metadata_box.append(post_box)

		post_action_btns_box = self.__add_action_btns(num_of_comments)

		post_metadata_box.append(post_action_btns_box)

		return post_metadata_box

	def __add_action_btns(self, num_of_comments: int) -> Gtk.Box:
		"""Add widgets for action buttons (e.g. share, save, crosspost, etc)."""
		post_action_btns_box = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL,
			halign=Gtk.Align.START,
			margin_top=5,
		)
		post_comments = Gtk.Label(
			label=f"{num_of_comments} comment{'s' if num_of_comments > 1 else ''} ",
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

	def render_page(self):
		"""Renders homepage."""
		box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL,
			spacing=20,
			css_classes=["box"],
			halign=Gtk.Align.CENTER,
			valign=Gtk.Align.START,
			hexpand=True,
			vexpand=True,
		)
		self.css_provider = load_css("/assets/styles/home.css")
		add_style_context(box, self.css_provider)

		for data in self.data["json"]["data"]["children"]:
			post_container = Gtk.Box(
				css_classes=["post-container"],
				orientation=Gtk.Orientation.HORIZONTAL,
				spacing=10,
			)
			add_style_context(post_container, self.css_provider)

			box.append(post_container)

			vote_btns_box = self.__add_vote_buttons(data["data"]["score"])
			post_container.append(vote_btns_box)

			post_image_box = self.__add_post_image()
			post_container.append(post_image_box)

			post_metadata_box = self.__add_post_metadata(
				data["data"]["title"],
				data["data"]["subreddit_name_prefixed"],
				data["data"]["author"],
				data["data"]["num_comments"],
				get_submission_time(data["data"]["created_utc"]),
			)
			post_container.append(post_metadata_box)

		viewport = Gtk.Viewport()
		viewport.set_child(box)

		scrolled_window = Gtk.ScrolledWindow(
			hscrollbar_policy=Gtk.PolicyType.NEVER,
			vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
		)
		scrolled_window.set_child(viewport)

		self.base.set_child(scrolled_window)
		self.base.maximize()
