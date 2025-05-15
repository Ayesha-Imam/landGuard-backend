from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from bson import ObjectId
from ..utils.db_utils import get_mongo_collection
from ..authentication import MongoJWTAuthentication

class CreateDriveView(APIView):
    authentication_classes = [MongoJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        required_fields = [
            "title", "location", "dateTime", "description",
            "capacity", "organizerName", "createdAt"
        ]

        for field in required_fields:
            if field not in data:
                return Response({"detail": f"Missing field: {field}"}, status=status.HTTP_400_BAD_REQUEST)

        drive_collection = get_mongo_collection("drives")

        drive_data = {
            "title": data["title"],
            "location": data["location"],
            "dateTime": data["dateTime"],
            "description": data["description"],
            "capacity": int(data["capacity"]),
            "organizerName": data["organizerName"],
            "status": "pending",
            "participants": 0,
            "createdAt": data["createdAt"],
            "user_id": str(user._id),
        }

        drive_collection.insert_one(drive_data)
        return Response({"detail": "Drive created successfully."}, status=status.HTTP_201_CREATED)


class AllDrivesView(APIView):
    def get(self, request):
        drive_collection = get_mongo_collection("drives")
        drives = list(drive_collection.find({}))
        
        # Convert ObjectId to string for each document
        for drive in drives:
            drive['_id'] = str(drive['_id'])
            
        return Response(drives, status=status.HTTP_200_OK)


class UserDrivesView(APIView):
    authentication_classes = [MongoJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        drive_collection = get_mongo_collection("drives")
        user_drives = list(drive_collection.find({"user_id": str(user._id)}, {"_id": 0}))
        return Response(user_drives, status=status.HTTP_200_OK)