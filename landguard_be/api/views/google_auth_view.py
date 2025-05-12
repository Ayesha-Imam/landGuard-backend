from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import jwt  # Your own JWT handling
from django.conf import settings
from bson import ObjectId

from ..utils.db_utils import get_mongo_collection

class GoogleAuthView(APIView):
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 🔍 Verify token with Google
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), audience=None)

            # Extract user info
            email = idinfo["email"]
            name = idinfo.get("name")
            # picture = idinfo.get("picture")

        except ValueError:
            return Response({"error": "Invalid Google token"}, status=status.HTTP_401_UNAUTHORIZED)

        # 🔐 Check if user exists in MongoDB
        user_collection = get_mongo_collection(collection_name="users")
        user = user_collection.find_one({"email": email})

        if not user:
            # 📌 Auto-signup: create new user
            user_data = {
                "email": email,
                "username": name,
                # "avatar": picture
            }
            result = user_collection.insert_one(user_data)
            user_data["_id"] = result.inserted_id
        else:
            user_data = user

        # ✅ Issue your own JWT for the app
        payload = {
            "user_id": str(user_data["_id"]),
            "email": user_data["email"]
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return Response({"token": token, "user": {
            "email": user_data["email"],
            "username": user_data.get("username")
            # "avatar": user_data.get("avatar")
        }})