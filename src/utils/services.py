"""Copyright 2022 believemanasseh.

Contains classes for various third-party services used
"""
import platform

import requests


class Reddit:
    """Base class for all operations on Reddit's API."""

    def __init__(self):
        """Initialises request headers."""
        self.system = platform.system()
        self.headers = {
            "User-Agent": f"Telex/{self.system}:v0.1.0 (by /u/believemanasseh)",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def generate_access_token(self, code):
        """Generates access token.

        Args:
            code - authorization code
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "telex://oauth",
        }
        try:
            res = requests.post(data=data, headers=self.headers, timeout=30)
        except requests.RequestException:
            return None

        return res.json()
