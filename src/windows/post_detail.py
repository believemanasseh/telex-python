"""Window class for post detail widgets.

This module provides:
- PostDetailWindow: window class for post detail
"""

import gi

gi.require_versions({"Gtk": "4.0", "Adw": "1"})

from gi.repository import Adw, Gtk

from services import Reddit
from utils.common import add_style_contexts, get_submission_time, load_css, load_image
from windows.home import HomeWindow


class PostDetailWindow(Gtk.ApplicationWindow):
    """Window class for displaying detailed post content and comments.
    
    This class is responsible for retrieving and displaying a Reddit post's 
    detailed content including the post itself and its comment tree. It shows
    the post at the top and nested comments below it with appropriate 
    indentation levels to indicate reply hierarchy. Comments include metadata 
    such as author, score, and content, along with action buttons.
    
    Attributes:
        base (HomeWindow): Reference to the base window instance
        api (Reddit): Reddit API instance for data operations
        css_provider (Gtk.CssProvider): Provider for styling post details
        data (dict): Fetched post and comments data
        box (Gtk.Box): Main container for post and comments
        clamp (Adw.Clamp): Clamp widget to constrain the content width
    """

    def __init__(self, base_window: HomeWindow, api: Reddit, post_id: str):
        """Initialises window for post details.
        
        Args:
            base_window (HomeWindow): Parent window instance containing the main application window
            api (Reddit): Reddit API instance for fetching post data
            post_id (str): Unique identifier of the Reddit post to display
        
        Attributes:
            base (HomeWindow): Reference to parent window
            css_provider: CSS styles provider for the window
            data: Post data fetched from Reddit
            box (Gtk.Box): Vertical container for post content
            clamp (Adw.Clamp): Width constraint container
            back_button (Gtk.Button): Navigation button to return to home view
        """
        self.base = base_window
        self.api = api
        self.css_provider = load_css("/assets/styles/post_detail.css")
        self.data = self.__fetch_data(post_id)
        self.box = Gtk.Box(
            css_classes=["box"],
            orientation=Gtk.Orientation.VERTICAL,
            valign=Gtk.Align.START,
            vexpand=True,
        )
        self.clamp = Adw.Clamp(child=self.box, maximum_size=1000)
        
        # Add back navigation button
        self.back_button = Gtk.Button(
            icon_name="xyz.daimones.Telex.arrow-pointing-left",
            tooltip_text="Back to Home"
        )
        self.back_button.connect("clicked", self.__on_back_clicked)
        
        self.base.base.header_bar.pack_start(self.back_button)

    def __on_back_clicked(self, button: Gtk.Button):
        """Handles back button click events.
        
        Returns to the home view by restoring the HomeWindow view
        and clearing the current post detail view.
        
        Args:
            button (Gtk.Button): The button that triggered the event
        """
        # Remove the back button from header bar
        self.base.base.header_bar.remove(self.back_button)
    
        # Remove post detail content
        if self.base.scrolled_window.get_child():
            self.base.scrolled_window.set_child(None)
        
        # Restore home window components
        self.base.render_page(customise_titlebar=False)

    def __fetch_data(self, post_id: str) -> dict[str, int | dict] | None:
        """Retrieves post details and comments from Reddit API.

        Calls the Reddit API to get the complete post data and its comment tree
        based on the provided post ID.

        Args:
            post_id (str): Unique identifier for the Reddit post

        Returns:
            dict[str, int | dict] | None: Post and comments data dictionary 
                                          or None if not found
        """
        return self.api.retrieve_comments(post_id)

    def __load_comments(
        self, parent_box: Gtk.Box, comment_data: dict, nesting_level: int = 0
    ) -> None:
        """Loads and renders comments recursively with proper nesting.

        Creates UI components for each comment including author information, 
        comment content, score, and action buttons. Recursively processes reply 
        chains with increased indentation to visually represent the comment hierarchy.

        Args:
            parent_box (Gtk.Box): Container to add the comment widgets to
            comment_data (dict): Comment data dictionary containing content and metadata
            nesting_level (int, optional): Current comment nesting level (0 for top-level comments)
        """
        if "kind" not in comment_data or comment_data["kind"] != "t1":
            return  # Skip if not a comment

        data = comment_data.get("data", {})

        if "author" not in data or data.get("author") is None:
            return  # Skip deleted comments

        author = data["author"]
        body = data["body"]
        score = data.get("score", 0)

        # Create comment container with proper indentation
        comment_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            valign=Gtk.Align.START,
            vexpand=True,
            spacing=8,
            margin_start=nesting_level * 30,
            margin_bottom=15,
            css_classes=["comment-box"],
        )

        # Create header box for author and metadata
        header_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
            valign=Gtk.Align.START,
            halign=Gtk.Align.START,
        )

        # Add user avatar
        avatar = load_image(
            "/assets/images/reddit-placeholder.png",
            "User avatar",
            css_classes=["comment-avatar"],
            css_provider=self.css_provider,
        )
        header_box.append(avatar)

        # Add author name
        author_label = Gtk.Label(
            label=author,
            halign=Gtk.Align.START,
            css_classes=["comment-author"],
        )
        header_box.append(author_label)

        # Add score
        score_label = Gtk.Label(
            label=f"· {score} points",
            halign=Gtk.Align.START,
            css_classes=["comment-score"],
        )
        header_box.append(score_label)

        # Add body text
        body_label = Gtk.Label(
            label=body,
            halign=Gtk.Align.START,
            max_width_chars=160,
            wrap=True,
            css_classes=["comment-body"],
        )

        # Add actions bar
        actions_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
            valign=Gtk.Align.START,
            halign=Gtk.Align.START,
            margin_top=5,
        )

        # Add reply button
        reply_button = Gtk.Button(
            label="Reply",
            css_classes=["comment-action-button"],
        )
        actions_box.append(reply_button)

        # Add upvote/downvote buttons
        vote_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=5,
            valign=Gtk.Align.CENTER,
        )
        upvote_btn = Gtk.Button(icon_name="xyz.daimones.Telex.upvote")
        downvote_btn = Gtk.Button(icon_name="xyz.daimones.Telex.downvote")
        vote_box.append(upvote_btn)
        vote_box.append(downvote_btn)
        actions_box.append(vote_box)

        # Assemble comment box
        comment_box.append(header_box)
        comment_box.append(body_label)
        comment_box.append(actions_box)

        # Add comment to parent box
        parent_box.append(comment_box)

        # Add style contexts
        add_style_contexts(
            [comment_box, author_label, body_label, score_label, avatar, reply_button],
            self.css_provider,
        )

        # Process replies recursively if they exist
        replies_data = data.get("replies", {})
        if replies_data and "data" in replies_data:
            children = replies_data["data"].get("children", [])
            for reply in children:
                self.__load_comments(parent_box, reply, nesting_level + 1)

    def render_page(self):
        """Renders the post detail page with post content and comments.
        
        Builds the complete UI for the post detail view including:
        - The post itself (reusing components from HomeWindow)
        - A comments header
        - The nested comment tree with proper indentation
        
        This method sets up the viewport and makes the content visible in the 
        scrolled window from the base HomeWindow instance.
        """
        post_data = self.data["json"][0]["data"]["children"][0]

        post_container = Gtk.Box(
            css_classes=["post-container"],
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10
        )

        self.box.append(post_container)

        vote_btns_box = self.base.add_vote_buttons(post_data["data"]["score"])
        post_container.append(vote_btns_box)

        post_image_box = self.base.add_post_image()
        post_container.append(post_image_box)

        post_metadata_box = self.base.add_post_metadata(
            post_data["data"]["title"],
            post_data["data"]["subreddit_name_prefixed"],
            post_data["data"]["author"],
            post_data["data"]["num_comments"],
            get_submission_time(post_data["data"]["created_utc"]),
        )
        post_container.append(post_metadata_box)
        add_style_contexts([self.box, post_container], self.css_provider)

        self.base.viewport.set_child(self.clamp)
        self.base.scrolled_window.set_child(self.base.viewport)
        self.base.scrolled_window.set_child_visible(True)

        # Create a comments section header
        comments_header = Gtk.Label(
            label="Comments",
            halign=Gtk.Align.START,
            margin_top=20,
            margin_bottom=10,
            margin_start=10,
            css_classes=["comments-header"],
        )
        self.box.append(comments_header)

        # Create a comments container
        comments_container = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            valign=Gtk.Align.START,
            halign=Gtk.Align.CENTER,
        )
        self.box.append(comments_container)
        add_style_contexts([comments_header, comments_container], self.css_provider)

        # Load comments
        comments_data = self.data["json"][1]["data"]["children"]
        for comment in comments_data:
            self.__load_comments(comments_container, comment, 0)
