"""Copyright 2022 believemanasseh.

Contains common utility functions shared across the app.
"""

import os

from gi.repository import Gtk


def generate_image(
	img_path: str, alt_text: str, css_classes: list, css_provider: Gtk.CssProvider
) -> Gtk.Picture:
	"""Generate image."""
	post_image = Gtk.Picture(
		alternative_text=alt_text, css_classes=css_classes
	).new_for_filename(os.path.dirname(__file__)[:27] + img_path)
	post_image.get_style_context().add_provider(
		css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
	)
	return post_image


def load_css(css_path) -> Gtk.CssProvider:
	"""Load css from assets file."""
	css_provider = Gtk.CssProvider()
	css_provider.load_from_path(os.path.dirname(__file__)[:27] + css_path)
	return css_provider
