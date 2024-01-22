# window.py
#
# Copyright 2022 manasseh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from .main import Gtk


class Window(Gtk.ApplicationWindow):
    __gtype_name__ = "MainWindow"

    def __init__(self, application, **kwargs):
        super().__init__(application=application, **kwargs)
        self.set_title("Telex")
        self.set_default_size(300, 600)
        Gtk.TextTag.background = 0000
        self.stack = Gtk.Stack()
        self.box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=10, width_request=200
        )
        self.set_child(self.box)
        self.box.set_halign(Gtk.Align.CENTER)
        self.box.set_valign(Gtk.Align.CENTER)
        self.login_btn = Gtk.Button(label="Login")
        self.login_btn.set_name("login-btn")
        self.register_btn = Gtk.Button.new()
        self.register_btn.set_label(label="Register")
        self.register_btn.set_name("register-btn")
        css_provider = Gtk.CssProvider()
        css = """
            #register-btn, #login-btn {
                background-color: #000000;
                color: #FFFFFF;
            }
        """
        css_provider.load_from_data(css.encode())
        login_context = self.login_btn.get_style_context()
        register_context = self.register_btn.get_style_context()
        login_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        register_context.add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.box.append(self.login_btn)
        self.box.append(self.register_btn)
        self.stack.add_child(self.box)
        self.login_btn.connect("clicked", self.on_login)
        self.register_btn.connect("clicked", self.on_register)

    def on_register(self, widget: Gtk.Widget):
        data = {
            "button_label": "Register",
            "text": "Already a user?",
            "event_handler": self.on_login,
        }
        self.load_page(data)

    def on_login(self, widget: Gtk.Widget):
        data = {
            "button_label": "Login",
            "text": "Not yet registered?",
            "event_handler": self.on_register,
        }
        self.load_page(data)

    def set_button_color(self, button: Gtk.Button, label: str):
        button.set_label(label)
        button.set_name("btn")
        css_provider = Gtk.CssProvider()
        css = """
            #btn {
                background-color: #000000;
                color: #FFFFFF;
            }
        """
        css_provider.load_from_data(css.encode())
        context = button.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def load_page(self, data):
        self.box.set_visible(False)
        box = Gtk.Box(
            name="login",
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
        )
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        self.set_child(box)
        self.email_field = Gtk.Entry(placeholder_text="Enter email address")
        self.password_field = Gtk.Entry(placeholder_text="Enter password")
        box.append(self.email_field)
        box.append(self.password_field)
        button = self.login_btn.new()
        self.set_button_color(button, data["button_label"])
        box.append(button)
        text = Gtk.Text(text=data["text"])
        link_btn = Gtk.LinkButton(label="click here")
        link_btn.connect("clicked", data["event_handler"])
        info_box = Gtk.Box(name="info", orientation=Gtk.Orientation.HORIZONTAL)
        info_box.append(text)
        info_box.append(link_btn)
        box.append(info_box)
        box.set_visible(True)
