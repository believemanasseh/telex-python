"""Window class for post detail widgets.

Thism module provides:
- PostDetailWindow: window class for post detail
"""

import gi

gi.require_versions({"Gtk": "4.0", "Adw": "1"})

from gi.repository import Gtk

from services import Reddit
from utils.common import get_submission_time
from windows.home import HomeWindow


class PostDetailWindow(Gtk.ApplicationWindow):
	"""Entry window class for post detail."""

	def __init__(self, base: HomeWindow, api: Reddit, post_id: str):
		"""Initialises window for post details."""
		self.base = base
		self.api = api

		self.data = self.__fetch_data(post_id)["json"]["data"]["children"][0]

	def __fetch_data(self, post_id) -> dict[str, int | dict] | None:
		return self.api.retrieve_comments(post_id)

	def render_page(self):
		"""Renders window."""
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		post_container = Gtk.Box(
			css_classes=["post-container"],
			orientation=Gtk.Orientation.HORIZONTAL,
			spacing=10,
		)

		box.append(post_container)

		vote_btns_box = self.base.add_vote_buttons(self.data["data"]["score"])
		post_container.append(vote_btns_box)

		post_image_box = self.base.add_post_image()
		post_container.append(post_image_box)

		post_metadata_box = self.base.add_post_metadata(
			self.data["data"]["title"],
			self.data["data"]["subreddit_name_prefixed"],
			self.data["data"]["author"],
			self.data["data"]["num_comments"],
			get_submission_time(self.data["data"]["created_utc"]),
		)
		post_container.append(post_metadata_box)

		self.base.viewport.set_child(box)
		self.base.scrolled_window.set_child(self.base.viewport)
