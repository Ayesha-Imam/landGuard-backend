from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from ..serializers.login import LoginSerializer

from ..utils.db_utils import get_mongo_collection

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        users_collection = get_mongo_collection("users")
        user = users_collection.find_one({"email": email})

        if not user:
            return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, user["password"]):
            return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

        # JWT Token Generation
        refresh = RefreshToken()
        refresh["user_id"] = str(user["_id"])
        refresh["email"] = user["email"]

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                # "id": str(user["_id"]),
                "email": user["email"],
                "username": user["username"],
                "userType": user["userType"]
            }
        }, status=status.HTTP_200_OK)