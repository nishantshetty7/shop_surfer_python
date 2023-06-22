from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class AuthTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.user_name
        # ...
        print("Token Updated")

        return token


class CustomAuthTokenView(TokenObtainPairView):
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
            max_age=(60 * 30)
        )
        
        return response
    

class CustomRefreshTokenView(APIView):
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