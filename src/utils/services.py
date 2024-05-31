"""Copyright 2022 believemanasseh.

Contains classes for various third-party services used
"""

import base64
import platform

import requests


class Reddit:
	"""Base class for all operations on Reddit's API."""

	def __init__(self):
		"""Initialises request headers."""
		self.domain = "https://{0}.reddit.com/api/v1"
		self.system = platform.system()
		base_encoded_string = base64.b64encode(b"TAugZFgqYCtC9yjZRcWpng").decode("utf-8")
		self.headers = {
			"User-Agent": f"Telex/{self.system}:v0.1.0 (by /u/Intrepid-Set1590)",
			"Content-Type": "application/x-www-form-urlencoded",
			"Authorization": f"Basic {base_encoded_string}",
		}

	def generate_access_token(self, code: str):
		"""Generates access token.

		Args:
		code - authorization code
		"""
		url = self.domain.format("www") + "/access_token"
		data = {
			"grant_type": "authorization_code",
			"code": code,
			"redirect_uri": "https://2ec8-160-152-128-100.ngrok-free.app",
		}
		print(self.headers)
		try:
			res = requests.post(url, data=data, headers=self.headers, timeout=30)
		except requests.RequestException:
			return None

		return {"status_code": res.status_code, "json": res.json()}
