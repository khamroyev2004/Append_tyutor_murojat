from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async

@database_sync_to_async
def get_user_from_token(token):
    try:
        from django.contrib.auth.models import AnonymousUser
        from rest_framework_simplejwt.authentication import JWTAuthentication

        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        return jwt_auth.get_user(validated_token)
    except Exception as e:
        print("🔴 JWT WS AUTH ERROR:", e)
        from django.contrib.auth.models import AnonymousUser
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        print("🟡 WS JWT MIDDLEWARE CALLED")

        query_string = scope.get("query_string", b"").decode()
        print("🟡 WS QUERY:", query_string)

        params = parse_qs(query_string)
        token = params.get("token", [None])[0]

        if token:
            print("🟢 WS TOKEN FOUND")
            scope["user"] = await get_user_from_token(token)
            print("🟢 WS USER:", scope["user"])
        else:
            print("🔴 WS TOKEN NOT FOUND")
            from django.contrib.auth.models import AnonymousUser
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
