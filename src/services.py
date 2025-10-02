"""Service integrations for external APIs and cloud services.

This module implements client classes for external service integrations:

Reddit API Client:
- OAuth2 authentication flow
- Post and comment data retrieval
- Content interaction (voting, commenting)
- User profile management

AWS Services:
- Secrets Manager operations
- Secure credential storage
- Secret lifecycle management
- Error handling for AWS operations

The module provides a clean interface for interacting with these services
while handling authentication, error cases, and data formatting.
"""

import base64
import platform

import boto3
import httpx
import requests
from botocore.exceptions import ClientError


class Reddit:
	"""Base class for all operations on Reddit's API."""

	def __init__(self) -> None:
		"""Initialises request headers for Reddit API authentication."""
		self.domain = "https://{0}.reddit.com"
		self.system = platform.system().lower()
		base_encoded_string = base64.b64encode(b"TAugZFgqYCtC9yjZRcWpng:" + b"").decode(
			"utf-8"
		)
		self.headers = {
			"Authorization": "Basic " + base_encoded_string,
			"User-Agent": f"{self.system}:telex:v0.1.0 (by /u/Intrepid-Set1590)",
		}

	def inject_token(self, token: str) -> None:
		"""Add access token to authorization header.

		Args:
			token (str): OAuth access token for Reddit API
		"""
		self.headers["Authorization"] = f"Bearer {token}"

	async def generate_access_token(self, code: str) -> dict[str, int | dict]:
		"""Generates access token from authorization code.

		Args:
			code (str): Authorization code from Reddit OAuth flow

		Returns:
			dict[str, int | dict]: Response containing status code and token data

		Raises:
			httpx.RequestError: If the request to Reddit API fails
		"""
		try:
			url = self.domain.format("www") + "/api/v1/access_token"
			data = {
				"grant_type": "authorization_code",
				"code": code,
				"redirect_uri": "https://9b4cdb6b1627.ngrok-free.app",
			}
			async with httpx.AsyncClient() as client:
				res = await client.post(url, data=data, headers=self.headers, timeout=30)
				return {"status_code": res.status_code, "json": res.json()}
		except httpx.RequestError as e:
			msg = "Failed to generate access token"
			raise httpx.RequestError(msg) from e

	async def retrieve_listings(self, category: str) -> dict[str, int | dict]:
		"""Returns posts from specified category.

		Args:
			category (str): Category of listings to retrieve e.g. 'new', 'hot', 'rising'

		Returns:
			dict[str, int | dict]: Response containing status code and listing data

		Raises:
			httpx.RequestError: If the request to Reddit API fails
		"""
		try:
			url = self.domain.format("oauth") + f"/{category}"
			async with httpx.AsyncClient() as client:
				res = await client.get(url, headers=self.headers, timeout=30)
				return {"status_code": res.status_code, "json": res.json()}
		except httpx.RequestError as e:
			msg = "Failed to retrieve listings"
			raise httpx.RequestError(msg) from e

	async def retrieve_user_details(self) -> dict[str, int | dict]:
		"""Returns user details.

		Returns:
			dict[str, int | dict]: Response containing status code and user data

		Raises:
			requests.RequestException: If the request to Reddit API fails
		"""
		try:
			url = self.domain.format("oauth") + "/api/v1/me"
			async with httpx.AsyncClient() as client:
				res = await client.get(url, headers=self.headers, timeout=30)
				return {"status_code": res.status_code, "json": res.json()}
		except requests.RequestException as e:
			msg = "Failed to retrieve user details"
			raise requests.RequestException(msg) from e

	async def retrieve_comments(self, post_id: str) -> dict[str, int | dict]:
		"""Returns all comments for post.

		Args:
			post_id (str): Post ID

		Returns:
			dict[str, int | dict]: Post data dictionary or None if not found

		Raises:
			requests.RequestException: If the request fails
		"""
		try:
			url = self.domain.format("oauth") + f"/comments/{post_id}"
			async with httpx.AsyncClient() as client:
				res = await client.get(url, headers=self.headers, timeout=30)
				return {"status_code": res.status_code, "json": res.json()}
		except requests.RequestException as e:
			msg = "Failed to retrieve comments"
			raise requests.RequestException(msg) from e

	async def retrieve_profile_details(
		self, username: str, category: str
	) -> dict[str, int | dict]:
		"""Returns profile details for a user.

		Args:
			username (str): Reddit username
			category (str): Category of profile data to retrieve (e.g. 'comment', 'posts')

		Returns:
			dict[str, int | dict]: Response containing status code and user data

		Raises:
			httpx.RequestError: If the request to Reddit API fails
		"""
		try:
			url = self.domain.format("oauth") + f"/user/{username}/{category}"
			async with httpx.AsyncClient() as client:
				res = await client.get(url, headers=self.headers, timeout=30)
				return {"status_code": res.status_code, "json": res.json()}
		except httpx.RequestError as e:
			msg = "Failed to retrieve about details"
			raise httpx.RequestError(msg) from e

	async def retrieve_subreddits(self) -> dict[str, int | dict]:
		"""Returns list of subreddits the user is subscribed to.

		Returns:
			dict[str, int | dict]: Response containing status code and subreddit data

		Raises:
			httpx.RequestError: If the request to Reddit API fails
		"""
		try:
			url = self.domain.format("oauth") + "/subreddits/mine/subscriber"
			async with httpx.AsyncClient() as client:
				res = await client.get(url, headers=self.headers, timeout=30)
				return {"status_code": res.status_code, "json": res.json()}
		except httpx.RequestError as e:
			msg = "Failed to retrieve subreddits"
			raise httpx.RequestError(msg) from e

	def submit_post(self, data: dict) -> dict[str, int | dict]:
		"""Submits a new post to Reddit.

		Args:
			data (dict): Post data including title, subreddit, kind, etc.

		Returns:
			dict[str, int | dict]: Response containing status code and submission result

		Raises:
			requests.RequestException: If the request to Reddit API fails
		"""
		try:
			url = self.domain.format("oauth") + "/api/submit"
			res = requests.post(url, headers=self.headers, data=data, timeout=30)
			return {"status_code": res.status_code, "json": res.json()}
		except requests.RequestException as e:
			msg = "Failed to submit post"
			raise requests.RequestException(msg) from e


class AWSClient:
	"""Base class for AWS Secrets Manager service."""

	def __init__(self):
		"""Initialises boto3 sdk session client for Secrets Manager."""
		session = boto3.Session()
		self.client = session.client(service_name="secretsmanager")

	def create_secret(self, name: str, secret_string: str) -> dict:
		"""Creates a new secret in AWS Secrets Manager.

		Args:
			name (str): Name identifier for the secret
			secret_string (str): The secret value to store

		Returns:
			dict: Response containing status and result data

		Raises:
			ClientError: If an AWS service error occurs (except ResourceExistsException)
		"""
		try:
			res = self.client.create_secret(Name=name, SecretString=secret_string)
		except ClientError as e:
			# Update secret if it already exists
			if e.response["Error"]["Code"] == "ResourceExistsException":
				return self.update_secret(secret_id=name, secret_string=secret_string)
		else:
			return {"status": "success", "json": res}

	def get_secret(self, secret_id: str) -> dict:
		"""Retrieves secret value from AWS Secrets Manager.

		Args:
			secret_id (str): Identifier for the secret to retrieve

		Returns:
			dict: Response containing status and retrieved secret value or error message

		Raises:
			ClientError: If an AWS service error occurs
		"""
		get_secret_value_response = self.client.get_secret_value(SecretId=secret_id)

		if "SecretString" not in get_secret_value_response:
			return {"status": "error", "message": "Secret string not in response"}

		return {
			"status": "success",
			"secret_value": get_secret_value_response["SecretString"],
		}

	def update_secret(self, secret_id: str, secret_string: str) -> dict:
		"""Updates an existing secret value in AWS Secrets Manager.

		Args:
			secret_id (str): Identifier for the secret to update
			secret_string (str): The new secret value

		Returns:
			dict: Response from AWS Secrets Manager API

		Raises:
			ClientError: If an AWS service error occurs
		"""
		try:
			return self.client.update_secret(
				SecretId=secret_id, SecretString=secret_string
			)
		except ClientError as e:
			msg = "Failed to update secret"
			raise ClientError(msg) from e

	def delete_secret(self, secret_id: str) -> dict:
		"""Deletes a secret from AWS Secrets Manager with recovery window.

		Args:
			secret_id (str): Identifier for the secret to delete

		Returns:
			dict: Response containing status and result data

		Raises:
			ClientError: If an AWS service error occurs
		"""
		try:
			res = self.client.delete_secret(
				SecretId=secret_id,
				RecoveryWindowInDays=7,
				ForceDeleteWithoutRecovery=False,
			)
		except ClientError as e:
			msg = "Failed to delete secret"
			raise ClientError(msg) from e
		else:
			return {"status": "success", "json": res}
