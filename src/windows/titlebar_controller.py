import gi

import store

gi.require_versions({"Adw": "1", "Gtk": "4.0"})

from gi.repository import Adw, Gtk

from services import Reddit
from utils.common import add_style_context, load_css, load_image

from .home import HomeWindow


class TitlebarController:
    """Manages header_bar contents for both HomeWindow and PostDetailWindow."""

    def __init__(self, header_bar: Adw.HeaderBar, home_window: HomeWindow, api: Reddit):
        self.header_bar = header_bar
        self.api = api
        self.home_window = home_window
        self.css_provider = load_css("/assets/styles/home.css")
        self.start_box: Gtk.Box | None = None
        self.end_box: Gtk.Box | None = None
        self.back_btn: Gtk.Button | None = None

    def setup_titlebar(self) -> None:
        """Customises the application headerbar.

        Adds buttons and menus to the header bar including reload button,
        sort menu button with popover, search button, and profile menu
        button with popover containing user information and account options.
        """
        # ── left─side (reload) ──
        self.start_box = Gtk.Box(halign=True, orientation=Gtk.Orientation.HORIZONTAL)
        reload_btn = Gtk.Button(
            icon_name="xyz.daimones.Telex.reload", tooltip_text="Reload"
        )
        reload_btn.connect("clicked", self.__on_reload_clicked)
        self.start_box.append(reload_btn)
        self.header_bar.pack_start(self.start_box)

        # ── right─side (sort, search, profile) ──
        self.end_box = Gtk.Box(halign=True, orientation=Gtk.Orientation.HORIZONTAL)

        # Sort menu button
        menu_btn_child = self.__add_menu_button_child()
        popover_child = self.__add_sort_popover_child()
        self.end_box.append(
            Gtk.MenuButton(
                child=menu_btn_child,
                tooltip_text="Sort posts",
                popover=Gtk.Popover(child=popover_child),
            )
        )

        # Search
        self.end_box.append(
            Gtk.Button(icon_name="xyz.daimones.Telex.search", tooltip_text="Search")
        )

        # Profile popover
        popover_child = self.__add_profile_popover_child()
        self.end_box.append(
            Gtk.MenuButton(
                icon_name="xyz.daimones.Telex.profile",
                tooltip_text="Profile",
                popover=Gtk.Popover(child=popover_child),
            )
        )

        self.header_bar.pack_end(self.end_box)

    def add_back_button(self) -> Gtk.Button:
        """Inserts a single back-arrow button at the left of the header."""
        self.back_btn = Gtk.Button(
            icon_name="xyz.daimones.Telex.arrow-pointing-left",
            tooltip_text="Back to Home",
        )
        self.back_btn.connect("clicked", self.__on_back_clicked)
        self.header_bar.pack_start(self.back_btn)
        return self.back_btn

    def __add_profile_popover_child(self) -> Gtk.Box:
        """Creates profile popover child widget.

        Creates a box containing the user profile information (profile picture,
        username, karma) and menu options (View Profile, Subreddits, Settings,
        About, Log Out) for the profile popover menu.

        Returns:
            Gtk.Box: Container with profile info and menu options
        """
        popover_child = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        grid = Gtk.Grid(column_spacing=30)
        grid.insert_row(0)
        grid.insert_column(0)
        grid.insert_column(1)

        user_profile_img = load_image(
            "/assets/images/reddit-placeholder.png",
            "placeholder",
            css_classes=["user-profile-img"],
        )
        add_style_context(user_profile_img, self.css_provider)
        grid.attach(user_profile_img, 0, 0, 1, 1)

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            valign=Gtk.Align.CENTER,
            halign=Gtk.Align.CENTER,
        )
        box.append(Gtk.Label(label="u/believemanasseh", halign=Gtk.Align.START))
        box.append(Gtk.Label(label="38 karma", halign=Gtk.Align.START))
        grid.attach(box, 1, 0, 1, 1)

        popover_child.append(grid)

        menu_labels = [
            "View Profile",
            "Subreddits",
            "Settings",
            "About",
            "Log Out",
        ]
        for label in menu_labels:
            if "Log" in label:
                menu_btn = Gtk.Button(
                    label=label, css_classes=["menu-btn-logout"], hexpand=True
                )
            else:
                menu_btn = Gtk.Button(
                    label=label, css_classes=["menu-btn"], hexpand=True
                )

            if menu_btn.get_child():
                menu_btn.get_child().set_halign(Gtk.Align.START)

            add_style_context(menu_btn, self.css_provider)
            popover_child.append(menu_btn)

        return popover_child

    def __add_sort_popover_child(self) -> Gtk.Box:
        """Creates sort popover child widget.

        Creates a box containing radio buttons for post sorting options
        (Hot, New, Rising, etc.) allowing the user to change the post
        sort order.

        Returns:
            Gtk.Box: Container with post sorting options as radio buttons
        """
        popover_child = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        active = True if store.current_sort == 0 else False
        best_check_btn = Gtk.CheckButton(
            active=active, name="0", label=store.post_sort_type[0]
        )
        best_check_btn.connect("toggled", self.__on_check_btn_toggled)

        active = True if store.current_sort == 1 else False
        new_check_btn = Gtk.CheckButton(
            active=active, name="1", label=store.post_sort_type[1]
        )
        new_check_btn.set_group(best_check_btn)
        new_check_btn.connect("toggled", self.__on_check_btn_toggled)

        active = True if store.current_sort == 2 else False
        hot_check_btn = Gtk.CheckButton(
            active=active, name="2", label=store.post_sort_type[2]
        )
        hot_check_btn.set_group(best_check_btn)
        hot_check_btn.connect("toggled", self.__on_check_btn_toggled)

        active = True if store.current_sort == 3 else False
        top_check_btn = Gtk.CheckButton(
            active=active, name="3", label=store.post_sort_type[3]
        )
        top_check_btn.set_group(hot_check_btn)
        top_check_btn.connect("toggled", self.__on_check_btn_toggled)

        active = True if store.current_sort == 4 else False
        rising_check_btn = Gtk.CheckButton(
            active=active, name="4", label=store.post_sort_type[4]
        )
        rising_check_btn.set_group(top_check_btn)
        rising_check_btn.connect("toggled", self.__on_check_btn_toggled)

        popover_child.append(best_check_btn)
        popover_child.append(new_check_btn)
        popover_child.append(hot_check_btn)
        popover_child.append(top_check_btn)
        popover_child.append(rising_check_btn)

        return popover_child

    def __add_menu_button_child(self) -> Gtk.Box:
        """Creates menu button child widget.

        Creates a box containing the sort menu button's label showing the
        current sort type and a dropdown icon to indicate it's expandable.

        Returns:
            Gtk.Box: Container with sort button label and dropdown icon
        """
        menu_btn_child = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
        )

        grid = Gtk.Grid(column_spacing=30)
        grid.insert_row(0)
        grid.insert_column(0)
        grid.insert_column(1)

        label = Gtk.Label(
            label=store.post_sort_type[store.current_sort],
            css_classes=["menu-btn-label"],
        )
        grid.attach(label, 0, 0, 1, 1)

        image = Gtk.Image(icon_name="xyz.daimones.Telex.sort-down")
        grid.attach(image, 1, 0, 1, 1)

        menu_btn_child.append(grid)

        add_style_context(label, self.css_provider)

        return menu_btn_child

    def __on_reload_clicked(self, _widget: Gtk.Button) -> None:
        """Handles reload button click events.

        Reloads the current page by fetching the latest data from Reddit
        and re-rendering the page with the updated content.

        Args:
            _widget (Gtk.Button): The reload button that was clicked

        Returns:
            None: This method does not return a value.
        """
        self.home_window.reload_data()
        self.home_window.render_page(setup_titlebar=False)

    def __on_check_btn_toggled(self, widget: Gtk.CheckButton) -> None:
        """Handles radio button click events for sorting options.

        Updates the current sort category based on the selected radio button
        and reloads the page with the new sorting option.

        Args:
            widget (Gtk.CheckButton): The radio button that was clicked

        Returns:
            None: This method does not return a value.
        """
        if widget.get_active():
            store.current_sort = int(widget.get_name())
            self.__on_reload_clicked(widget)
            self.header_bar.remove(self.start_box)
            self.header_bar.remove(self.end_box)
            self.setup_titlebar()

    def __on_back_clicked(self, button: Gtk.Button) -> None:
        """Handles back button click events.

        Returns to the home view by restoring the HomeWindow view
        and clearing the current post detail view.

        Args:
            button (Gtk.Button): The button that triggered the event

        Returns:
            None: This method does not return a value.
        """
        # Remove the back button from header bar
        self.header_bar.remove(self.back_btn)

        # Remove post detail content
        if self.home_window.scrolled_window.get_child():
            self.home_window.scrolled_window.set_child(None)

        # Restore home window components
        self.home_window.render_page(setup_titlebar=False)
