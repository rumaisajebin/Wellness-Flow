from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

@database_sync_to_async
def get_user(token):
    from django.contrib.auth.models import AnonymousUser
    try:
        from account.models import CustomUser
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload['user_id']
        user = CustomUser.objects.get(id=user_id)
        print(f"User retrieved: {user}")  # Log the user
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        print("Invalid or expired token")
        return AnonymousUser()
    except CustomUser.DoesNotExist:
        print("User does not exist")
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Retrieve token from query parameters
        token = scope['query_string'].decode().split('token=')[-1] if 'token=' in scope['query_string'].decode() else None
        
        if token:
            print("Token found:", token)  # Log the token
            
            # Assuming you have a function to validate and retrieve the user
            scope['user'] = await get_user(token)
            if scope['user'] is None:
                scope['user'] = AnonymousUser()
                print("User not found from token, set to AnonymousUser.")
            else:
                print("User authenticated:", scope['user'])
        else:
            print("No token found, setting user to AnonymousUser.")
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)