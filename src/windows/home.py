from gi.repository import Gtk


class Home(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load_page(self):
        text = Gtk.Text(text="Welcome to Telex!", css_name="text")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            """
            #text {
                background-color: #000000;
                color: #FFFFFF;
            }
        """.encode()
        )
        box.get_style_context().add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.set_child(box)
        box.append(text)
        box.set_visible(True)
