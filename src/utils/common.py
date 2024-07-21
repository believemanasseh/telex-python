"""Copyright 2022 believemanasseh.

Contains common utility functions shared across the app.
"""

import os

from gi.repository import Gtk


def load_image(
	img_path: str, alt_text: str, css_classes: list, css_provider: Gtk.CssProvider
) -> Gtk.Picture:
	"""Generate image."""
	abspath = os.path.abspath(__file__)
	post_image = Gtk.Picture(
		alternative_text=alt_text, css_classes=css_classes
	).new_for_filename(abspath[: len(abspath) - 16] + img_path)
	post_image.get_style_context().add_provider(
		css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
	)
	return post_image


def load_css(css_path) -> Gtk.CssProvider:
	"""Load css from assets file."""
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
