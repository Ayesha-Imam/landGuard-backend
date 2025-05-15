from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from bson import ObjectId
import os

from ..utils.db_utils import get_mongo_collection

class GoogleAuthView(APIView):
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify token with Google (specify your CLIENT_ID)
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_OAUTH2_CLIENT_ID  # Add this to your settings
            )

            # Validate token audience
            if idinfo['aud'] != settings.GOOGLE_OAUTH2_CLIENT_ID:
                raise ValueError("Invalid audience")

            email = idinfo["email"]
            name = idinfo.get("name", email.split('@')[0])
            picture = idinfo.get("picture")

        except ValueError as e:
            return Response({"error": f"Invalid Google token: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)

        # Get or create user
        user_collection = get_mongo_collection("users")
        user = user_collection.find_one({"email": email})

        if not user:
            # Create new user
            user_data = {
                "email": email,
                "username": name,
                "userType": "user",
                "avatar": picture,
                "isVerified": True  # Google-authenticated users are verified
            }
            result = user_collection.insert_one(user_data)
            user_id = result.inserted_id
        else:
            user_id = user["_id"]
            # Update existing user if needed
            user_collection.update_one(
                {"_id": user_id},
                {"$set": {
                    "username": name,
                    "avatar": picture
                }}
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user_id)  # Works with custom user model
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            "access": access_token,
            "refresh": refresh_token,
            "user": {
                "id": str(user_id),
                "email": email,
                "username": name,
                "userType": "user",
                "avatar": picture
            }
        }, status=status.HTTP_200_OK)


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from google.oauth2 import id_token
# from google.auth.transport import requests as google_requests
# import jwt  # Your own JWT handling
# from django.conf import settings
# from bson import ObjectId

# from ..utils.db_utils import get_mongo_collection

# class GoogleAuthView(APIView):
#     def post(self, request):
#         token = request.data.get("token")
#         if not token:
#             return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # 🔍 Verify token with Google
#             idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), audience=None)

#             # Extract user info
#             email = idinfo["email"]
#             name = idinfo.get("name")
#             # picture = idinfo.get("picture")

#         except ValueError:
#             return Response({"error": "Invalid Google token"}, status=status.HTTP_401_UNAUTHORIZED)

#         # 🔐 Check if user exists in MongoDB
#         user_collection = get_mongo_collection(collection_name="users")
#         user = user_collection.find_one({"email": email})

#         if not user:
#             # 📌 Auto-signup: create new user
#             user_data = {
#                 "email": email,
#                 "username": name,
#                 "userType": "user"
#                 # "avatar": picture
#             }
#             result = user_collection.insert_one(user_data)
#             user_data["_id"] = result.inserted_id
#         else:
#             user_data = user

#         # ✅ Issue your own JWT for the app
#         payload = {
#             "user_id": str(user_data["_id"]),
#             "email": user_data["email"]
#         }
#         token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

#         return Response({"token": token, "user": {
#             "email": user_data["email"],
#             "username": user_data.get("username"),
#             "userType": user_data.get("userType")
#             # "avatar": user_data.get("avatar")
#         }})