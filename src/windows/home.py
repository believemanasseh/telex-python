"""Window class for app's homepage.

This module provides:
- HomeWindow: window class for home page
"""

import gi

import store

gi.require_versions({"Gtk": "4.0", "Pango": "1.0"})

from gi.repository import Gtk, Pango

from services import Reddit
from utils.common import (
    add_style_context,
    add_style_contexts,
    append_all,
    create_cursor,
    get_submission_time,
    load_css,
    load_image,
)
from windows.auth import AuthWindow


class HomeWindow(Gtk.ApplicationWindow):
    """Base class for homepage."""

    def __init__(self, base_window: AuthWindow, api: Reddit):
        """Maximises base application window and styles base box widget."""
        self.base = base_window
        self.api = api
        self.cursor = create_cursor("pointer")
        self.css_provider = load_css("/assets/styles/home.css")

        # Fetches data from Reddit
        category = store.post_sort_type[store.current_sort].lower()
        self.data = self.__fetch_data(category)

    def __fetch_data(self, category: str) -> dict[str, int | dict] | None:
        """Retrieves post listings from Reddit API.

        Args:
            category (str): Category of posts to retrieve (e.g., 'hot', 'new', 'rising')

        Returns:
            dict[str, int | dict] | None: Response containing status code and listing data
        """
        return self.api.retrieve_listings(category)

    def add_post_image(self) -> Gtk.Box:
        """Creates a container for a post thumbnail image.

        Creates a Gtk.Box containing the post thumbnail image with appropriate
        styling and layout settings.

        Returns:
            Gtk.Box: Container holding the post thumbnail image
        """
        post_image_box = Gtk.Box(
            css_classes=["post-image-box"],
            width_request=100,
        )
        add_style_context(post_image_box, self.css_provider)

        post_image = load_image(
            "/assets/images/reddit-placeholder.png",
            "Reddit placeholder",
            css_classes=["post-image"],
            css_provider=self.css_provider,
        )
        post_image_box.append(post_image)

        return post_image_box

    def add_vote_buttons(self, score: int) -> Gtk.Box:
        """Creates upvote/downvote buttons and score display.

        Creates a vertically arranged box with upvote button, score counter,
        and downvote button with appropriate styling.

        Args:
            score (int): The post's current vote score to display

        Returns:
            Gtk.Box: Container with vote buttons and score display
        """
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=10, css_classes=["icon-box"]
        )
        add_style_context(box, self.css_provider)

        upvote_btn = Gtk.Button(icon_name="xyz.daimones.Telex.upvote")
        box.append(upvote_btn)

        score_count = Gtk.Label(label=f"{score}", css_classes=["score-count"])
        add_style_context(score_count, self.css_provider)
        box.append(score_count)

        downvote_btn = Gtk.Button(icon_name="xyz.daimones.Telex.downvote")
        box.append(downvote_btn)

        return box

    def add_post_metadata(
        self,
        title: str,
        subreddit_name: str,
        user: str,
        num_of_comments: int,
        submission_time: str,
    ) -> Gtk.Box:
        """Add widgets for post metadata (e.g. post title, post user, post subreddit)."""
        post_metadata_box = Gtk.Box(
            css_classes=["post-metadata-box"],
            orientation=Gtk.Orientation.VERTICAL,
            valign=Gtk.Align.CENTER,
            halign=Gtk.Align.START,
        )
        add_style_context(post_metadata_box, self.css_provider)

        post_title = Gtk.Label(
            label=title,
            css_classes=["post-title"],
            wrap=True,
            hexpand=True,
            halign=Gtk.Align.START,
            wrap_mode=Pango.WrapMode.CHAR,
            cursor=self.cursor,
            max_width_chars=90,
        )
        add_style_context(post_title, self.css_provider)
        post_metadata_box.append(post_title)
        post_box = Gtk.Box(margin_top=5, orientation=Gtk.Orientation.HORIZONTAL)
        post_time = Gtk.Label(
            label=f"submitted {submission_time} by ",
            css_classes=["post-metadata"],
            halign=Gtk.Align.START,
            margin_top=5,
        )

        post_user = Gtk.Label(
            label=f"{user} ",
            css_classes=["post-user"],
            cursor=self.cursor,
            margin_top=5,
        )
        add_style_context(post_user, self.css_provider)

        post_text = Gtk.Label(label="to ", css_classes=["post-metadata"], margin_top=5)
        add_style_contexts([post_time, post_text], self.css_provider)

        post_subreddit = Gtk.Label(
            label=subreddit_name,
            css_classes=["post-subreddit"],
            cursor=self.cursor,
            margin_top=5,
        )
        add_style_context(post_subreddit, self.css_provider)

        append_all(post_box, [post_time, post_user, post_text, post_subreddit])

        post_metadata_box.append(post_box)

        post_action_btns_box = self.add_action_btns(num_of_comments)

        post_metadata_box.append(post_action_btns_box)

        return post_metadata_box

    def add_action_btns(self, num_of_comments: int) -> Gtk.Box:
        """Add widgets for action buttons (e.g. share, save, crosspost, etc)."""
        post_action_btns_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.START,
            margin_top=5,
        )

        labels = [
            f"{num_of_comments} comment{'s' if num_of_comments > 1 else ''} ",
            "share ",
            "save ",
            "hide ",
            "report ",
            "crosspost ",
        ]

        for label in labels:
            post = Gtk.Label(
                label=label,
                css_classes=["post-action-btn"],
                cursor=self.cursor,
                margin_top=5,
            )
            add_style_context(post, self.css_provider)

            post_action_btns_box.append(post)

        return post_action_btns_box

    def __add_profile_popover_child(self) -> Gtk.Box:
        """Creates profile popover child widget.

        Creates a box containing the user profile information and menu options
        for the profile popover menu.

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

        Creates a box containing radio buttons for post sorting options.

        Returns:
            Gtk.Box: Container with post sorting options
        """
        popover_child = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        check_btn = Gtk.CheckButton(
            active=True, label=store.post_sort_type[store.current_sort]
        )

        store.current_sort += 1
        check_btn1 = Gtk.CheckButton(active=False)
        check_btn1.set_group(check_btn)
        check_btn1.set_label(store.post_sort_type[store.current_sort])

        store.current_sort += 1
        check_btn2 = Gtk.CheckButton(
            active=False, label=store.post_sort_type[store.current_sort]
        )
        check_btn2.set_group(check_btn1)

        store.current_sort += 1
        check_btn3 = Gtk.CheckButton(
            active=False, label=store.post_sort_type[store.current_sort]
        )
        check_btn3.set_group(check_btn2)

        store.current_sort += 1
        check_btn4 = Gtk.CheckButton(
            active=False, label=store.post_sort_type[store.current_sort]
        )
        check_btn4.set_group(check_btn3)

        popover_child.append(check_btn)
        popover_child.append(check_btn1)
        popover_child.append(check_btn2)
        popover_child.append(check_btn3)
        popover_child.append(check_btn4)

        return popover_child

    def __add_menu_button_child(self) -> Gtk.Box:
        """Creates menu button child widget.

        Creates a box containing the sort menu button's label and dropdown icon.

        Returns:
            Gtk.Box: Container with sort button label and icon
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
    
    def __on_box_clicked(
        self,
        _gesture: Gtk.GestureClick,
        _n_press: int,
        _x: float,
        _y: float,
        widget: Gtk.Box,
    ):
        """Handles post click events.

        Opens the post detail view when a post container is clicked.

        Args:
            _gesture (Gtk.GestureClick): The click gesture that triggered the event
            _n_press (int): Number of presses that triggered the event
            _x (float): x-coordinate of the event
            _y (float): y-coordinate of the event
            widget (Gtk.Box): The post container widget that was clicked
        """
        from windows.post_detail import PostDetailWindow

        store.current_sort = 0
        index = widget.get_name()
        post_id = self.data["json"]["data"]["children"][int(index)]["data"]["id"]
        self.scrolled_window.set_child_visible(False)
        post_detail_window = PostDetailWindow(
            base_window=self, api=self.api, post_id=post_id
        )
        post_detail_window.render_page()

    def customise_titlebar(self) -> Gtk.HeaderBar:
        """Customise titlebar widgets.

        Adds buttons and menus to the header bar including reload, sort,
        search, and profile buttons.

        Returns:
            Gtk.HeaderBar: Customized header bar for the application
        """
        start_box = Gtk.Box(halign=True, orientation=Gtk.Orientation.HORIZONTAL)
        start_box.append(
            Gtk.Button(icon_name="xyz.daimones.Telex.reload", tooltip_text="Reload")
        )

        end_box = Gtk.Box(halign=True, orientation=Gtk.Orientation.HORIZONTAL)

        menu_btn_child = self.__add_menu_button_child()
        popover_child = self.__add_sort_popover_child()
        end_box.append(
            Gtk.MenuButton(
                child=menu_btn_child,
                tooltip_text="Sort posts",
                popover=Gtk.Popover(child=popover_child),
            )
        )
        end_box.append(
            Gtk.Button(icon_name="xyz.daimones.Telex.search", tooltip_text="Search")
        )

        popover_child = self.__add_profile_popover_child()

        end_box.append(
            Gtk.MenuButton(
                icon_name="xyz.daimones.Telex.profile",
                tooltip_text="Profile",
                popover=Gtk.Popover(child=popover_child),
            )
        )

        self.base.header_bar.pack_start(start_box)
        self.base.header_bar.pack_end(end_box)

        return self.base.header_bar

    def render_page(self):
        """Renders homepage.

        Creates the main layout for the homepage, customizes the titlebar,
        and displays the list of posts with scrolling functionality.
        """
        self.customise_titlebar()

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=20,
            css_classes=["box"],
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.START,
            hexpand=True,
            vexpand=True,
        )
        add_style_context(box, self.css_provider)

        for index, data in enumerate(self.data["json"]["data"]["children"]):
            post_container = Gtk.Box(
                css_classes=["post-container"],
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=10,
                name=str(index),
            )
            add_style_context(post_container, self.css_provider)

            click_controller = Gtk.GestureClick()
            click_controller.connect(
                "pressed",
                lambda gesture,
                n_press,
                x,
                y,
                widget=post_container: self.__on_box_clicked(
                    gesture, n_press, x, y, widget
                ),
            )
            post_container.add_controller(click_controller)

            box.append(post_container)

            vote_btns_box = self.add_vote_buttons(data["data"]["score"])
            post_container.append(vote_btns_box)

            post_image_box = self.add_post_image()
            post_container.append(post_image_box)

            post_metadata_box = self.add_post_metadata(
                data["data"]["title"],
                data["data"]["subreddit_name_prefixed"],
                data["data"]["author"],
                data["data"]["num_comments"],
                get_submission_time(data["data"]["created_utc"]),
            )
            post_container.append(post_metadata_box)

        self.viewport = Gtk.Viewport()
        self.viewport.set_child(box)

        self.scrolled_window = Gtk.ScrolledWindow(
            hscrollbar_policy=Gtk.PolicyType.NEVER,
            vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
        )
        self.scrolled_window.set_child(self.viewport)

        self.base.set_child(self.scrolled_window)
        self.base.maximize()
