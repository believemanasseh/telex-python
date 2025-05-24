"""Settings window module for the Telex application.

This module provides:
- PreferencesWindow: Main settings window with appearance and Reddit feed preferences.
"""

import logging

import gi

gi.require_versions({"Adw": "1", "Gio": "2.0", "GObject": "2.0"})

from gi.repository import Adw, GObject, Gio


class PreferencesWindow(Adw.PreferencesWindow):
	"""Preferences window for Telex application."""

	def __init__(self, **kwargs) -> None:
		"""Initialise the preferences window.

		Args:
			**kwargs: Arbitrary keyword arguments passed to parent class.
		"""
		# Initialise settings
		self.settings: Gio.Settings = kwargs.pop("settings")

		super().__init__(**kwargs)

		# Set window properties
		self.set_default_size(600, 450)
		self.set_title("Preferences")

		style_manager = Adw.StyleManager.get_default()

		# General Settings Page
		general_page = Adw.PreferencesPage(
			icon_name="preferences-system-symbolic", title="General"
		)
		self.add(general_page)

		# Appearance Group
		appearance_group = Adw.PreferencesGroup(title="Appearance")
		general_page.add(appearance_group)

		# Dark Mode Switch
		dark_mode_row = Adw.ActionRow(title="Dark Mode", subtitle="Use dark color scheme")
		dark_switch = Adw.SwitchRow(can_focus=False)
		dark_mode_row.add_suffix(dark_switch)
		appearance_group.add(dark_mode_row)
		self.settings.bind(
			"dark-mode", dark_switch, "active", Gio.SettingsBindFlags.DEFAULT
		)
		dark_switch.connect("notify", self.__on_dark_mode_change, style_manager)

		# Feed Settings Group
		feed_group = Adw.PreferencesGroup(title="Feed Settings")
		general_page.add(feed_group)

		# NSFW Content Switch
		nsfw_row = Adw.ActionRow(title="NSFW Content", subtitle="Show NSFW posts in feed")
		nsfw_switch = Adw.SwitchRow()
		nsfw_row.add_suffix(nsfw_switch)
		feed_group.add(nsfw_row)
		self.settings.bind(
			"show-nsfw", dark_switch, "active", Gio.SettingsBindFlags.DEFAULT
		)

	def __on_dark_mode_change(
		self,
		switch: Adw.SwitchRow,
		_pspec: GObject.ParamSpec,
		style_manager: Adw.StyleManager,
	) -> None:
		"""Callback for dark mode switch change.

		Args:
			switch: The switch that was toggled.
			_pspec: Parameter specification (unused).
			style_manager: The style manager to update.

		Returns:
			None: This method does not return a value.
		"""
		if switch.get_active():
			logging.info("Dark mode enabled")
			self.settings.set_boolean("dark-mode", True)
			style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
		else:
			logging.info("Dark mode disabled")
			self.settings.set_boolean("dark-mode", False)
			style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

		self.settings.sync()
		logging.info("Settings synced")
