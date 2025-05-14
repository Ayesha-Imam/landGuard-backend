from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson.objectid import ObjectId
from ..utils.db_utils import get_mongo_collection
from ..serializers.signUp import SignupSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_data = serializer.validated_data
        email = user_data['email']
        username = user_data['username']
        password = make_password(user_data['password'])

        users_collection = get_mongo_collection("users")

        # Check if email or username already exists
        if users_collection.find_one({"email": email}):
            return Response({"email": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        if users_collection.find_one({"username": username}):
            return Response({"username": "A user with this username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create user document
        user_doc = {
            "email": email,
            "username": username,
            "password": password,
        }

        inserted = users_collection.insert_one(user_doc)
        user_id = str(inserted.inserted_id)

        # Generate token manually
        refresh = RefreshToken()
        refresh["user_id"] = user_id
        refresh["email"] = email

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                # "id": user_id,
                "email": email,
                "username": username
            }
        }, status=status.HTTP_201_CREATED)
