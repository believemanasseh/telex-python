"""Copyright 2022 believemanasseh.

Window class for app's homepage
"""

import gi

gi.require_version("Gtk", "4.0")


from gi.repository import Gdk, Gtk

from utils.common import add_style_context, add_style_contexts, load_css, load_image


class HomeWindow:
	"""Base class for homepage."""

	def __init__(self, base_window: Gtk.ApplicationWindow, base_box: Gtk.Box):
		"""Maximises base application window and styles base box widget."""
		self.base = base_window
		self.box = base_box
		self.css_provider = load_css("/assets/styles/home.css")
		self.box.set_valign(Gtk.Align.START)
		add_style_context(self.box, self.css_provider)
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

		# Add likes count and upvote/downvote buttons to navigation box
		navigation_box = Gtk.Box(
			orientation=Gtk.Orientation.VERTICAL, spacing=10, css_classes=["icon-box"]
		)
		add_style_context(navigation_box, self.css_provider)

		upvote_btn = Gtk.Button(icon_name="upvote-btn")
		navigation_box.append(upvote_btn)

		likes_count = Gtk.Label(label=6000, css_classes=["likes-count"])
		add_style_context(likes_count, self.css_provider)
		navigation_box.append(likes_count)

		downvote_btn = Gtk.Button(icon_name="downvote-btn")
		navigation_box.append(downvote_btn)

		post_container.append(navigation_box)

		# Add image to post container
		post_image_box = Gtk.Box(
			css_classes=["post-image-box"],
		)
		post_image = load_image(
			"/assets/images/light.jpg", "Light", ["post-image"], self.css_provider
		)
		post_image_box.append(post_image)

		post_container.append(post_image_box)

		# Add post title and necessary metadata
		# Metadata includes post title, post user, post subreddit, post
		# submission date etc
		post_details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		cursor = Gdk.Cursor.new_from_name("pointer")
		post_title = Gtk.Label(
			label="This is the first post from the Reddit API client and whatever the fuck that means I don't give a fuck mans fuck me.",
			css_classes=["post-title"],
			wrap=True,
			valign=Gtk.Align.START,
			cursor=cursor,
		)
		add_style_context(post_title, self.css_provider)
		post_details_box.append(post_title)

		post_metadata_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		post_metadata = Gtk.Label(
			label="submitted 23 hours ago by ",
			css_classes=["post-metadata"],
			halign=Gtk.Align.START,
			margin_top=5,
		)
		post_user = Gtk.Label(
			label="FriendlyBabyFrog ",
			css_classes=["post-user"],
			cursor=cursor,
			margin_top=5,
		)
		add_style_context(post_user, self.css_provider)
		post_metadata2 = Gtk.Label(label="to ", margin_top=5)
		post_subreddit = Gtk.Label(
			label="r/mildlyinteresting",
			css_classes=["post-subreddit"],
			cursor=cursor,
			margin_top=5,
		)
		add_style_context(post_subreddit, self.css_provider)
		post_metadata_box.append(post_metadata)
		post_metadata_box.append(post_user)
		post_metadata_box.append(post_metadata2)
		post_metadata_box.append(post_subreddit)

		post_action_btns_box = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL,
			halign=Gtk.Align.START,
			css_classes=["post-action-btns"],
		)
		post_comments = Gtk.Label(
			use_markup=True,
			css_classes=["post-action-btn"],
			cursor=cursor,
			margin_top=5,
		)
		post_comments.set_text_with_mnemonic("_3274 comments_ ")

		post_share = Gtk.Label(
			use_markup=True,
			css_classes=["post-action-btn"],
			cursor=cursor,
			margin_top=5,
		)
		post_share.set_text_with_mnemonic("_share_ ")

		post_save = Gtk.Label(
			use_markup=True,
			css_classes=["post-action-btn"],
			cursor=cursor,
			margin_top=5,
		)
		post_save.set_text_with_mnemonic("_save_ ")

		post_hide = Gtk.Label(
			use_markup=True,
			css_classes=["post-action-btn"],
			cursor=cursor,
			margin_top=5,
		)
		post_hide.set_text_with_mnemonic("_hide_ ")

		post_report = Gtk.Label(
			use_markup=True,
			css_classes=["post-action-btn"],
			cursor=cursor,
			margin_top=5,
		)
		post_report.set_text_with_mnemonic("_report_ ")

		post_crosspost = Gtk.Label(
			use_markup=True,
			css_classes=["post-action-btn"],
			cursor=cursor,
			margin_top=5,
		)
		post_crosspost.set_text_with_mnemonic("_crosspost_ ")

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

		post_details_box.append(post_metadata)
		post_details_box.append(post_metadata_box)
		post_container.append(post_details_box)
		post_container.append(post_action_btns_box)
