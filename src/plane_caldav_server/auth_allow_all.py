"""
Custom authentication module that allows all requests.
"""

from radicale.auth import BaseAuth


class Auth(BaseAuth):
    """Authentication that accepts any credentials."""

    def login(self, login, password):
        """Always return the login username."""
        # Return the username to authenticate successfully
        # If login is empty, use a default user
        return login if login else "anonymous"
