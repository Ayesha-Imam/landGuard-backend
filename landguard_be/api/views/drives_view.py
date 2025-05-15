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
            "capacity", "organizerName", "createdAt", "participants"
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
            "participants": data["participants"],
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
    
    
class JoinDriveView(APIView):
    authentication_classes = [MongoJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, driveId):
        user = request.user
        drive_collection = get_mongo_collection("drives")

        # Check if the drive exists
        drive = drive_collection.find_one({"_id": ObjectId(driveId)})
        if not drive:
            return Response(
                {"error": "Drive not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if user is already a participant
        if "participants" in drive and user.email in drive["participants"]:
            return Response(
                {"error": "User already joined this drive"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Add user email to participants array
        drive_collection.update_one(
            {"_id": ObjectId(driveId)},
            {"$addToSet": {"participants": user.email}}  # Ensures no duplicates
        )

        return Response(
            {"message": "Successfully joined the drive"},
            status=status.HTTP_200_OK
        )
    
class DeleteDriveView(APIView):
    authentication_classes = [MongoJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, driveId):
        user = request.user
        drive_collection = get_mongo_collection("drives")

        # Validate driveId format
        if not ObjectId.is_valid(driveId):
            return Response(
                {"detail": "Invalid drive ID format"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find the drive and verify ownership
        drive = drive_collection.find_one({"_id": ObjectId(driveId)})
        if not drive:
            return Response(
                {"detail": "Drive not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if drive.get("user_id") != str(user._id):
            return Response(
                {"detail": "You are not authorized to delete this drive"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Delete the drive
        drive_collection.delete_one({"_id": ObjectId(driveId)})

        return Response(
            {"detail": "Drive deleted successfully"},
            status=status.HTTP_200_OK
        )