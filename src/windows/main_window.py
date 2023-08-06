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

from gi.repository import Adw, Gtk


@Gtk.Template(resource_path="/org/gnome/Telex/main.ui")
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'MainWindow'

    label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("PyTelex")
        self.set_default_size(300, 600)
        Gtk.TextTag.background = 0000
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(self.box)
        self.box.set_margin_top(250)
        self.login_btn = Gtk.Button(label="Login")
        self.register_btn = Gtk.Button(label="Register")
        self.box.append(self.login_btn)
        self.box.append(self.register_btn)
        self.login_btn.connect("clicked", self.logisn)
        self.register_btn.connect("clicked", self.register)

    def login(self, widget: Gtk.Button) -> None:
        print("Logged in")
        print(widget, "widget")
        win = Gtk.AboutDialog(
            version="1.0",
            authors=["Believe Manasseh"],
            program_name="PyTelex"
        )
        win.present()

    def register(self, widget: Gtk.Button) -> None:
        print("Signed up")


