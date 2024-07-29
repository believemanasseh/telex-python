"""Copyright 2022 believemanasseh.

Contains common utility functions shared across the app.
"""

import os
from collections.abc import Callable, Sequence

import requests
from gi.repository import Gdk, GdkPixbuf, Gtk


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
	"""Add multiple css style contexts to widget."""
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
