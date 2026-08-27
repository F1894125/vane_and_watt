# import jwt
# from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
# from rest_framework.exceptions import AuthenticationFailed

from .authentication import JWTAuthentication
# from .tokens import create_token, decode_token


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to attach the authenticated
    user to the request.
    
    Necessary for templates that access
    user attributes.
    """
    def process_request(self, request):
        # Only attempt JWT auth if user is not already authenticated
        # This preserves Django's session-based auth for admin panel
        if request.user.is_authenticated:
            return
        
        auth = JWTAuthentication()
        result = auth.authenticate(request)
        
        if result:
            request.user, _ = result
        else:
            request.user = AnonymousUser()

    def process_response(self, request, response):
        new_access_token = getattr(request, '_new_access_token', None)

        if new_access_token:
            response.set_cookie(
                key='access_token',
                value=new_access_token,
                httponly=True,
                samesite='Lax'
            )

        return response


# ============================================================

# The middleware will authenticate a user on every request
# even if they're already authenticated to inject the user
# in the cookies, that's because the requests are stateless
# and have no memory of the user in subsequent requests.
# There's no other way to attach the user to the request.
# Middleware is the best place to do it because it intercepts
# every single request and response.

# Monkey-patching is the only way to attach the new access
# token to the request object as request.COOKIES is read-only,
# so the existing token can't be overriden

# Moreover, attributes of a response object are completely
# separate from the request which means that cookies in a
# request object aren't automatically added to the response
# object, it has to be done manually. That's why
# process_response is needed to pick up the new access token
# from the request object and attach it to the response object.

# There's a better way to implement the requirement satisfied
# by the middleware below, that's by using a custom authentication
# class. The existing middleware runs on every request, even if
# the request doesn't need authentication. It's also not integrated
# with the DRF's permission system and is non-standard.

# User = get_user_model()

# class JWTAuthenticationMiddleware(MiddlewareMixin):
#     """Middleware to attach the authenticated user to the request."""
#     def process_request(self, request):
#         access_token = request.COOKIES.get("access_token")

#         if not access_token:
#             request.user = AnonymousUser()
#             return

#         try:
#             user_id = decode_token(access_token, 'a')
#             user = User.objects.get(id=user_id)
#             request.user = user

#         except jwt.ExpiredSignatureError:
#             refresh_token = request.COOKIES.get("refresh_token")
#             # In case the access token is expired
#             # use the refresh token to get the user
#             # and create a new access token that
#             # will be attached to the current request
#             # and in the browser cookies

#             if not refresh_token:
#                 request.user = AnonymousUser()
#                 return
            
#             try:
#                 user_id = decode_token(refresh_token, 'r')
#                 new_access_token = create_token(user_id, 'a')

#                 # Updating the current request with the new access token
#                 request.COOKIES['access_token'] = new_access_token

#                 # Monkey-patching the current request with
#                 # the new access token so that process_response
#                 # can attach it to the browser cookies
#                 request._new_access_token = new_access_token

#                 user = User.objects.get(id=user_id)
#                 request.user = user

#             except (
#                 jwt.ExpiredSignatureError,
#                 jwt.InvalidTokenError,
#                 User.DoesNotExist,
#                 KeyError,
#             ):
#                 request.user = AnonymousUser()
        
#         except (
#             AuthenticationFailed,
#             jwt.InvalidTokenError,
#             User.DoesNotExist,
#             KeyError,
#         ):
#             request.user = AnonymousUser()

#     def process_response(self, request, response):
#         new_access_token = getattr(request, '_new_access_token', None)

#         if new_access_token:
#             response.set_cookie(
#                 key='access_token',
#                 value=new_access_token,
#                 httponly=True,
#                 samesite='Lax'
#             )

#         return response