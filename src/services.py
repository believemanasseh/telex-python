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
        """Initializes request headers for Reddit API authentication."""
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
        """Add access token to authorization header.

        Args:
            token (str): OAuth access token for Reddit API
        """
        self.headers["Authorization"] = f"Bearer {token}"

    def generate_access_token(self, code: str) -> dict[str, int | dict] | None:
        """Generates access token from authorization code.

        Args:
            code (str): Authorization code from Reddit OAuth flow

        Returns:
            dict[str, int | dict] | None: Response containing status code and token data

        Raises:
            requests.RequestException: If the request to Reddit API fails
        """
        url = self.domain.format("www") + "/api/v1/access_token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "https://ab67-169-159-83-94.ngrok-free.app",
        }

        try:
            res = requests.post(url, data=data, headers=self.headers, timeout=30)
        except requests.RequestException:
            raise

        return {"status_code": res.status_code, "json": res.json()}

    def retrieve_listings(self, category: str) -> dict[str, int | dict] | None:
        """Returns posts from specified category.

        Args:
            category (str): Category of listings to retrieve (e.g., 'new', 'hot', 'rising')

        Returns:
            dict[str, int | dict] | None: Response containing status code and listing data

        Raises:
            requests.RequestException: If the request to Reddit API fails
        """
        url = self.domain.format("oauth") + f"/{category}"
        try:
            res = requests.get(url, headers=self.headers, timeout=30)
        except requests.RequestException:
            raise
        return {"status_code": res.status_code, "json": res.json()}

    def retrieve_comments(self, post_id: str) -> dict[str, int | dict] | None:
        """Returns all comments for post.

        Args:
            post_id (str): Post ID

        Returns:
            dict[str, int | dict] | None: Post data dictionary or None if not found

        Raises:
            requests.RequestException: If the request fails
        """
        url = self.domain.format("oauth") + f"/comments/{post_id}"
        try:
            res = requests.get(url, headers=self.headers, timeout=30)
        except requests.RequestException:
            raise
        return {"status_code": res.status_code, "json": res.json()}


class AWSClient:
    """Base class for AWS Secrets Manager service."""

    def __init__(self):
        """Initializes boto3 sdk session client for Secrets Manager."""
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
        except ClientError:
            raise

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
        except ClientError:
            raise
        return {"status": "success", "json": res}
