"""
Utility functions for authentication and password management.
"""

import os
from passlib.hash import apr_md5_crypt


def generate_htpasswd_file(filepath: str, username: str, password: str) -> None:
    """
    Generate an htpasswd file with the given username and password.

    Args:
        filepath: Path to the htpasswd file to create/update
        username: Username for authentication
        password: Password for authentication (will be hashed with apr_md5_crypt)
    """
    # Generate the password hash using apr_md5_crypt (Apache MD5)
    password_hash = apr_md5_crypt.hash(password)

    # Write to htpasswd file in the format: username:hash
    with open(filepath, "w") as f:
        f.write(f"{username}:{password_hash}\n")


def get_credentials_from_env() -> tuple[str, str]:
    """
    Get username and password from environment variables.

    Returns:
        tuple: (username, password)

    Raises:
        ValueError: If required environment variables are missing
    """
    username = os.environ.get("USER")
    password = os.environ.get("PASSWORD")

    if not username:
        raise ValueError("USER environment variable is required")

    if not password:
        raise ValueError("PASSWORD environment variable is required")

    return username, password
