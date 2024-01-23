"""Copyright 2022 believemanasseh.

Application's entry window class. Contains logic for login and registration
"""

from gi.repository import Gtk

from windows import Home


class Window(Gtk.ApplicationWindow):
    """Authentication window for registration and login."""

    __gtype_name__ = "Window"

    def __init__(self, application, **kwargs):
        """Initialises authentication window.

        Create and style login/register buttons
        """
        super().__init__(application=application, **kwargs)
        self.set_title("Telex")
        self.set_default_size(300, 600)
        self.stack = Gtk.Stack()
        self.box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            width_request=200,
        )
        self.set_child(self.box)
        self.box.set_halign(Gtk.Align.CENTER)
        self.box.set_valign(Gtk.Align.CENTER)
        self.login_btn = Gtk.Button(label="Login", name="login-btn")
        self.register_btn = Gtk.Button(label="Register", name="register-btn")
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            """
            #register-btn, #login-btn {
                background-color: #000000;
                color: #FFFFFF;
            }
        """
        )
        self.login_btn.get_style_context().add_provider(
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
        self.register_btn.get_style_context().add_provider(
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
        self.box.append(self.login_btn)
        self.box.append(self.register_btn)
        self.stack.add_child(self.box)
        self.login_btn.connect("clicked", self.on_login)
        self.register_btn.connect("clicked", self.on_register)

    def set_button_color(self, button: Gtk.Button, label: str):
        """Sets color of register and login button."""
        button.set_label(label)
        button.set_name("btn")
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            """
            #btn {
                background-color: #000000;
                color: #FFFFFF;
            }
        """
        )
        button.get_style_context().add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def render_page(self, data):
        """Renders register or login page.

        Creates entry fields for email and password authentication /
        creates action buttons and attaches the necessary signal handlers.
        """
        self.box.set_visible(False)
        self.auth_box = Gtk.Box(
            name="login",
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
        )
        self.auth_box.set_halign(Gtk.Align.CENTER)
        self.auth_box.set_valign(Gtk.Align.CENTER)
        self.set_child(self.auth_box)
        self.email_field = Gtk.Entry(placeholder_text="Enter email address")
        self.password_field = Gtk.Entry(placeholder_text="Enter password")
        self.auth_box.append(self.email_field)
        self.auth_box.append(self.password_field)
        button = self.login_btn.new()
        self.set_button_color(button, data["button_label"])
        self.auth_box.append(button)
        text = Gtk.Text(text=data["text"])
        link_btn = Gtk.LinkButton(label="click here")
        info_box = Gtk.Box(name="info", orientation=Gtk.Orientation.HORIZONTAL)
        info_box.append(text)
        info_box.append(link_btn)
        self.auth_box.append(info_box)
        self.auth_box.set_visible(True)
        button.connect("clicked", self.on_render_homepage)
        link_btn.connect("clicked", data["signal_handler"])

    def on_register(self, _widget: Gtk.Widget):
        """Responds to click signals from the register button."""
        data = {
            "button_label": "Register",
            "text": "Already a user?",
            "signal_handler": self.on_login,
        }
        self.render_page(data)

    def on_login(self, _widget: Gtk.Widget):
        """Responds to click signals from the login button."""
        data = {
            "button_label": "Login",
            "text": "Not yet registered?",
            "signal_handler": self.on_register,
        }
        self.render_page(data)

    def on_render_homepage(self, _widget: Gtk.Widget):
        """Responds to click signals from either the register or login button."""
        self.auth_box.set_visible(False)
        home = Home()
        home.render_page()
