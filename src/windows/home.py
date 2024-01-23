from app import Gtk


class Home(Gtk.ApplicationWindow):
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    @classmethod
    def load_page(cls, *args, **kwargs):
        text = Gtk.Text(text="Welcome to Telex!")
        cls.box.append(text)
        cls.box.set_visible(True)
