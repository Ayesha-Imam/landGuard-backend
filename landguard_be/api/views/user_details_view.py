from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from bson.objectid import ObjectId
from ..utils.db_utils import get_mongo_collection
from ..authentication import MongoJWTAuthentication
from django.contrib.auth.hashers import check_password, make_password
from ..serializers.change_pass import ChangePasswordSerializer

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch current user"""
        user_id = request.user["_id"]
        collection = get_mongo_collection("users")
        user = collection.find_one({"_id": ObjectId(user_id)}, {"password": 0})
        if user:
            user["_id"] = str(user["_id"])
            return Response(user, status=status.HTTP_200_OK)
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class UserEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """Edit user profile"""
        user_id = request.user["_id"]
        data = request.data  # Only allow fields you expect
        allowed_fields = ["username", "email", "phone", "address"]
        update_fields = {key: value for key, value in data.items() if key in allowed_fields}

        if not update_fields:
            return Response({"error": "No valid fields to update"}, status=status.HTTP_400_BAD_REQUEST)

        collection = get_mongo_collection("users")
        result = collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_fields})

        if result.modified_count:
            return Response({"message": "Profile updated"}, status=status.HTTP_200_OK)
        return Response({"message": "No changes made"}, status=status.HTTP_200_OK)

class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        """Delete user account"""
        user_id = request.user["_id"]
        collection = get_mongo_collection("users")
        result = collection.delete_one({"_id": ObjectId(user_id)})

        if result.deleted_count:
            return Response({"message": "Account deleted"}, status=status.HTTP_200_OK)
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        # Get the user email from the token
        email = request.user["email"]  

        users_collection = get_mongo_collection("users")
        user = users_collection.find_one({"email": email})

        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if not check_password(old_password, user["password"]):
            return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        users_collection.update_one(
            {"email": email},
            {"$set": {"password": make_password(new_password)}}
        )

        return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
