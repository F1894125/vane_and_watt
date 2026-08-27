import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

from .tokens import create_token, decode_token


User = get_user_model()

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")
        
        if not access_token:
            return None
        
        try:
            user_id = decode_token(access_token, 'a')
            user = User.objects.get(id=user_id)
            return (user, None)
            
        except jwt.ExpiredSignatureError:
            refresh_token = request.COOKIES.get("refresh_token")
            if not refresh_token:
                raise AuthenticationFailed(
                    "Access token expired and no refresh token available."
                )

            try:
                user_id = decode_token(refresh_token, 'r')
                user = User.objects.get(id=user_id)

                new_access_token = create_token(user.id, 'a')
                request._new_access_token = new_access_token

                return (user, None)
            
            except Exception as e:
                raise AuthenticationFailed(str(e)) from e
                # Using 'from e' sets the original exception as __cause__
                # of the new exception, which is visible in the traceback

        except Exception as e:
            raise AuthenticationFailed(str(e)) from e