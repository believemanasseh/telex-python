"""Settings window module for the Telex application.

This module provides:
- PreferencesWindow: Main settings window with appearance and Reddit feed preferences.
"""

import gi

gi.require_versions({"Gtk": "4.0", "Adw": "1"})

from gi.repository import Adw


class PreferencesWindow(Adw.PreferencesWindow):
	"""Preferences window for Telex application."""

	def __init__(self, **kwargs):
		"""Initialise the preferences window.

		Args:
			**kwargs: Arbitrary keyword arguments passed to parent class.
		"""
		super().__init__(**kwargs)

		# Set window properties
		self.set_default_size(600, 450)
		self.set_title("Preferences")

		# General Settings Page
		general_page = Adw.PreferencesPage()
		general_page.set_title("General")
		general_page.set_icon_name("preferences-system-symbolic")
		self.add(general_page)

		# Appearance Group
		appearance_group = Adw.PreferencesGroup()
		appearance_group.set_title("Appearance")
		general_page.add(appearance_group)

		# Dark Mode Switch
		dark_mode_row = Adw.ActionRow()
		dark_mode_row.set_title("Dark Mode")
		dark_mode_row.set_subtitle("Use dark color scheme")
		dark_switch = Adw.SwitchRow()
		dark_mode_row.add_suffix(dark_switch)
		appearance_group.add(dark_mode_row)

		# Feed Settings Group
		feed_group = Adw.PreferencesGroup()
		feed_group.set_title("Feed Settings")
		general_page.add(feed_group)

		# NSFW Content Switch
		nsfw_row = Adw.ActionRow()
		nsfw_row.set_title("NSFW Content")
		nsfw_row.set_subtitle("Show NSFW posts in feed")
		nsfw_switch = Adw.SwitchRow()
		nsfw_row.add_suffix(nsfw_switch)
		feed_group.add(nsfw_row)
