from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
import jwt
from functools import wraps

def authorize(fn):

    @wraps(fn)
    def wrapper(request, *args, **kwargs):
        try:
            token = ""
            if "Authorization" in request.headers:
                token = request.headers["Authorization"].split(" ")[1]
 
            # Verify the JWT token
            decoded_token = jwt.decode(
                token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token.get("user_id", "")
            request.user_id = user_id
            print("TOKEN AUTHORIZED")

            response = fn(request, *args, **kwargs)
            
            return response

        except jwt.ExpiredSignatureError:
            return Response({"message": "Token is expired"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"message": "Token is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    
    return wrapper