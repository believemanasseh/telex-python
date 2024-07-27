"""Copyright 2022 believemanasseh.

Contains classes for various third-party services used
"""

import base64
import platform

import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class Reddit:
	"""Base class for all operations on Reddit's API."""

	def __init__(self):
		"""Initialises request headers."""
		self.domain = "https://{0}.reddit.com/api/v1"
		self.system = platform.system()
		base_encoded_string = base64.b64encode(b"TAugZFgqYCtC9yjZRcWpng:" + b"").decode(
			"utf-8"
		)
		self.headers = {
			"Authorization": "Basic " + base_encoded_string,
			"User-Agent": f"{self.system.lower()}:telex:v0.1.0 (by /u/Intrepid-Set1590)",
		}

	def inject_token(self, token: str) -> None:
		"""Add access token to authorisation header."""
		self.headers["Authorization"] = f"Bearer {token}"

	def generate_access_token(self, code: str) -> dict[str, int | dict]:
		"""Generates access token.

		Args:
		code - authorization code
		"""
		url = self.domain.format("www") + "/access_token"
		data = {
			"grant_type": "authorization_code",
			"code": code,
			"redirect_uri": "https://9873-160-152-51-66.ngrok-free.app",
		}

		try:
			res = requests.post(url, data=data, headers=self.headers, timeout=30)
		except requests.RequestException:
			return None

		return {"status_code": res.status_code, "json": res.json()}


class AzureClient:
	"""Base class for Azure Key Vault Secrets service."""

	@classmethod
	def create_client(cls):
		"""Creates secret client for requests to Azure."""
		credential = DefaultAzureCredential()
		return SecretClient(
			vault_url="https://telex.vault.azure.net/", credential=credential
		)
