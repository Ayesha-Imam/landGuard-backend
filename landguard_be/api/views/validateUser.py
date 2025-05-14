from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ValidateUserView(APIView):
    permission_classes = [IsAuthenticated]  # Will trigger your MongoJWTAuthentication

    def get(self, request):
        user = request.user  # This comes from MongoJWTAuthentication

        return Response({
            "valid": True,
            "user": {
                # "id": str(user["_id"]),
                "email": user["email"],
                "username": user["username"],
                "userType": user["userType"]
            }
        })


# from bson import ObjectId
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework_simplejwt.tokens import AccessToken
# from ..utils.db_utils import get_mongo_collection

# class ValidateUserView(APIView):
#     def get(self, request):
#         auth_header = request.headers.get("Authorization")
#         if not auth_header or not auth_header.startswith("Bearer "):
#             return Response({"error": "Authorization header missing"}, status=status.HTTP_401_UNAUTHORIZED)

#         token_str = auth_header.split(" ")[1]

#         try:
#             token = AccessToken(token_str)
#             user_id = token.get("user_id")

#             users_collection = get_mongo_collection("users")
#             user = users_collection.find_one({"_id": ObjectId(user_id)})  # Again, maybe use ObjectId(user_id)

#             if not user:
#                 return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

#             return Response({
#                 "valid": True,
#                 "user": {
#                     "id": str(user["_id"]),
#                     "email": user["email"],
#                     "username": user["username"]
#                 }
#             })

#         except Exception as e:
#             return Response({"error": "Invalid or expired token", "details": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
