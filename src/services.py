"""Contains classes for various third-party services used.

This module provides:
- Reddit: base Reddit class for all http operations
- AWSClient: base class for AWS Secrets Manager
"""

import base64
import platform

import boto3
import requests
from botocore.exceptions import ClientError


class Reddit:
	"""Base class for all operations on Reddit's API."""

	def __init__(self) -> None:
		"""Initialises request headers."""
		self.domain = "https://{0}.reddit.com"
		self.system = platform.system()
		base_encoded_string = base64.b64encode(b"xLfTJ9fCMdxmr5JCiNWMHQ:" + b"").decode(
			"utf-8"
		)
		self.headers = {
			"Authorization": "Basic " + base_encoded_string,
			"User-Agent": f"{self.system.lower()}:telex:v0.1.0 (by /u/Intrepid-Set1590)",
		}

	def inject_token(self, token: str) -> None:
		"""Add access token to authorisation header."""
		self.headers["Authorization"] = f"Bearer {token}"

	def generate_access_token(self, code: str) -> dict[str, int | dict] | None:
		"""Generates access token."""
		url = self.domain.format("www") + "/api/v1/access_token"
		data = {
			"grant_type": "authorization_code",
			"code": code,
			"redirect_uri": "https://93c9-169-159-123-32.ngrok-free.app",
		}

		try:
			res = requests.post(url, data=data, headers=self.headers, timeout=30)
		except requests.RequestException:
			return None

		return {"status_code": res.status_code, "json": res.json()}

	def retrieve_listings(self, category: str) -> dict[str, int | dict] | None:
		"""Returns new posts."""
		url = self.domain.format("oauth") + f"/{category}"
		try:
			res = requests.get(url, headers=self.headers, timeout=30)
		except requests.RequestException:
			return None
		return {"status_code": res.status_code, "json": res.json()}

	def retrieve_comments(self, post_id: str) -> dict[str, int | dict] | None:
		"""Returns all comments for post."""
		url = self.domain.format("oauth") + f"/comments/{post_id}"
		try:
			res = requests.get(url, headers=self.headers, timeout=30)
		except requests.RequestException:
			return None
		return {"status_code": res.status_code, "json": res.json()}


class AWSClient:
	"""Base class for AWS Secrets Manager service."""

	def __init__(self):
		"""Initialises boto3 sdk session client."""
		session = boto3.Session()
		self.client = session.client(service_name="secretsmanager")

	def create_secret(self, name: str, secret_string: str) -> dict:
		"""Creates secret."""
		try:
			res = self.client.create_secret(Name=name, SecretString=secret_string)
		except ClientError as e:
			# Update secret if it already exists
			if e.response["Error"]["Code"] == "ResourceExistsException":
				return self.update_secret(secret_id=name, secret_string=secret_string)

		return {"status": "success", "json": res}

	def get_secret(self, secret_id: str) -> dict:
		"""Retrieves secret value."""
		get_secret_value_response = self.client.get_secret_value(SecretId=secret_id)

		if "SecretString" not in get_secret_value_response:
			return {"status": "error", "message": "Secret string not in response"}

		return {
			"status": "success",
			"secret_value": get_secret_value_response["SecretString"],
		}

	def update_secret(self, secret_id: str, secret_string: str) -> dict:
		"""Updates secret value."""
		return self.client.update_secret(SecretId=secret_id, SecretString=secret_string)

	def delete_secret(self, secret_id: str) -> dict:
		"""Deletes secret."""
		res = self.client.delete_secret(
			SecretId=secret_id,
			RecoveryWindowInDays=7,
			ForceDeleteWithoutRecovery=False,
		)
		return {"status": "success", "json": res}
