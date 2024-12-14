"""Copyright 2022 believemanasseh.

Contains classes for various third-party services used
"""

import base64
import platform
from typing import Any

import boto3
import requests
from botocore.exceptions import ClientError


class Reddit:
	"""Base class for all operations on Reddit's API."""

	def __init__(self) -> None:
		"""Initialises request headers."""
		self.domain = "https://{0}.reddit.com/api/v1"
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
		url = self.domain.format("www") + "/access_token"
		data = {
			"grant_type": "authorization_code",
			"code": code,
			"redirect_uri": "https://ce43-169-159-70-11.ngrok-free.app",
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


class AWSClient:
	"""Base class for AWS Secrets Manager service."""

	def __init__(self):
		"""Initialises boto3 sdk session client."""
		session = boto3.Session()
		self.client = session.client(service_name="secretsmanager")

	def create_secret(self, name: str, secret_string: str) -> dict[str, Any]:
		"""Creates secret."""
		return self.client.create_secret(Name=name, SecretString=secret_string)

	def get_secret(self, secret_id: str) -> str:
		"""Retrieves secret value."""
		error_msg = None

		try:
			get_secret_value_response = self.client.get_secret_value(SecretId=secret_id)

			if "SecretString" in get_secret_value_response:
				return {
					"status": "success",
					"secret_value": get_secret_value_response["SecretString"],
				}
		except ClientError as e:
			if e.response["Error"]["Code"] == "ResourceNotFoundException":
				error_msg = f"The requested secret {secret_id} was not found"
			elif e.response["Error"]["Code"] == "InvalidRequestException":
				error_msg = f"The request was invalid due to: {e}"
			elif e.response["Error"]["Code"] == "InvalidParameterException":
				error_msg = f"The request had invalid params: {e}"
			elif e.response["Error"]["Code"] == "DecryptionFailure":
				error_msg = f"The requested secret can't be decrypted using the provided \
				KMS key: {e}"
			elif e.response["Error"]["Code"] == "InternalServiceError":
				error_msg = f"An error occurred on service side: {e}"

		return {"status": "error", "message": error_msg}

	def delete_secret(self, secret_id: str) -> dict:
		"""Deletes secret."""
		return self.client.delete_secret(
			SecretId=secret_id, RecoveryWindowInDays=7, ForceDeleteWithoutRecovery=False
		)
