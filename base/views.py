from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from base.models import User
from base.utils import get_object_or_none
from django.contrib.auth.hashers import make_password


class AuthTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['is_admin'] = user.is_staff
        # ...
        print("Token Updated")

        return token


class LoginUserView(TokenObtainPairView):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data.get('refresh')

        # Custom response data
        response_data = {
            'access_token': response.data.get('access'),
        }
        
        response = Response(response_data)
        
        # Set the refresh token as an HTTP cookie
        response.set_cookie(
            key='jwt',
            value=refresh_token,
            httponly=True,
            secure=True,    # Enable this if using HTTPS
            samesite=None,
            max_age=(60 * 15)
        )
        
        return response
    

class LoginRefreshView(APIView):
    def get(self, request):
        # Retrieve the refresh token from the HTTP cookie
        refresh_token = request.COOKIES.get('jwt')

        # If the refresh token is not present, return a 400 Bad Request response
        if not refresh_token:
            return Response({'error': 'Refresh token not provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create a RefreshToken instance from the refresh token
            token = RefreshToken(refresh_token)

            # Verify the refresh token
            token.verify()

            # Generate a new access token
            access_token = token.access_token

            # Return the new access token in the response
            return Response({'access_token': str(access_token)})

        except Exception as e:
            # Handle any potential exceptions (e.g., token expiration, invalid signature, etc.)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def register(request):
    email = request.data.pop("email", None)
    phone_number = request.data.pop("phone", None)
    password = request.data.pop("pwd", None)
    first_name = request.data.pop("firstName", None)
    last_name = request.data.pop("lastName", None)

    if not email or not password or not first_name:
        return Response({ "message": "Email, password and first name are required." }, status=status.HTTP_400_BAD_REQUEST)
    
    user = get_object_or_none(User, email=email)
    if user:
        return Response({ "message": "User already exists" }, status=status.HTTP_409_CONFLICT)

    try:
        hashed_password = make_password(password)
        User.objects.create(email=email, 
                            password=hashed_password,
                            phone_number=phone_number, 
                            first_name=first_name,
                            last_name=last_name)
        return Response({ "success": f"New user {email} created!" }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({ "error": str(e) }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class CustomTokenView(APIView):
#     def post(self, request, *args, **kwargs):
#         # Your authentication logic here
#         # Assuming you have obtained the user and access/refresh tokens
        
#         refresh_token = RefreshToken.for_user(user)
#         access_token = refresh_token.access_token
        
#         response_data = {
#             'access_token': str(access_token),
#         }
        
#         response = Response(response_data)
        
#         # Set the refresh token as an HTTP cookie
#         response.set_cookie(
#             key='refresh_token',
#             value=str(refresh_token),
#             httponly=True,
#             secure=True  # Enable this if using HTTPS
#         )
        
#         return response