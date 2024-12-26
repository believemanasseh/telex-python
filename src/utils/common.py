"""Common utility functions shared across the app.

This module provides:
- load_image: function to load image files
- load_css: function to load css files
- add_style_context: function to add style context to widget
- add_style_contexts: function to add css style contexts to multiple widgets
- create_cursor: function to create cursor from name
- append_all: function to add multiple widgets to box
- load_image_from_url_async: function to download image asynchronously from url
- create_image_widget: function to create picture widget
- get_submission_time: function to retrieve post submission time
"""

import os
from collections.abc import Callable, Sequence
from datetime import datetime, timezone

import requests
from gi.repository import Gdk, GdkPixbuf, Gtk

from .constants import Seconds


def load_image(
	img_path: str, alt_text: str, css_classes: list[str], css_provider: Gtk.CssProvider
) -> Gtk.Picture:
	"""Load image file from assets directory."""
	abspath = os.path.abspath(__file__)
	post_image = Gtk.Picture(
		alternative_text=alt_text, css_classes=css_classes
	).new_for_filename(abspath[: len(abspath) - 16] + img_path)
	post_image.get_style_context().add_provider(
		css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
	)
	return post_image


def load_css(css_path) -> Gtk.CssProvider:
	"""Load css file from assets directory."""
	css_provider = Gtk.CssProvider()
	abspath = os.path.abspath(__file__)
	css_provider.load_from_path(abspath[: len(abspath) - 16] + css_path)
	return css_provider


def add_style_context(widget: Gtk.Widget, css_provider: Gtk.CssProvider) -> None:
	"""Add css style context to widget."""
	widget.get_style_context().add_provider(
		css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
	)


def add_style_contexts(widgets: list[Gtk.Widget], css_provider: Gtk.CssProvider) -> None:
	"""Add css style context to multiple widgets."""
	for widget in widgets:
		widget.get_style_context().add_provider(
			css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)


def create_cursor(name: str) -> Gdk.Cursor | None:
	"""Creates cursor from name."""
	return Gdk.Cursor.new_from_name(name)


def append_all(box: Gtk.Box, widgets: list[Gtk.Widget]) -> None:
	"""Append multiple widgets to box."""
	for widget in widgets:
		box.append(widget)


def load_image_from_url_async(
	url: str, callback: Callable[[GdkPixbuf.Pixbuf | None], None]
) -> None:
	"""Download image asynchronously from a url."""

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


def create_image_widget(pixbuf) -> None:
	"""Creates the image widget."""
	if pixbuf:
		Gtk.Picture.new_for_pixbuf(pixbuf)
		return

	# Creates placeholder image
	abspath = os.path.abspath(__file__)
	Gtk.Picture(alternative_text="placeholder img").new_for_filename(
		abspath[: len(abspath) - 16] + "/assets/images/placeholder.jpg"
	)


def get_submission_time(utc_timestamp: int) -> str:
	"""Returns submission time of post."""
	current_time = datetime.now(tz=timezone.utc)
	event_time = datetime.fromtimestamp(utc_timestamp, tz=timezone.utc)
	time_difference = current_time - event_time
	total_seconds = abs(time_difference.total_seconds())

	# Determine the scale -- minutes, hours, days, or weeks
	if total_seconds < Seconds.MINUTE:
		return "Less than a minute ago"

	if total_seconds < Seconds.HOUR:  # 60 seconds * 60 minutes
		minutes = int(total_seconds // Seconds.MINUTE)
		return f"{minutes} minute{'s' if minutes > 1 else ''} ago"

	if total_seconds < Seconds.DAY:  # 3600 seconds * 24 hours
		hours = int(total_seconds // Seconds.HOUR)
		return f"{hours} hour{'s' if hours > 1 else ''} ago"

	if total_seconds < Seconds.WEEK:  # 86400 seconds * 7 days
		days = int(total_seconds // Seconds.DAY)
		return f"{days} day{'s' if days > 1 else ''} ago"

	weeks = int(total_seconds // Seconds.WEEK)

	return f"{weeks} week{'s' if weeks > 1 else ''} ago"
