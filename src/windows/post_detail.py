"""Window class for post detail widgets.

Thism module provides:
- PostDetailWindow: window class for post detail
"""

import gi

gi.require_versions({"Gtk": "4.0", "Adw": "1"})

from gi.repository import Adw, Gtk

from services import Reddit
from utils.common import add_style_contexts, get_submission_time, load_css, load_image
from windows.home import HomeWindow


class PostDetailWindow(Gtk.ApplicationWindow):
	"""Entry window class for post detail."""

	def __init__(self, base_window: HomeWindow, api: Reddit, post_id: str):
		"""Initialises window for post details."""
		self.base = base_window
		self.api = api
		self.css_provider = load_css("/assets/styles/post_detail.css")

		self.data = self.__fetch_data(post_id)
		self.box = Gtk.Box(
			css_classes=["box"],
			orientation=Gtk.Orientation.VERTICAL,
			halign=Gtk.Align.CENTER,
			valign=Gtk.Align.START,
			hexpand=True,
			vexpand=True,
		)

	def __fetch_data(self, post_id: str) -> dict[str, int | dict] | None:
		"""Retrieves comments."""
		return self.api.retrieve_comments(post_id)

	def __load_comments(self, parent_box: Gtk.Box, comments_data: list[dict]) -> None:
		"""Loads comments.

		Args:
		  parent_box: Gtk.Box instance
		  comments_data: List of comments
		"""
		data = comments_data["data"]["children"][0]

		box = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=10,
		)

		grid = Gtk.Grid(column_spacing=30)
		grid.insert_row(0)
		grid.insert_column(0)
		grid.insert_column(1)

		post_image = load_image(
			"/assets/images/reddit-placeholder.png",
			"Reddit placeholder",
			css_provider=self.css_provider,
		)
		grid.attach(post_image, 0, 0, 1, 1)

		grid_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

		if "author" in data["data"]:
			author = data["data"]["author"]
			body = data["data"]["body"]
			replies = data["data"]["replies"]

			author_label = Gtk.Label(label=author, halign=Gtk.Align.START)
			body_label = Gtk.Label(label=body, halign=Gtk.Align.START)
			grid_box.append(author_label)
			grid_box.append(body_label)

			grid.attach(grid_box, 1, 0, 1, 1)

			parent_box.append(grid)

			if replies:
				self.__load_comments(box, replies)

	def render_page(self):
		"""Renders window."""
		post_data = self.data["json"][0]["data"]["children"][0]

		post_container = Gtk.Box(
			css_classes=["post-container"],
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=10,
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
		add_style_contexts([self.box, post_container], self.css_provider)

		self.base.viewport.set_child(self.box)
		self.base.base.set_titlebar(
			Adw.HeaderBar(
				decoration_layout="close,maximize,minimize", show_back_button=True
			)
		)
		self.base.scrolled_window.set_child(self.base.viewport)
		self.base.scrolled_window.set_child_visible(True)

		# Load comments
		comments_data = self.data["json"][1:]
		for comments in comments_data:
			self.__load_comments(self.box, comments)
