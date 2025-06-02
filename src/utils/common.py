"""Utility functions for GTK widget management and UI operations.

This module provides common utility functions for:

UI Components:
- Image loading and manipulation
- CSS styling and theme management
- Cursor creation and management
- Widget container operations
- Asynchronous image loading

Time Formatting:
- Post submission time formatting
- Relative time calculations

The module aims to centralise common UI operations and provide a consistent
interface for widget styling and manipulation across the application.
"""

import os

import gi
import requests

import store

gi.require_versions({"Gdk": "4.0"})

from collections.abc import Callable, Sequence
from datetime import UTC, datetime

from gi.repository import Gdk, GdkPixbuf, Gtk

from . import _
from .constants import Seconds


def load_image(
	img_path: str,
	alt_text: str,
	can_shrink: bool = True,
	css_classes: list[str] | None = None,
	css_provider: Gtk.CssProvider | None = None,
	tooltip_text: str | None = None,
	valign: Gtk.Align = Gtk.Align.CENTER,
) -> Gtk.Picture:
	"""Load and configure an image widget from a file.

	Creates a Gtk.Picture widget from an image file with specified styling and
	layout options. Handles loading from relative paths in assets directory.

	Args:
		img_path: Relative path to image file from assets directory
		alt_text: Alternative text description of the image
		can_shrink: Whether image can shrink below natural size
		css_classes: Optional list of CSS classes to apply
		css_provider: Optional CSS provider for additional styling
		valign: Vertical alignment of image within container
		tooltip_text: Optional tooltip text for the image

	Returns:
		Gtk.Picture: Configured picture widget containing the loaded image
	"""
	abspath = os.path.abspath(__file__)
	post_image = Gtk.Picture(
		alternative_text=_("%s") % alt_text, can_shrink=can_shrink, valign=valign
	).new_for_filename(abspath[: len(abspath) - 16] + img_path)

	if css_classes:
		post_image.set_css_classes(css_classes)

	if css_provider:
		post_image.get_style_context().add_provider(
			css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)

	if tooltip_text:
		post_image.set_tooltip_text(_("%s") % tooltip_text)

	return post_image


def load_css(css_path: str) -> Gtk.CssProvider:
	"""Load and parse CSS styles from a file.

	Creates a CSS provider from a CSS file for styling GTK widgets.
	Handles relative paths from the assets directory.

	Args:
		css_path: Relative path to CSS file from assets directory

	Returns:
		Gtk.CssProvider: Configured CSS provider with loaded styles
	"""
	css_provider = Gtk.CssProvider()
	abspath = os.path.abspath(__file__)
	css_provider.load_from_path(abspath[: len(abspath) - 16] + css_path)
	return css_provider


def add_style_context(widget: Gtk.Widget, css_provider: Gtk.CssProvider) -> None:
	"""Apply CSS styles to a single widget.

	Adds a CSS provider to a widget's style context for custom styling.

	Args:
		widget: Widget to style
		css_provider: CSS provider containing styles to apply
	"""
	widget.get_style_context().add_provider(
		css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
	)


def add_style_contexts(widgets: list[Gtk.Widget], css_provider: Gtk.CssProvider) -> None:
	"""Apply CSS styles to multiple widgets.

	Adds the same CSS provider to multiple widgets' style contexts.

	Args:
		widgets: List of widgets to style
		css_provider: CSS provider containing styles to apply
	"""
	for widget in widgets:
		widget.get_style_context().add_provider(
			css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)


def create_cursor(name: str) -> Gdk.Cursor | None:
	"""Create a cursor object from a named cursor type.

	Args:
		name: Standard cursor name (e.g. 'pointer', 'text')

	Returns:
		Gdk.Cursor | None: Cursor object or None if name is invalid
	"""
	return Gdk.Cursor.new_from_name(name)


def append_all(box: Gtk.Box, widgets: list[Gtk.Widget]) -> None:
	"""Add multiple widgets to a container box.

	Appends a list of widgets to a GTK box container in sequence.

	Args:
		box: Container box to add widgets to
		widgets: List of widgets to append
	"""
	for widget in widgets:
		box.append(widget)


def load_image_from_url_async(
	url: str, callback: Callable[[GdkPixbuf.Pixbuf | None], None]
) -> None:
	"""Asynchronously download and load an image from a URL.

	Downloads image data in chunks and creates a pixbuf loader.
	Calls provided callback with resulting pixbuf when complete.

	Args:
		url: URL of image to download
		callback: Function to call with loaded pixbuf or None on error

	Raises:
		requests.RequestException: If download fails
	"""

	def on_data_received(loader: GdkPixbuf.PixbufLoader, data: Sequence[int]):
		loader.write(data)

	def on_finished(loader: GdkPixbuf.PixbufLoader):
		pixbuf = loader.get_pixbuf()
		callback(pixbuf)

	loader = GdkPixbuf.PixbufLoader()
	loader.connect("data", on_data_received)
	loader.connect("area-prepared", on_finished)

	try:
		response = requests.get(url, stream=True, timeout=30)
		response.raise_for_status()
		for chunk in response.iter_content(1024):
			loader.write(chunk)
		loader.close()
	except requests.RequestException:
		callback(None)


def create_image_widget(pixbuf: GdkPixbuf.Pixbuf | None = None) -> None:
	"""Create an image widget from a pixbuf or placeholder.

	Creates a Gtk.Picture widget either from provided pixbuf or
	falls back to a placeholder image if pixbuf is None.

	Args:
		pixbuf: Optional pixbuf to create image from
	"""
	if pixbuf:
		Gtk.Picture.new_for_pixbuf(pixbuf)
		return

	# Creates placeholder image
	abspath = os.path.abspath(__file__)
	Gtk.Picture(alternative_text=_("placeholder img")).new_for_filename(
		abspath[: len(abspath) - 16] + "/assets/images/placeholder.jpg"
	)


def get_submission_time(utc_timestamp: int) -> str:
	"""Format a UTC timestamp into a relative time string.

	Converts a UTC timestamp into a human-readable relative time
	(e.g. "5 minutes ago", "2 hours ago", "3 days ago").

	Args:
		utc_timestamp: UTC timestamp in seconds since epoch

	Returns:
		str: Formatted relative time string
	"""
	current_time = datetime.now(tz=UTC)
	event_time = datetime.fromtimestamp(utc_timestamp, tz=UTC)
	time_difference = current_time - event_time
	total_seconds = abs(time_difference.total_seconds())

	# Determine the scale -- minutes, hours, days, or weeks
	if total_seconds < Seconds.MINUTE:
		return _("Less than a minute ago")

	if total_seconds < Seconds.HOUR:  # 60 seconds * 60 minutes
		minutes = int(total_seconds // Seconds.MINUTE)
		return _("{minutes} minute{s} ago").format(
			minutes=minutes, s="s" if minutes > 1 else ""
		)

	if total_seconds < Seconds.DAY:  # 3600 seconds * 24 hours
		hours = int(total_seconds // Seconds.HOUR)
		return _("{hours} hour{s} ago").format(hours=hours, s="s" if hours > 1 else "")

	if total_seconds < Seconds.WEEK:  # 86400 seconds * 7 days
		days = int(total_seconds // Seconds.DAY)
		return _("{days} day{s} ago").format(days=days, s="s" if days > 1 else "")

	weeks = int(total_seconds // Seconds.WEEK)

	return _("{weeks} week{s} ago").format(weeks=weeks, s="s" if weeks > 1 else "")


def set_current_window(window_name: str, widget: Gtk.Widget) -> None:
	"""Set the current window for the application.

	Sets the current window to be used for GTK operations.

	Args:
		window_name: The name of the current window.
		widget: The GTK window instance to set as current.

	Returns:
		None: This function does not return a value.
	"""
	if window_name == "auth":
		store.current_window = window_name
		store.auth_window = widget
	elif window_name == "home":
		store.current_window = window_name
		store.home_window = widget
	elif window_name == "post_detail":
		store.current_window = window_name
		store.post_detail_window = widget
	else:
		store.current_window = window_name
		store.profile_window = widget
