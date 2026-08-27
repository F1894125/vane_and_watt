import jwt
from datetime import datetime, timedelta, timezone
from decouple import config
from rest_framework.exceptions import AuthenticationFailed


def create_token(user_id: int, type: str):
    """
    Create JWT Access or Refresh Token with user_id.

    Args:
        user_id (int): User ID
        type (str): Token type ('a' for access, 'r' for refresh)

    Returns:
        str: JWT Access or Refresh Token

    Raises:
        AuthenticationFailed: If token type is invalid
            or secret key is unavailable.
    """
    token_types = {
        'a': config('ACCESS_TOKEN_VALIDITY', cast=int),
        'r': config('REFRESH_TOKEN_VALIDITY', cast=int),
    }
    if type not in token_types:
        raise AuthenticationFailed(
            f"Invalid token type - '{type}'."
        )

    validity = token_types[type]
    if validity is not None:
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": user_id,
            "iat": now.timestamp(),
            "exp": (
                int((now + timedelta(minutes=validity)).timestamp())
                if type == 'a'
                else int((now + timedelta(days=validity)).timestamp())
            )
        }
    else:
        raise AuthenticationFailed(
            f'{"Access" if type == "a" else "Refresh"} token validity not set.'
        )

    secret_key = config('SECRET_KEY')
    if not secret_key:
        raise AuthenticationFailed(
            "SECRET_KEY unavailable in environment variables."
        )

    token = jwt.encode(
        payload, secret_key, algorithm="HS256"
    )

    return token

def decode_token(token: str, type: str):
    """
    Decode JWT Access Token and return user_id.
    
    Args:
        token (str): JWT Access Token
        type (str): Token type ('a' for access, 'r' for refresh)

    Returns:
        int: User ID
    
    Raises:
        AuthenticationFailed: If token type is invalid,
            secret key is unavailable, token is expired,
            or token is invalid.
        jwt.ExpiredSignatureError: If token has expired.
        jwt.InvalidTokenError: If token is invalid.
    """
    token_types = {'a', 'r'}
    if type not in token_types:
        raise AuthenticationFailed(
            f"Invalid token type - '{type}'."
        )
    
    secret_key = config('SECRET_KEY')
    if not secret_key:
        raise AuthenticationFailed(
            "SECRET_KEY unavailable in environment variables."
        )

    try:
        payload = jwt.decode(
            token, secret_key, algorithms=["HS256"]
        )
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError(
            f"{"Access" if type == 'a' else "Refresh"} token has expired."
        )
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError(
            f"{"Access" if type == 'a' else "Refresh"} token is invalid."
        )