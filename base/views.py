from django.conf import settings
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

from base.serializers import AuthTokenSerializer
import jwt
from base.emailer import send_verification_email


class LoginUserView(TokenObtainPairView):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get("email", None)

        user = get_object_or_none(User, email=email)

        if user and user.auth_type == "google":
            return Response({"message": """It looks like you've previously registered using social authentication. Please use the same social authentication method (Google) to log in."""}, status=status.HTTP_403_FORBIDDEN)

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
            max_age=(60 * 60 * 24)
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
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


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
        if not user.is_active:
            return Response({ "message": "You have already registered but need to verify your account. Please check your mail or resend verification email", "resend": True},
                             status=status.HTTP_409_CONFLICT)
        
        return Response({ "message": "Email ID Taken" }, status=status.HTTP_409_CONFLICT)

    try:
        hashed_password = make_password(password)
        new_user = User.objects.create(email=email, 
                            password=hashed_password,
                            phone_number=phone_number, 
                            first_name=first_name,
                            last_name=last_name)
        
        result = send_verification_email(new_user)
        if result:
            return Response({ "message": "We have sent you an email. Please click on the verification link to activate your account." },
                         status=status.HTTP_201_CREATED)
        
        return Response({ "message": "Email not sent" }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({ "message": str(e) }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def google_login(request):
    request_data = request.data
    email = request_data.get("email", None)
    first_name = request_data.get("given_name", None)
    last_name = request_data.get("family_name", None)
    image = request_data.get("picture", "")

    if not email:
        return Response({ "message": "Email is required." }, status=status.HTTP_400_BAD_REQUEST)
    
    user = get_object_or_none(User, email=email)
    if not user:
        try:
            hashed_password = make_password(f"{email}_{first_name}")
            user = User.objects.create(email=email, 
                                       password=hashed_password,
                                        first_name=first_name,
                                        last_name=last_name,
                                        image=image,
                                        is_active=True,
                                        auth_type="google")
        except Exception as e:
            return Response({ "message": str(e) }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    serializer = AuthTokenSerializer()

    if user.auth_type == "regular":
        return Response({"message":"You have already registered with password authentication. Please contact support for any assistance."},status=status.HTTP_409_CONFLICT)

    tokens = serializer.validate({'email': user.email, 'password': f"{email}_{first_name}"})

    access_token = tokens['access']
    refresh_token = tokens['refresh']

    response = Response({"access_token": access_token}, status=status.HTTP_200_OK)
    
    # Set the refresh token as an HTTP cookie
    response.set_cookie(
        key='jwt',
        value=refresh_token,
        httponly=True,
        secure=True,    # Enable this if using HTTPS
        samesite=None,
        max_age=(60 * 60 * 24)
    )
    
    return response
    
    
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def logout(request):

    # Retrieve the refresh token from the HTTP cookie
    refresh_token = request.COOKIES.get('jwt', None)

    # If the refresh token is not present, return a 400 Bad Request response
    if not refresh_token:
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    try:
        response = Response({"message": "Logged Out!"}, status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('jwt')
        return response
    except Exception as e:
        return Response({ "error": str(e) }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def verify_register(request):

    try:
        token = request.data.get("token", "")
        # Verify the JWT token
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        # # Extract the expiration time from the token payload
        # expiration_time = datetime.datetime.fromtimestamp(decoded_token['exp'])

        # # Check if the token has expired
        # current_time = datetime.datetime.now()
        # if current_time > expiration_time:
        #     return Response({"message":"Registration link expired"}, status=status.HTTP_401_UNAUTHORIZED)
        # else:
        user_obj = get_object_or_none(User, email=decoded_token["email"])
        if user_obj:
            if not user_obj.is_active:
                user_obj.is_active = True
                user_obj.save()
            else:
                return Response({"message":f"Hello {user_obj.first_name}! Your account is already activated"}, status=status.HTTP_409_CONFLICT)
        else:
            return Response({"message":"User Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"message":f"Hello {user_obj.first_name}! Your account is activated"}, status=status.HTTP_200_OK)
        
    except jwt.ExpiredSignatureError:
        return Response({"message":"Registration link expired"}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({"message":"Registration link invalid"}, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def resend_register(request):

    email = request.data.get("email", None)

    user_obj = get_object_or_none(User, email=email)
    if user_obj:
        if user_obj.is_active:
            return Response({"message":"User Already Verified"}, status=status.HTTP_409_CONFLICT)
        
        result = send_verification_email(user_obj)
        if result:
            return Response({"message":"Verification Email Resent"}, status=status.HTTP_200_OK)
    else:
        return Response({"message":"User Not Found"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({"message":"Verification Email Not Sent"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

@api_view(['GET'])
def send_email(request):
    user_obj = get_object_or_none(User, email="nishantshetty92@gmail.com")
    if user_obj:
        result = send_verification_email(user_obj)
        if result:
            return Response({ "Email Sent" }, status=status.HTTP_200_OK)
    else:
        return Response({ "User Not Found" }, status=status.HTTP_404_NOT_FOUND)
    
    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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